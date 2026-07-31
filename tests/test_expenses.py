import pytest
from fastapi.testclient import TestClient

import src.main as main
from src.main import app


@pytest.fixture(autouse=True)
def isolated_expenses_file(tmp_path, monkeypatch):
    test_file = tmp_path / "expenses.json"
    monkeypatch.setattr("src.main.EXPENSES_FILE", test_file)
    yield test_file


@pytest.fixture
def client():
    return TestClient(app)


def _sample_expense(
    title="Lunch",
    amount=12.50,
    category="Food",
    date="2026-07-31",
):
    return {
        "title": title,
        "amount": amount,
        "category": category,
        "date": date,
    }


def test_create_expense_returns_201(client):
    response = client.post("/expenses", json=_sample_expense())
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Lunch"
    assert data["amount"] == 12.50
    assert data["category"] == "Food"
    assert data["date"] == "2026-07-31"
    assert "id" in data


def test_create_expense_validates_title(client):
    payload = _sample_expense(title="")
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_validates_amount(client):
    payload = _sample_expense(amount=0)
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_list_expenses_returns_all(client):
    client.post("/expenses", json=_sample_expense(title="Lunch", category="Food"))
    client.post(
        "/expenses",
        json=_sample_expense(title="Bus fare", amount=5.0, category="Transport"),
    )

    response = client.get("/expenses")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_expenses_filters_by_category(client):
    client.post("/expenses", json=_sample_expense(title="Lunch", category="Food"))
    client.post(
        "/expenses",
        json=_sample_expense(title="Bus fare", amount=5.0, category="Transport"),
    )

    response = client.get("/expenses", params={"category": "Food"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Food"


def test_summary_empty(client):
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0.0
    assert data["by_category"] == []


def test_summary_with_expenses(client):
    client.post("/expenses", json=_sample_expense(amount=10.10, category="Food"))
    client.post("/expenses", json=_sample_expense(amount=5.05, category="Food"))
    client.post(
        "/expenses",
        json=_sample_expense(title="Taxi", amount=20.0, category="Transport"),
    )

    response = client.get("/expenses/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 35.15

    by_category = {item["category"]: item["total"] for item in data["by_category"]}
    assert by_category["Food"] == 15.15
    assert by_category["Transport"] == 20.0


def test_search_case_insensitive(client):
    client.post("/expenses", json=_sample_expense(title="Pizza Night", category="Food"))
    client.post(
        "/expenses",
        json=_sample_expense(title="Groceries", amount=30.0, category="food shop"),
    )

    response = client.get("/expenses/search", params={"q": "pizza"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Pizza Night"

    response = client.get("/expenses/search", params={"q": "FOOD"})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_expense_returns_204(client):
    create_response = client.post("/expenses", json=_sample_expense())
    expense_id = create_response.json()["id"]

    response = client.delete(f"/expenses/{expense_id}")
    assert response.status_code == 204
    assert response.content == b""

    list_response = client.get("/expenses")
    assert list_response.json() == []


def test_delete_nonexistent_expense_returns_404(client):
    response = client.delete("/expenses/nonexistent-id")
    assert response.status_code == 404


def test_summary_route_not_treated_as_id(client):
    response = client.get("/expenses/summary")
    assert response.status_code == 200
    assert "total" in response.json()


def test_isolated_expenses_file(isolated_expenses_file):
    assert main.EXPENSES_FILE == isolated_expenses_file
    assert not isolated_expenses_file.exists()


def test_create_expense_rejects_negative_amount(client):
    payload = _sample_expense(amount=-5.0)
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_rejects_invalid_date(client):
    payload = _sample_expense(date="not-a-date")
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_create_expense_rejects_missing_fields(client):
    response = client.post("/expenses", json={"title": "Oops"})
    assert response.status_code == 422


def test_create_expense_rejects_empty_category(client):
    payload = _sample_expense(category="")
    response = client.post("/expenses", json=payload)
    assert response.status_code == 422


def test_each_expense_gets_unique_id(client):
    ids = set()

    for i in range(5):
        response = client.post(
            "/expenses",
            json=_sample_expense(title=f"Item {i}")
        )
        ids.add(response.json()["id"])

    assert len(ids) == 5


def test_filter_nonexistent_category_returns_empty(client):
    client.post("/expenses", json=_sample_expense(category="Food"))

    response = client.get(
        "/expenses",
        params={"category": "Healthcare"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_search_no_matches_returns_empty(client):
    client.post("/expenses", json=_sample_expense())

    response = client.get(
        "/expenses/search",
        params={"q": "xyz"},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_search_empty_query_rejected(client):
    response = client.get(
        "/expenses/search",
        params={"q": ""},
    )

    assert response.status_code == 422


def test_delete_same_id_twice(client):
    create_response = client.post(
        "/expenses",
        json=_sample_expense(),
    )

    expense_id = create_response.json()["id"]

    client.delete(f"/expenses/{expense_id}")

    second_delete = client.delete(
        f"/expenses/{expense_id}"
    )

    assert second_delete.status_code == 404


def test_create_expense_accepts_large_amount(client):
    payload = _sample_expense(amount=999999.99)
    response = client.post("/expenses", json=payload)
    assert response.status_code == 201
    assert response.json()["amount"] == 999999.99


def test_create_expense_accepts_max_title_length(client):
    title = "x" * 100
    response = client.post("/expenses", json=_sample_expense(title=title))
    assert response.status_code == 201
    assert response.json()["title"] == title


def test_create_expense_rejects_title_over_max_length(client):
    title = "x" * 101
    response = client.post("/expenses", json=_sample_expense(title=title))
    assert response.status_code == 422


def test_create_expense_accepts_max_category_length(client):
    category = "c" * 50
    response = client.post("/expenses", json=_sample_expense(category=category))
    assert response.status_code == 201
    assert response.json()["category"] == category


def test_create_expense_rejects_category_over_max_length(client):
    category = "c" * 51
    response = client.post("/expenses", json=_sample_expense(category=category))
    assert response.status_code == 422


def test_invalid_http_method_on_expenses(client):
    response = client.put("/expenses", json=_sample_expense())
    assert response.status_code == 405

    response = client.patch("/expenses", json=_sample_expense())
    assert response.status_code == 405


def test_invalid_json_payload(client):
    response = client.post(
        "/expenses",
        content=b"not valid json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_multiple_sequential_deletes(client):
    ids = []
    for i in range(3):
        response = client.post(
            "/expenses",
            json=_sample_expense(title=f"Item {i}"),
        )
        ids.append(response.json()["id"])

    for expense_id in ids:
        response = client.delete(f"/expenses/{expense_id}")
        assert response.status_code == 204

    list_response = client.get("/expenses")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_load_expenses_handles_invalid_json(isolated_expenses_file):
    isolated_expenses_file.write_text("{ invalid json", encoding="utf-8")
    assert main._load_expenses() == []


def test_load_expenses_handles_empty_file(isolated_expenses_file):
    isolated_expenses_file.write_text("", encoding="utf-8")
    assert main._load_expenses() == []
