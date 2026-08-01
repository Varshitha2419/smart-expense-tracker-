AI Usage Notes

1. Which parts of the code were AI-generated vs. written by me

I used ChatGPT to help generate the initial project structure, the FastAPI application in `src/main.py` (including the endpoints, Pydantic models, JSON file storage, summary and search logic), the test suite in `tests/test_expenses.py`, and the initial `README.md`.

I reviewed the generated code, made improvements where needed, and ensured it met the assignment requirements. I also went through the generated code function by function until I could explain what each part does and why. For example, I understood why the expense ID is generated on the server using `uuid.uuid4()`, why `/expenses/summary` and `/expenses/search` are defined before the parameterized route, and why `_load_expenses()` returns an empty list if the JSON file is missing, empty, or invalid.

I did not personally encounter these as bugs during development—they were already handled correctly in the generated code—but I made sure I understood the reasoning behind them instead of treating the implementation as a black box.



 2. What I validated, tested, or changed, and why

- Ran the complete test suite using `python -m pytest tests/ -v` and confirmed that all **31 tests passed**.
- Started the FastAPI application locally and tested every endpoint through the Swagger UI (`/docs`) to verify that creating, listing, filtering, searching, summarizing, and deleting expenses worked as expected.
- Verified that the API responses matched the examples documented in the `README.md`.
- Verified the empty summary case (`GET /expenses/summary` returns `{"total": 0.0, "by_category": []}` when no expenses exist).
- Verified that deleting the same expense twice returns **204 No Content** on the first request and **404 Not Found** on the second request.
- Verified through the passing tests that the test isolation setup (`tmp_path` and `monkeypatch`) worked as intended and prevented the real `expenses.json` file from being modified during testing.
- Updated the `README.md` to include installation steps, project features, folder structure, API examples, validation rules, and testing instructions.
- Reviewed the AI-generated validation logic (field length limits, positive amount validation, and date validation) and confirmed that it behaved correctly through the existing tests.

---

3. AI suggestions I decided not to use, and why

The AI suggested adding additional features such as authentication, Docker support, a database backend, pagination, and update (`PUT`/`PATCH`) endpoints.

I decided not to include these because the assignment specifically required using a local JSON file instead of a database and focused only on the requested REST API functionality. I kept the implementation aligned with the assignment requirements and included only the optional **search** feature.

---

