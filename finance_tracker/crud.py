from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas


def get_transaction(db: Session, transaction_id: int) -> Optional[models.Transaction]:
    return db.get(models.Transaction, transaction_id)


def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[models.TransactionType] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list[models.Transaction]:
    stmt = select(models.Transaction)
    if type:
        stmt = stmt.where(models.Transaction.type == type)
    if category:
        stmt = stmt.where(models.Transaction.category.ilike(f"%{category}%"))
    if start_date:
        stmt = stmt.where(models.Transaction.date >= start_date)
    if end_date:
        stmt = stmt.where(models.Transaction.date <= end_date)
    stmt = stmt.order_by(models.Transaction.date.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create_transaction(
    db: Session, transaction: schemas.TransactionCreate
) -> models.Transaction:
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def update_transaction(
    db: Session, transaction_id: int, transaction: schemas.TransactionUpdate
) -> Optional[models.Transaction]:
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return None
    for field, value in transaction.model_dump(exclude_unset=True).items():
        setattr(db_transaction, field, value)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def delete_transaction(db: Session, transaction_id: int) -> bool:
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return False
    db.delete(db_transaction)
    db.commit()
    return True


def get_summary(db: Session) -> dict:
    income = db.scalar(
        select(func.sum(models.Transaction.amount)).where(
            models.Transaction.type == models.TransactionType.income
        )
    ) or 0.0
    expenses = db.scalar(
        select(func.sum(models.Transaction.amount)).where(
            models.Transaction.type == models.TransactionType.expense
        )
    ) or 0.0
    count = db.scalar(select(func.count(models.Transaction.id))) or 0
    return {
        "total_income": income,
        "total_expenses": expenses,
        "net_balance": income - expenses,
        "transaction_count": count,
    }


def get_category_breakdown(
    db: Session, type: Optional[models.TransactionType] = None
) -> list[dict]:
    stmt = (
        select(
            models.Transaction.category,
            func.sum(models.Transaction.amount).label("total"),
            func.count(models.Transaction.id).label("count"),
        )
        .group_by(models.Transaction.category)
        .order_by(func.sum(models.Transaction.amount).desc())
    )
    if type:
        stmt = stmt.where(models.Transaction.type == type)
    rows = db.execute(stmt).all()
    grand_total = sum(r.total for r in rows) or 1.0
    return [
        {
            "category": r.category,
            "total": r.total,
            "count": r.count,
            "percentage": round(r.total / grand_total * 100, 2),
        }
        for r in rows
    ]
