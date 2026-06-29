import pytest
from datetime import date

from fastapi.testclient import TestClient

TODAY = str(date.today())


def _add(client, amount, type_, category):
    return client.post(
        "/transactions/",
        json={"amount": amount, "type": type_, "category": category, "date": TODAY},
    )


def test_summary_empty_db(client: TestClient):
    response = client.get("/summary/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_income"] == 0
    assert data["total_expenses"] == 0
    assert data["net_balance"] == 0
    assert data["transaction_count"] == 0


def test_summary_with_transactions(client: TestClient):
    _add(client, 3000, "income", "Salary")
    _add(client, 1000, "income", "Freelance")
    _add(client, 800, "expense", "Rent")
    _add(client, 200, "expense", "Groceries")

    response = client.get("/summary/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_income"] == 4000
    assert data["total_expenses"] == 1000
    assert data["net_balance"] == 3000
    assert data["transaction_count"] == 4


def test_category_breakdown_all(client: TestClient):
    _add(client, 300, "expense", "Rent")
    _add(client, 200, "expense", "Groceries")
    _add(client, 100, "expense", "Coffee")

    response = client.get("/summary/by-category")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    # highest amount first
    assert data[0]["category"] == "Rent"
    assert data[0]["percentage"] == 50.0


def test_category_breakdown_filter_by_type(client: TestClient):
    _add(client, 3000, "income", "Salary")
    _add(client, 500, "income", "Freelance")
    _add(client, 400, "expense", "Rent")
    _add(client, 100, "expense", "Food")

    expense_resp = client.get("/summary/by-category?type=expense")
    assert expense_resp.status_code == 200
    expense_data = expense_resp.json()
    assert len(expense_data) == 2
    categories = [r["category"] for r in expense_data]
    assert "Salary" not in categories

    income_resp = client.get("/summary/by-category?type=income")
    assert income_resp.status_code == 200
    income_data = income_resp.json()
    assert len(income_data) == 2
    assert income_data[0]["category"] == "Salary"
    assert income_data[0]["percentage"] == pytest.approx(85.71, abs=0.1)  # 3000/3500


def test_category_breakdown_percentages_sum_to_100(client: TestClient):
    _add(client, 400, "expense", "Rent")
    _add(client, 300, "expense", "Food")
    _add(client, 200, "expense", "Transport")
    _add(client, 100, "expense", "Entertainment")

    data = client.get("/summary/by-category?type=expense").json()
    total_pct = sum(r["percentage"] for r in data)
    assert abs(total_pct - 100.0) < 0.1
