# BET — Budget & Expense Tracker

A desktop app for setting a budget, recording expenses and viewing monthly summaries. Built with Python, Tkinter and SQLAlchemy (SQLite).

## Features

- Set and view a budget (₦)
- Add expenses with amount, category, description and date
- View all expenses with total spent and remaining budget
- Monthly summary grouped by category

## Requirements

- Python 3.10+
- Tkinter (included with Python on Windows and macOS)
- SQLAlchemy 2.0+

On Linux, install Tkinter separately if it is missing:

```bash
sudo apt install python3-tk
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python gui.py
```

The database file `bet.db` is created automatically next to the code on first run.

## Project structure

| File | Role |
|------|------|
| `gui.py` | Tkinter interface (`BudgetApp` class) and entry point |
| `logic.py` | Validation and rules; no tkinter, no SQL |
| `database.py` | SQLAlchemy models (`Budget`, `Expense`) and queries |

The layers only call downward: `gui` → `logic` → `database`.

## Usage notes

- Dates must be `YYYY-MM-DD` and the summary month `YYYY-MM`.
- Amounts must be positive, finite numbers.
- Only one budget is stored; setting a new one replaces it.
