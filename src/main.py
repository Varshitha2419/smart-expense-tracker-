import json
import uuid
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

EXPENSES_FILE = Path("expenses.json")

app = FastAPI(title="Smart Expense Tracker")


class ExpenseCreate(BaseModel):
    """Request body for creating a new expense."""

    title: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)
    date: date


class Expense(ExpenseCreate):
    """A stored expense with a server-generated unique identifier."""

    id: str


def _load_expenses() -> list[dict]:
    """Load expenses from the JSON file, returning an empty list on any read error."""
    if not EXPENSES_FILE.exists():
        return []
    try:
        with EXPENSES_FILE.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        return []


def _save_expenses(expenses: list[dict]) -> None:
    """Persist the full expense list to the JSON file."""
    with EXPENSES_FILE.open("w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2, ensure_ascii=False, default=str)


@app.post("/expenses", status_code=status.HTTP_201_CREATED, response_model=Expense)
def create_expense(expense: ExpenseCreate) -> Expense:
    """Create a new expense and assign it a UUID."""
    expenses = _load_expenses()
    new_expense = Expense(
        id=str(uuid.uuid4()),
        **expense.model_dump(),
    )
    expenses.append(new_expense.model_dump(mode="json"))
    _save_expenses(expenses)
    return new_expense


@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: Optional[str] = Query(default=None),
) -> list[Expense]:
    """Return all expenses, optionally filtered by category."""
    expenses = _load_expenses()
    if category is not None:
        expenses = [e for e in expenses if e.get("category") == category]
    return [Expense(**e) for e in expenses]


class CategorySummary(BaseModel):
    """Total spending for a single category."""

    category: str
    total: float


class ExpenseSummary(BaseModel):
    """Aggregated spending totals across all expenses."""

    total: float
    by_category: list[CategorySummary]


@app.get("/expenses/summary", response_model=ExpenseSummary)
def get_expenses_summary() -> ExpenseSummary:
    """Return overall and per-category spending totals."""
    expenses = _load_expenses()
    total = round(sum(e["amount"] for e in expenses), 2)

    category_totals: dict[str, float] = {}
    for expense in expenses:
        cat = expense["category"]
        category_totals[cat] = category_totals.get(cat, 0.0) + expense["amount"]

    by_category = [
        CategorySummary(
            category=cat,
            total=round(total_amount, 2)
        )
        for cat, total_amount in category_totals.items()
    ]
    return ExpenseSummary(
        total=total,
        by_category=by_category
    )


@app.get("/expenses/search", response_model=list[Expense])
def search_expenses(q: str = Query(..., min_length=1)) -> list[Expense]:
    """Search expenses by title or category (case-insensitive)."""
    expenses = _load_expenses()
    query = q.lower()
    matched = [
        e
        for e in expenses
        if query in e["title"].lower() or query in e["category"].lower()
    ]
    return [Expense(**e) for e in matched]


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: str) -> None:
    """Remove an expense by ID. Raises 404 if the ID is not found."""
    expenses = _load_expenses()
    for index, expense in enumerate(expenses):
        if expense["id"] == expense_id:
            expenses.pop(index)
            _save_expenses(expenses)
            return
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Expense with id '{expense_id}' not found",
    )
