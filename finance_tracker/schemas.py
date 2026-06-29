from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .models import TransactionType


class TransactionBase(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount (must be positive)")
    type: TransactionType
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    date: date


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    date: Optional[date] = None


class Transaction(TransactionBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SummaryResponse(BaseModel):
    total_income: float
    total_expenses: float
    net_balance: float
    transaction_count: int


class CategoryBreakdown(BaseModel):
    category: str
    total: float
    count: int
    percentage: float
