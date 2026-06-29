# Finance Tracker API

A RESTful API for tracking personal income and expenses — built with **FastAPI**, **SQLAlchemy 2.0**, and **Pydantic v2**.

[![CI](https://github.com/ACampos-Pro/finance-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/ACampos-Pro/finance-tracker/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- Full **CRUD** for financial transactions (income & expenses)
- **Filtering** by type, category, and date range
- **Summary endpoint** — total income, total expenses, and net balance
- **Category breakdown** with percentage share per category
- **Auto-generated interactive docs** at `/docs` (Swagger UI) and `/redoc`
- Comprehensive **pytest** test suite with 95%+ coverage
- **GitHub Actions** CI pipeline across Python 3.10 / 3.11 / 3.12

## Tech Stack

| Layer | Library |
|-------|---------|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM | [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) |
| Validation | [Pydantic v2](https://docs.pydantic.dev/) |
| Database | SQLite (swappable for PostgreSQL/MySQL) |
| Server | [Uvicorn](https://www.uvicorn.org/) |
| Testing | [pytest](https://pytest.org/) + [HTTPX](https://www.python-httpx.org/) |

## Quick Start

### 1. Clone and set up

```bash
git clone https://github.com/ACampos-Pro/finance-tracker.git
cd finance-tracker

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install -e ".[dev]"
```

### 2. Run the server

```bash
uvicorn finance_tracker.main:app --reload
```

The API is live at **http://localhost:8000**.  
Interactive docs: **http://localhost:8000/docs**

### 3. (Optional) Seed demo data

```bash
python seed.py
```

## API Reference

### Transactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/transactions/` | Create a transaction |
| `GET` | `/transactions/` | List transactions (with filters) |
| `GET` | `/transactions/{id}` | Get a single transaction |
| `PUT` | `/transactions/{id}` | Update a transaction |
| `DELETE` | `/transactions/{id}` | Delete a transaction |

**Query filters for `GET /transactions/`:**
- `type` — `income` or `expense`
- `category` — partial string match
- `start_date` / `end_date` — ISO 8601 date (`YYYY-MM-DD`)
- `skip` / `limit` — pagination

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/summary/` | Total income, expenses, net balance |
| `GET` | `/summary/by-category` | Per-category totals and percentages |

## Example Usage

```bash
# Add a salary payment
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{"amount": 3500, "type": "income", "category": "Salary", "date": "2024-06-01"}'

# Add a rent expense
curl -X POST http://localhost:8000/transactions/ \
  -H "Content-Type: application/json" \
  -d '{"amount": 950, "type": "expense", "category": "Rent", "date": "2024-06-02"}'

# Get your financial summary
curl http://localhost:8000/summary/

# See expense breakdown by category
curl "http://localhost:8000/summary/by-category?type=expense"

# Filter transactions by date range
curl "http://localhost:8000/transactions/?start_date=2024-06-01&end_date=2024-06-30"
```

**Example summary response:**

```json
{
  "total_income": 3500.0,
  "total_expenses": 950.0,
  "net_balance": 2550.0,
  "transaction_count": 2
}
```

**Example category breakdown response:**

```json
[
  { "category": "Rent", "total": 950.0, "count": 1, "percentage": 100.0 }
]
```

## Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=finance_tracker --cov-report=term-missing
```

## Project Structure

```
finance-tracker/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── finance_tracker/
│   ├── routers/
│   │   ├── transactions.py     # CRUD endpoints
│   │   └── summary.py          # Analytics endpoints
│   ├── main.py                 # FastAPI app & lifespan handler
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── crud.py                 # Database operations
│   └── database.py             # Engine, session factory, dependency
├── tests/
│   ├── conftest.py             # Shared fixtures (isolated test DB)
│   ├── test_transactions.py    # CRUD endpoint tests
│   └── test_summary.py        # Analytics endpoint tests
├── seed.py                     # Demo data generator
├── pyproject.toml
└── .gitignore
```

## Design Decisions

- **SQLite by default** — zero-config for development; swap the `SQLALCHEMY_DATABASE_URL` in `database.py` for any SQLAlchemy-supported database.
- **Pydantic v2 `model_dump(exclude_unset=True)`** on PATCH-style updates so only provided fields are written.
- **Dependency injection via `Depends(get_db)`** keeps route handlers thin and makes the test DB override a one-liner.
- **`asynccontextmanager` lifespan** creates tables on startup so there's no separate migration step for the SQLite default setup.

## License

[MIT](LICENSE)
