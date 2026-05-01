import csv
import io
import os
import random
import secrets
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import select

from .db import engine, get_session, init_db
from .models import Answer, Attempt
from .questions import QUESTIONS, by_id
from .scoring import score as score_q

BASE = Path(__file__).resolve().parent

ADMIN_KEY = os.environ.get("ADMIN_KEY", "change-me")
QUIZ_DURATION_MIN = int(os.environ.get("QUIZ_DURATION_MIN", "60"))
QUESTIONS_PER_ATTEMPT = int(os.environ.get("QUESTIONS_PER_ATTEMPT", "12"))
ATTEMPT_COOKIE = "attempt_id"
COOKIE_SECRET = os.environ.get("COOKIE_SECRET", secrets.token_hex(16))

app = FastAPI(title="ML Practice 16 — PCA Quiz")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_attempt(request: Request) -> Attempt | None:
    raw = request.cookies.get(ATTEMPT_COOKIE)
    if not raw:
        return None
    try:
        aid = int(raw)
    except ValueError:
        return None
    with get_session() as s:
        return s.get(Attempt, aid)


def _is_expired(a: Attempt) -> bool:
    if a.finished_at:
        return True
    return datetime.utcnow() - a.started_at > timedelta(minutes=QUIZ_DURATION_MIN)


def _finish_attempt(a: Attempt) -> None:
    with get_session() as s:
        a = s.get(Attempt, a.id)
        if a.finished_at:
            return
        rows = s.exec(select(Answer).where(Answer.attempt_id == a.id)).all()
        a.score = sum(r.earned_points for r in rows)
        a.finished_at = datetime.utcnow()
        s.add(a)
        s.commit()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("start.html", {"request": request})


@app.post("/start")
def start(request: Request, name: str = Form(...)):
    name = (name or "").strip()
    if not name:
        return RedirectResponse("/", status_code=303)

    pool = [q.id for q in QUESTIONS]
    k = min(QUESTIONS_PER_ATTEMPT, len(pool))
    qids = random.sample(pool, k)

    with get_session() as s:
        a = Attempt(name=name, question_order=qids, cur_index=0)
        s.add(a)
        s.commit()
        s.refresh(a)

    resp = RedirectResponse(f"/q/0", status_code=303)
    resp.set_cookie(ATTEMPT_COOKIE, str(a.id), httponly=True, samesite="lax")
    return resp


@app.get("/q/{idx}", response_class=HTMLResponse)
def render_question(request: Request, idx: int):
    a = _get_attempt(request)
    if not a:
        return RedirectResponse("/", status_code=303)
    if _is_expired(a):
        _finish_attempt(a)
        return RedirectResponse("/finish", status_code=303)
    if idx >= len(a.question_order):
        return RedirectResponse("/finish", status_code=303)
    if idx != a.cur_index:
        return RedirectResponse(f"/q/{a.cur_index}", status_code=303)

    q = by_id(a.question_order[idx])

    with get_session() as s:
        a = s.get(Attempt, a.id)
        if a.cur_shown_at is None:
            a.cur_shown_at = datetime.utcnow()
            s.add(a)
            s.commit()
        s.refresh(a)

    deadline = a.started_at + timedelta(minutes=QUIZ_DURATION_MIN)
    secs_left = max(0, int((deadline - datetime.utcnow()).total_seconds()))

    return templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "q": q,
            "idx": idx,
            "total": len(a.question_order),
            "secs_left": secs_left,
            "speed_window": q.speed_window_s,
            "speed_bonus_pct": q.speed_bonus_pct,
        },
    )


def _parse_payload(q_type: str, form: dict) -> dict:
    if q_type == "single":
        return {"choice": form.get("choice")}
    if q_type == "multi":
        return {"choices": form.getlist("choices")}
    if q_type == "match":
        pairs = {}
        for k, v in form.items():
            if k.startswith("match_"):
                pairs[k[len("match_"):]] = v
        return {"pairs": pairs}
    if q_type == "order":
        raw = form.get("order", "")
        return {"order": [x for x in raw.split(",") if x]}
    if q_type == "bins":
        bins: dict[str, list[str]] = {}
        for k, v in form.items():
            if k.startswith("bin_") and v:
                bins[k[len("bin_"):]] = [x for x in v.split(",") if x]
        return {"bins": bins}
    if q_type == "code_fill":
        blanks = {}
        for k, v in form.items():
            if k.startswith("blank_"):
                blanks[k[len("blank_"):]] = v
        return {"blanks": blanks}
    if q_type == "sabotage":
        return {"line": form.get("line")}
    return {}


@app.post("/q/{idx}")
async def submit_question(request: Request, idx: int):
    a = _get_attempt(request)
    if not a:
        return RedirectResponse("/", status_code=303)
    if _is_expired(a):
        _finish_attempt(a)
        return RedirectResponse("/finish", status_code=303)
    if idx != a.cur_index:
        return RedirectResponse(f"/q/{a.cur_index}", status_code=303)

    qid = a.question_order[idx]
    q = by_id(qid)

    form = await request.form()
    # form is FormData (multidict); preserve getlist behaviour
    payload = _parse_payload(q.type, form)
    ratio = score_q(q, payload)

    elapsed = 0.0
    if a.cur_shown_at:
        elapsed = (datetime.utcnow() - a.cur_shown_at).total_seconds()
    speed_bonus = ratio > 0 and elapsed <= q.speed_window_s
    multiplier = 1 + (q.speed_bonus_pct / 100.0 if speed_bonus else 0)
    earned = round(q.points * ratio * multiplier, 2)

    with get_session() as s:
        ans = Answer(
            attempt_id=a.id,
            question_id=qid,
            payload=payload,
            correct_ratio=ratio,
            base_points=q.points,
            earned_points=earned,
            elapsed_s=elapsed,
            speed_bonus=speed_bonus,
        )
        s.add(ans)
        a2 = s.get(Attempt, a.id)
        a2.cur_index = idx + 1
        a2.cur_shown_at = None
        s.add(a2)
        s.commit()

    if idx + 1 >= len(a.question_order):
        _finish_attempt(a)
        return RedirectResponse("/finish", status_code=303)
    return RedirectResponse(f"/q/{idx + 1}", status_code=303)


@app.get("/finish", response_class=HTMLResponse)
def finish(request: Request):
    a = _get_attempt(request)
    if not a:
        return RedirectResponse("/", status_code=303)
    if not a.finished_at:
        _finish_attempt(a)
    with get_session() as s:
        a = s.get(Attempt, a.id)
        rows = s.exec(select(Answer).where(Answer.attempt_id == a.id)).all()
    return templates.TemplateResponse(
        "finish.html",
        {
            "request": request,
            "attempt": a,
            "answers": rows,
            "duration_str": _fmt_duration(_duration_s(a)),
        },
    )


def _duration_s(a: Attempt) -> int:
    if not (a.started_at and a.finished_at):
        return 10**9
    return int((a.finished_at - a.started_at).total_seconds())


def _fmt_duration(secs: int) -> str:
    if secs >= 10**9:
        return "—"
    return f"{secs // 60}:{secs % 60:02d}"


def _attempt_key(a: Attempt) -> tuple[float, int]:
    # Higher score first; faster time wins ties.
    return (-a.score, _duration_s(a))


@app.get("/leaderboard", response_class=HTMLResponse)
def leaderboard(request: Request):
    with get_session() as s:
        rows = s.exec(
            select(Attempt).where(Attempt.finished_at.is_not(None))
        ).all()

    best: dict[str, Attempt] = {}
    for r in rows:
        cur = best.get(r.name)
        if cur is None or _attempt_key(r) < _attempt_key(cur):
            best[r.name] = r

    board = sorted(best.values(), key=_attempt_key)
    board_view = [
        {
            "rank": i + 1,
            "name": a.name,
            "score": a.score,
            "duration_s": _duration_s(a),
            "duration_str": _fmt_duration(_duration_s(a)),
            "finished_at": a.finished_at,
        }
        for i, a in enumerate(board)
    ]

    return templates.TemplateResponse(
        "leaderboard.html",
        {"request": request, "board": board_view},
    )


@app.get("/admin", response_class=HTMLResponse)
def admin(request: Request, key: str = ""):
    if key != ADMIN_KEY:
        raise HTTPException(403, "Bad admin key")
    with get_session() as s:
        attempts = s.exec(select(Attempt).order_by(Attempt.score.desc())).all()
    rows_view = [
        {
            "id": a.id,
            "name": a.name,
            "started_at": a.started_at,
            "finished_at": a.finished_at,
            "score": a.score,
            "duration_str": _fmt_duration(_duration_s(a)) if a.finished_at else "в процессе",
        }
        for a in attempts
    ]
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "attempts": rows_view, "key": key},
    )


@app.get("/admin/export.csv")
def export_csv(key: str = ""):
    if key != ADMIN_KEY:
        raise HTTPException(403, "Bad admin key")

    with get_session() as s:
        attempts = s.exec(select(Attempt).order_by(Attempt.score.desc())).all()
        all_answers = s.exec(select(Answer)).all()

    by_attempt: dict[int, list[Answer]] = {}
    for ans in all_answers:
        by_attempt.setdefault(ans.attempt_id, []).append(ans)

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "attempt_id", "name", "started_at", "finished_at", "duration_s", "score",
        "question_id", "correct_ratio", "earned_points", "elapsed_s",
        "speed_bonus", "payload",
    ])
    for a in attempts:
        dur = _duration_s(a) if a.finished_at else ""
        rows = by_attempt.get(a.id, [])
        if not rows:
            w.writerow([a.id, a.name, a.started_at, a.finished_at, dur, a.score,
                        "", "", "", "", "", ""])
            continue
        for r in rows:
            w.writerow([
                a.id, a.name, a.started_at, a.finished_at, dur, a.score,
                r.question_id, r.correct_ratio, r.earned_points,
                round(r.elapsed_s, 2), r.speed_bonus, r.payload,
            ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=leaderboard.csv"},
    )


@app.get("/health")
def health():
    return {"ok": True}
