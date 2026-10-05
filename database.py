from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DB_PATH = Path(__file__).resolve().parent / "bet.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Budget(Base):
    __tablename__ = "budget"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float]


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float]
    category: Mapped[str]
    description: Mapped[str]
    date: Mapped[str]


@contextmanager
def session_scope():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    Base.metadata.create_all(engine)


def save_budget(amount):
    with session_scope() as s:
        s.merge(Budget(id=1, amount=amount))


def fetch_budget():
    """Returns the budget as a float, or None if not set."""
    with session_scope() as s:
        budget = s.get(Budget, 1)
        return budget.amount if budget else None


def insert_expense(amount, category, description, date):
    with session_scope() as s:
        s.add(Expense(amount=amount, category=category,
                      description=description, date=date))


def fetch_expenses():
    with session_scope() as s:
        stmt = select(Expense).order_by(Expense.date.desc(), Expense.id.desc())
        return s.scalars(stmt).all()


def fetch_total_spent():
    with session_scope() as s:
        return s.scalar(select(func.coalesce(func.sum(Expense.amount), 0)))


def fetch_month_summary(month):
    """month is 'YYYY-MM'. Returns rows with .category and .total, biggest first."""
    with session_scope() as s:
        total = func.sum(Expense.amount).label("total")
        stmt = (
            select(Expense.category, total)
            .where(Expense.date.like(f"{month}-%"))
            .group_by(Expense.category)
            .order_by(total.desc())
        )
        return s.execute(stmt).all()
