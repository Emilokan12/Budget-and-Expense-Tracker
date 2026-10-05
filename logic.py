import math
from datetime import datetime

import database

CATEGORIES = [
    "Food", "Transport", "Rent", "Utilities", "Healthcare",
    "Education", "Entertainment", "Clothing", "Savings", "Miscellaneous",
]
CATEGORY_PLACEHOLDER = "Select a category"


def start():
    database.init_db()


def _parse_amount(text, error):
    try:
        value = float(text)
    except ValueError:
        raise ValueError(error)
    if not math.isfinite(value):
        raise ValueError(error)
    return value


def set_budget(amount_text):
    amount_text = amount_text.strip()
    if not amount_text:
        raise ValueError("Enter a budget amount")
    error = "Enter a valid positive budget amount"
    value = _parse_amount(amount_text, error)
    if value < 0:
        raise ValueError(error)
    database.save_budget(value)
    return value


def get_budget():
    """Returns float or None."""
    return database.fetch_budget()


def add_expense(amount_text, category, desc, date):
    amount_text, desc, date = amount_text.strip(), desc.strip(), date.strip()

    if not all([amount_text, desc, date]) or category == CATEGORY_PLACEHOLDER:
        raise ValueError("All fields are required")

    error = "Enter a valid positive amount"
    amount = _parse_amount(amount_text, error)
    if amount <= 0:
        raise ValueError(error)

    try:
        date = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Enter a valid date in YYYY-MM-DD format")

    database.insert_expense(amount, category, desc, date)


def get_expenses_report():
    """Returns (rows, total_spent, remaining). remaining is None if no budget."""
    rows = database.fetch_expenses()
    total = database.fetch_total_spent()
    budget = database.fetch_budget()
    remaining = budget - total if budget is not None else None
    return rows, total, remaining


def get_monthly_summary(month):
    """Returns (rows, total) for a 'YYYY-MM' month."""
    month = month.strip()
    if not month:
        raise ValueError("Enter a month  e.g. 2025-11")
    try:
        month = datetime.strptime(month, "%Y-%m").strftime("%Y-%m")
    except ValueError:
        raise ValueError("Enter a valid month in YYYY-MM format")

    rows = database.fetch_month_summary(month)
    if not rows:
        raise LookupError(f"No expenses found for {month}")
    total = sum(r.total for r in rows)
    return rows, total
