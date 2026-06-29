from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/", response_model=schemas.SummaryResponse)
def get_summary(db: Session = Depends(get_db)):
    """Return total income, total expenses, net balance, and transaction count."""
    return crud.get_summary(db)


@router.get("/by-category", response_model=list[schemas.CategoryBreakdown])
def get_category_breakdown(
    type: Optional[models.TransactionType] = Query(
        None, description="Limit breakdown to income or expense"
    ),
    db: Session = Depends(get_db),
):
    """Return spending/income grouped by category with percentage share."""
    return crud.get_category_breakdown(db, type)
