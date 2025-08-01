from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from uuid import UUID
from datetime import date

from database import get_db
from models import Transaction, Account, BudgetCategory

router = APIRouter()

# Pydantic models
class TransactionCreate(BaseModel):
    account_id: UUID
    amount: Decimal
    description: Optional[str] = None
    transaction_date: date
    category_id: Optional[UUID] = None
    payee: Optional[str] = None
    memo: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    account_name: str
    amount: Decimal
    description: Optional[str]
    transaction_date: date
    category_id: Optional[str]
    category_name: Optional[str]
    payee: Optional[str]
    memo: Optional[str]
    is_reconciled: bool
    created_at: str

@router.get("/", response_model=List[TransactionResponse])
async def get_transactions(
    account_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    limit: int = 100,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering"""
    query = db.query(Transaction, Account, BudgetCategory).join(
        Account, Transaction.account_id == Account.id
    ).outerjoin(
        BudgetCategory, Transaction.category_id == BudgetCategory.id
    ).filter(Account.user_id == current_user_id)
    
    if account_id:
        query = query.filter(Transaction.account_id == account_id)
    if category_id:
        query = query.filter(Transaction.category_id == category_id)
    
    transactions = query.order_by(Transaction.transaction_date.desc()).limit(limit).all()
    
    return [
        TransactionResponse(
            id=str(transaction.id),
            account_id=str(transaction.account_id),
            account_name=account.name,
            amount=transaction.amount,
            description=transaction.description,
            transaction_date=transaction.transaction_date,
            category_id=str(transaction.category_id) if transaction.category_id else None,
            category_name=category.name if category else None,
            payee=transaction.payee,
            memo=transaction.memo,
            is_reconciled=transaction.is_reconciled,
            created_at=transaction.created_at.isoformat()
        )
        for transaction, account, category in transactions
    ]

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    # Verify account belongs to user
    account = db.query(Account).filter(
        Account.id == transaction.account_id,
        Account.user_id == current_user_id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    db_transaction = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
        category_id=transaction.category_id,
        payee=transaction.payee,
        memo=transaction.memo
    )
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    
    # Get category name for response
    category = None
    if db_transaction.category_id:
        category = db.query(BudgetCategory).filter(
            BudgetCategory.id == db_transaction.category_id
        ).first()
    
    return TransactionResponse(
        id=str(db_transaction.id),
        account_id=str(db_transaction.account_id),
        account_name=account.name,
        amount=db_transaction.amount,
        description=db_transaction.description,
        transaction_date=db_transaction.transaction_date,
        category_id=str(db_transaction.category_id) if db_transaction.category_id else None,
        category_name=category.name if category else None,
        payee=db_transaction.payee,
        memo=db_transaction.memo,
        is_reconciled=db_transaction.is_reconciled,
        created_at=db_transaction.created_at.isoformat()
    )
