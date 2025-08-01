from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from datetime import date
from dateutil.relativedelta import relativedelta

from database import get_db
from models import BudgetPeriod, BudgetCategory, BudgetItem

router = APIRouter()

# Pydantic models
class BudgetCategoryCreate(BaseModel):
    name: str
    parent_category_id: Optional[UUID] = None
    color: Optional[str] = None

class BudgetCategoryResponse(BaseModel):
    id: str
    name: str
    parent_category_id: Optional[str]
    color: Optional[str]
    is_active: bool

class BudgetPeriodCreate(BaseModel):
    name: str
    start_date: date
    end_date: date

class BudgetPeriodResponse(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    is_active: bool

class BudgetItemCreate(BaseModel):
    category_id: UUID
    allocated_amount: Decimal
    rollover_enabled: bool = False
    notes: Optional[str] = None

class BudgetItemResponse(BaseModel):
    id: str
    category_id: str
    category_name: str
    allocated_amount: Decimal
    rollover_from_previous: Decimal
    rollover_enabled: bool
    spent_amount: Decimal
    remaining_amount: Decimal
    notes: Optional[str]

@router.get("/categories", response_model=List[BudgetCategoryResponse])
async def get_budget_categories(
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get all budget categories"""
    categories = db.query(BudgetCategory).filter(
        BudgetCategory.user_id == current_user_id,
        BudgetCategory.is_active == True
    ).all()
    
    return [
        BudgetCategoryResponse(
            id=str(category.id),
            name=category.name,
            parent_category_id=str(category.parent_category_id) if category.parent_category_id else None,
            color=category.color,
            is_active=category.is_active
        )
        for category in categories
    ]

@router.post("/categories", response_model=BudgetCategoryResponse)
async def create_budget_category(
    category: BudgetCategoryCreate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create a new budget category"""
    db_category = BudgetCategory(
        user_id=current_user_id,
        name=category.name,
        parent_category_id=category.parent_category_id,
        color=category.color
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return BudgetCategoryResponse(
        id=str(db_category.id),
        name=db_category.name,
        parent_category_id=str(db_category.parent_category_id) if db_category.parent_category_id else None,
        color=db_category.color,
        is_active=db_category.is_active
    )

@router.get("/periods", response_model=List[BudgetPeriodResponse])
async def get_budget_periods(
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get all budget periods"""
    periods = db.query(BudgetPeriod).filter(
        BudgetPeriod.user_id == current_user_id,
        BudgetPeriod.is_active == True
    ).order_by(BudgetPeriod.start_date.desc()).all()
    
    return [
        BudgetPeriodResponse(
            id=str(period.id),
            name=period.name,
            start_date=period.start_date,
            end_date=period.end_date,
            is_active=period.is_active
        )
        for period in periods
    ]

@router.post("/periods", response_model=BudgetPeriodResponse)
async def create_budget_period(
    period: BudgetPeriodCreate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create a new budget period"""
    db_period = BudgetPeriod(
        user_id=current_user_id,
        name=period.name,
        start_date=period.start_date,
        end_date=period.end_date
    )
    
    db.add(db_period)
    db.commit()
    db.refresh(db_period)
    
    return BudgetPeriodResponse(
        id=str(db_period.id),
        name=db_period.name,
        start_date=db_period.start_date,
        end_date=db_period.end_date,
        is_active=db_period.is_active
    )

@router.post("/periods/{period_id}/rollover")
async def create_budget_with_rollover(
    period_id: UUID,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create next month's budget with rollover functionality"""
    current_period = db.query(BudgetPeriod).filter(
        BudgetPeriod.id == period_id,
        BudgetPeriod.user_id == current_user_id
    ).first()
    
    if not current_period:
        raise HTTPException(status_code=404, detail="Budget period not found")
    
    # Calculate next month
    next_start = current_period.end_date + relativedelta(days=1)
    next_end = next_start + relativedelta(months=1) - relativedelta(days=1)
    
    # Create new period
    new_period = BudgetPeriod(
        user_id=current_user_id,
        name=f"Budget - {next_start.strftime('%B %Y')}",
        start_date=next_start,
        end_date=next_end
    )
    
    db.add(new_period)
    db.commit()
    db.refresh(new_period)
    
    # Copy budget items with rollover
    current_items = db.query(BudgetItem).filter(
        BudgetItem.budget_period_id == period_id
    ).all()
    
    for item in current_items:
        rollover_amount = Decimal('0.00')
        if item.rollover_enabled:
            # Calculate rollover (simplified - would need transaction data)
            rollover_amount = item.allocated_amount + item.rollover_from_previous
        
        new_item = BudgetItem(
            budget_period_id=new_period.id,
            category_id=item.category_id,
            allocated_amount=item.allocated_amount,
            rollover_from_previous=rollover_amount,
            rollover_enabled=item.rollover_enabled,
            notes=item.notes
        )
        db.add(new_item)
    
    db.commit()
    return {"message": "Budget created with rollover", "period_id": str(new_period.id)}
