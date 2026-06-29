from datetime import date

from fastapi.testclient import TestClient


TODAY = str(date.today())


def test_create_transaction_income(client: TestClient):
    response = client.post(
        "/transactions/",
        json={"amount": 3000.00, "type": "income", "category": "Salary", "date": TODAY},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 3000.00
    assert data["type"] == "income"
    assert data["category"] == "Salary"
    assert "id" in data
    assert "created_at" in data


def test_create_transaction_expense(client: TestClient):
    response = client.post(
        "/transactions/",
        json={
            "amount": 75.50,
            "type": "expense",
            "category": "Groceries",
            "description": "Weekly shop",
            "date": TODAY,
        },
    )
    assert response.status_code == 201
    assert response.json()["description"] == "Weekly shop"


def test_create_transaction_invalid_amount(client: TestClient):
    response = client.post(
        "/transactions/",
        json={"amount": -100, "type": "expense", "category": "Food", "date": TODAY},
    )
    assert response.status_code == 422


def test_create_transaction_zero_amount(client: TestClient):
    response = client.post(
        "/transactions/",
        json={"amount": 0, "type": "expense", "category": "Food", "date": TODAY},
    )
    assert response.status_code == 422


def test_create_transaction_invalid_type(client: TestClient):
    response = client.post(
        "/transactions/",
        json={"amount": 50, "type": "transfer", "category": "Misc", "date": TODAY},
    )
    assert response.status_code == 422


def test_list_transactions_empty(client: TestClient):
    response = client.get("/transactions/")
    assert response.status_code == 200
    assert response.json() == []


def test_list_transactions(client: TestClient):
    client.post("/transactions/", json={"amount": 500, "type": "expense", "category": "Rent", "date": TODAY})
    client.post("/transactions/", json={"amount": 3000, "type": "income", "category": "Salary", "date": TODAY})
    response = client.get("/transactions/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_transactions_filter_by_type(client: TestClient):
    client.post("/transactions/", json={"amount": 500, "type": "expense", "category": "Rent", "date": TODAY})
    client.post("/transactions/", json={"amount": 3000, "type": "income", "category": "Salary", "date": TODAY})
    response = client.get("/transactions/?type=expense")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Rent"


def test_list_transactions_filter_by_category(client: TestClient):
    client.post("/transactions/", json={"amount": 200, "type": "expense", "category": "Groceries", "date": TODAY})
    client.post("/transactions/", json={"amount": 50, "type": "expense", "category": "Coffee", "date": TODAY})
    response = client.get("/transactions/?category=groc")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Groceries"


def test_get_transaction_by_id(client: TestClient):
    created = client.post(
        "/transactions/",
        json={"amount": 150, "type": "expense", "category": "Dining Out", "date": TODAY},
    ).json()
    response = client.get(f"/transactions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_transaction_not_found(client: TestClient):
    response = client.get("/transactions/9999")
    assert response.status_code == 404


def test_update_transaction(client: TestClient):
    created = client.post(
        "/transactions/",
        json={"amount": 200, "type": "expense", "category": "Food", "date": TODAY},
    ).json()
    response = client.put(
        f"/transactions/{created['id']}",
        json={"amount": 250, "category": "Groceries"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 250
    assert data["category"] == "Groceries"
    assert data["type"] == "expense"  # unchanged


def test_update_transaction_not_found(client: TestClient):
    response = client.put("/transactions/9999", json={"amount": 100})
    assert response.status_code == 404


def test_delete_transaction(client: TestClient):
    created = client.post(
        "/transactions/",
        json={"amount": 50, "type": "expense", "category": "Coffee", "date": TODAY},
    ).json()
    response = client.delete(f"/transactions/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/transactions/{created['id']}").status_code == 404


def test_delete_transaction_not_found(client: TestClient):
    response = client.delete("/transactions/9999")
    assert response.status_code == 404
