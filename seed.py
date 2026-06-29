"""
Seed the database with sample transactions for demo purposes.

Usage:
    python seed.py
"""
import random
from datetime import date, timedelta

from finance_tracker import models
from finance_tracker.crud import create_transaction
from finance_tracker.database import SessionLocal, engine
from finance_tracker.schemas import TransactionCreate

models.Base.metadata.create_all(bind=engine)

INCOME_SOURCES = ["Salary", "Freelance", "Dividends", "Side Project"]
EXPENSE_CATEGORIES = [
    "Rent",
    "Groceries",
    "Utilities",
    "Entertainment",
    "Transport",
    "Healthcare",
    "Dining Out",
    "Subscriptions",
]


def seed(months: int = 6) -> None:
    db = SessionLocal()
    try:
        today = date.today()
        for i in range(months):
            month_start = today.replace(day=1) - timedelta(days=30 * i)

            # Primary income each month
            create_transaction(
                db,
                TransactionCreate(
                    amount=round(random.uniform(3000, 5500), 2),
                    type=models.TransactionType.income,
                    category="Salary",
                    description="Monthly salary",
                    date=month_start,
                ),
            )

            # Occasional side income
            if random.random() > 0.5:
                create_transaction(
                    db,
                    TransactionCreate(
                        amount=round(random.uniform(100, 800), 2),
                        type=models.TransactionType.income,
                        category=random.choice(["Freelance", "Side Project"]),
                        date=month_start + timedelta(days=random.randint(1, 20)),
                    ),
                )

            # Several expenses throughout the month
            for _ in range(random.randint(8, 15)):
                create_transaction(
                    db,
                    TransactionCreate(
                        amount=round(random.uniform(10, 600), 2),
                        type=models.TransactionType.expense,
                        category=random.choice(EXPENSE_CATEGORIES),
                        date=month_start + timedelta(days=random.randint(0, 28)),
                    ),
                )

        print(f"Seeded {months} months of transactions successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
