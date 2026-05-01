import os
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = os.environ.get("DB_PATH", "/data/quiz.db")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    return Session(engine)
