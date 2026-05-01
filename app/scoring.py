"""Per-type scoring. Returns ratio in [0, 1]."""

import re
from typing import Any
from .questions import Question


_WS = re.compile(r"\s+")


def _norm_code(s: str) -> str:
    s = (s or "").strip().lower()
    s = s.replace("'", "\"")
    s = _WS.sub("", s)
    return s


def score(q: Question, payload: dict[str, Any]) -> float:
    if q.type == "single":
        return 1.0 if payload.get("choice") == q.correct else 0.0

    if q.type == "multi":
        chosen = set(payload.get("choices", []))
        correct = set(q.correct or [])
        if not correct:
            return 0.0
        # all-or-nothing: exact set match
        return 1.0 if chosen == correct else 0.0

    if q.type == "match":
        ans = payload.get("pairs", {}) or {}
        correct = q.correct or {}
        if not correct:
            return 0.0
        hit = sum(1 for k, v in correct.items() if ans.get(k) == v)
        return hit / len(correct)

    if q.type == "order":
        ans = payload.get("order", []) or []
        correct = q.correct or []
        if not correct or len(ans) != len(correct):
            return 0.0
        hit = sum(1 for i, x in enumerate(correct) if i < len(ans) and ans[i] == x)
        return hit / len(correct)

    if q.type == "bins":
        ans = payload.get("bins", {}) or {}
        correct = q.correct or {}
        total = sum(len(v) for v in correct.values()) or 1
        hit = 0
        for bin_id, items in correct.items():
            chosen = set(ans.get(bin_id, []))
            hit += len(set(items) & chosen)
        return hit / total

    if q.type == "code_fill":
        ans = payload.get("blanks", {}) or {}
        correct = q.correct or {}
        if not correct:
            return 0.0
        hit = 0
        for bid, variants in correct.items():
            user_norm = _norm_code(ans.get(bid, ""))
            ok = any(user_norm == _norm_code(v) for v in variants)
            if ok:
                hit += 1
        return hit / len(correct)

    if q.type == "sabotage":
        try:
            chosen = int(payload.get("line", -1))
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if chosen == q.correct else 0.0

    return 0.0
