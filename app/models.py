from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON


class Attempt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    finished_at: Optional[datetime] = None
    score: float = 0.0
    question_order: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    cur_index: int = 0
    cur_shown_at: Optional[datetime] = None


class Answer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    attempt_id: int = Field(foreign_key="attempt.id", index=True)
    question_id: str
    payload: dict = Field(default_factory=dict, sa_column=Column(JSON))
    correct_ratio: float = 0.0
    base_points: int = 0
    earned_points: float = 0.0
    elapsed_s: float = 0.0
    speed_bonus: bool = False
