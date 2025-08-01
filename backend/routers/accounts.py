from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from uuid import UUID

from database import get_db
from models import Account

router = APIRouter()

# Pydantic models
class AccountCreate(BaseModel):
    name: str
    account_type: str
    balance: Optional[Decimal] = Decimal('0.00')
    currency: Optional[str] = "USD"
    simplefin_account_id: Optional[str] = None

class AccountUpdate(BaseModel):
    name: Optional[str] = None
    account_type: Optional[str] = None
    balance: Optional[Decimal] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None

class AccountResponse(BaseModel):
    id: str
    name: str
    account_type: str
    balance: Decimal
    currency: str
    simplefin_account_id: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AccountResponse])
async def get_accounts(
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get all accounts for the current user"""
    accounts = db.query(Account).filter(
        Account.user_id == current_user_id,
        Account.is_active == True
    ).all()
    
    return [
        AccountResponse(
            id=str(account.id),
            name=account.name,
            account_type=account.account_type,
            balance=account.balance,
            currency=account.currency,
            simplefin_account_id=account.simplefin_account_id,
            is_active=account.is_active,
            created_at=account.created_at.isoformat(),
            updated_at=account.updated_at.isoformat()
        )
        for account in accounts
    ]

@router.post("/", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    db_account = Account(
        user_id=current_user_id,
        name=account.name,
        account_type=account.account_type,
        balance=account.balance,
        currency=account.currency,
        simplefin_account_id=account.simplefin_account_id
    )
    
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return AccountResponse(
        id=str(db_account.id),
        name=db_account.name,
        account_type=db_account.account_type,
        balance=db_account.balance,
        currency=db_account.currency,
        simplefin_account_id=db_account.simplefin_account_id,
        is_active=db_account.is_active,
        created_at=db_account.created_at.isoformat(),
        updated_at=db_account.updated_at.isoformat()
    )

@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: UUID,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get a specific account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    return AccountResponse(
        id=str(account.id),
        name=account.name,
        account_type=account.account_type,
        balance=account.balance,
        currency=account.currency,
        simplefin_account_id=account.simplefin_account_id,
        is_active=account.is_active,
        created_at=account.created_at.isoformat(),
        updated_at=account.updated_at.isoformat()
    )

@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: UUID,
    account_update: AccountUpdate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Update an account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Update fields
    update_data = account_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    
    return AccountResponse(
        id=str(account.id),
        name=account.name,
        account_type=account.account_type,
        balance=account.balance,
        currency=account.currency,
        simplefin_account_id=account.simplefin_account_id,
        is_active=account.is_active,
        created_at=account.created_at.isoformat(),
        updated_at=account.updated_at.isoformat()
    )

@router.delete("/{account_id}")
async def delete_account(
    account_id: UUID,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Delete (deactivate) an account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user_id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Soft delete - just mark as inactive
    account.is_active = False
    db.commit()
    
    return {"message": "Account deleted successfully"}
