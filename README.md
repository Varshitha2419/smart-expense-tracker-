# Smart Expense Tracker REST API

A REST API built with FastAPI for managing personal expenses. It supports creating, listing, searching, filtering, summarizing, and deleting expenses, with data stored locally in a JSON file (`expenses.json`).

## Installation

```bash
pip install -r requirements.txt
```

## Run the Server

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Run Tests

```bash
python -m pytest tests/ -v
```

## Project Features

- Create, list, search, and delete personal expenses
- Filter expenses by category
- View spending summary with totals grouped by category
- Case-insensitive search across title and category fields
- Input validation using Pydantic v2 models
- Local JSON file persistence (no database required)
- Interactive Swagger UI for API exploration

## Folder Structure

```text
smart-expense-tracker/
├── src/
│   ├── __init__.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_expenses.py
├── requirements.txt
├── README.md
├── AI_NOTES.md
└── expenses.json        # Created automatically when data is first saved
```

## Technologies Used

- Python 3.10+
- FastAPI
- Pydantic v2
- Uvicorn
- pytest
- httpx (used by FastAPI TestClient)

## API Endpoints

| Method | Endpoint | Status | Description |
|--------|----------|:------:|-------------|
| POST | `/expenses` | 201 | Create a new expense |
| GET | `/expenses` | 200 | List all expenses |
| GET | `/expenses?category=Food` | 200 | Filter expenses by category |
| GET | `/expenses/summary` | 200 | Get total expenses overall and by category |
| GET | `/expenses/search?q=lunch` | 200 | Search expenses by title or category |
| DELETE | `/expenses/{expense_id}` | 204 | Delete an expense |

## Example Requests

### Create an Expense

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":12.50,"category":"Food","date":"2026-07-31"}'
```

### List All Expenses

```bash
curl http://127.0.0.1:8000/expenses
```

### Filter by Category

```bash
curl "http://127.0.0.1:8000/expenses?category=Food"
```

### Get Summary

```bash
curl http://127.0.0.1:8000/expenses/summary
```

### Search Expenses

```bash
curl "http://127.0.0.1:8000/expenses/search?q=lunch"
```

### Delete an Expense

```bash
curl -X DELETE http://127.0.0.1:8000/expenses/{expense_id}
```

## Example Responses

### POST /expenses (201)

```json
{
  "title": "Lunch",
  "amount": 12.5,
  "category": "Food",
  "date": "2026-07-31",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### GET /expenses (200)

```json
[
  {
    "title": "Lunch",
    "amount": 12.5,
    "category": "Food",
    "date": "2026-07-31",
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  }
]
```

### GET /expenses/summary (200)

```json
{
  "total": 35.15,
  "by_category": [
    {
      "category": "Food",
      "total": 15.15
    },
    {
      "category": "Transport",
      "total": 20.0
    }
  ]
}
```

### DELETE /expenses/{expense_id} (204)

No response body.

## Validation Rules

| Field | Validation |
|-------|------------|
| `title` | Required, 1–100 characters |
| `amount` | Required, greater than 0 |
| `category` | Required, 1–50 characters |
| `date` | Required ISO date (`YYYY-MM-DD`) |
| `q` | Search query, minimum 1 character |

## Data Storage

Expenses are stored in `expenses.json` at the project root. The file is created automatically on the first write. Data is stored as a JSON array. If the file is missing, empty, or contains invalid JSON, the API safely treats the expense list as empty.

## API Documentation

After starting the server:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Common Error Responses

### 422 Unprocessable Entity

```json
{
  "detail": [
    {
      "type": "greater_than",
      "loc": ["body", "amount"],
      "msg": "Input should be greater than 0",
      "input": 0
    }
  ]
}
```

### 404 Not Found

```json
{
  "detail": "Expense with id 'nonexistent-id' not found"
}
```

### 405 Method Not Allowed

Returned when an unsupported HTTP method is used.

## Running the Tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests use a temporary JSON file, so they do not modify the real `expenses.json`.

## Future Improvements

- Add pagination for large expense lists
- Support date-range filtering
- Add update (`PUT`/`PATCH`) endpoints
- Migrate to a database
- Add authentication and multi-user support