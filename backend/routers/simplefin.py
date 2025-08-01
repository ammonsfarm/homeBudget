"""
SimpleFIN API Router

Handles SimpleFIN integration endpoints for token exchange and transaction sync.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import logging

from database import get_db
from models import User, Transaction, Account
from utils.security import get_current_user
from services.simplefin import SimpleFINService, SimpleFINError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/simplefin", tags=["SimpleFIN"])

class SetupTokenRequest(BaseModel):
    setup_token: str

class SetupTokenResponse(BaseModel):
    access_url: str
    message: str

class SyncResponse(BaseModel):
    success: bool
    transactions_imported: int
    message: str

class SimpleFINAccount(BaseModel):
    external_id: str
    name: str
    organization: str
    balance: Optional[str] = None
    currency: str = "USD"

class SimpleFINTransaction(BaseModel):
    external_id: str
    account_name: str
    organization: str
    description: str
    amount: str
    date: str
    pending: bool
    category: Optional[str] = None

@router.post("/setup", response_model=SetupTokenResponse)
async def setup_simplefin_connection(
    request: SetupTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exchange SimpleFIN setup token for access URL and store for user
    """
    try:
        async with SimpleFINService() as service:
            # Exchange setup token for access URL
            access_url = await service.exchange_setup_token(request.setup_token)
            
            # Store access URL in user record (you may want a separate table for this)
            current_user.simplefin_access_url = access_url
            db.commit()
            
            return SetupTokenResponse(
                access_url=access_url,
                message="SimpleFIN connection established successfully"
            )
            
    except SimpleFINError as e:
        logger.error(f"SimpleFIN setup error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during SimpleFIN setup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to setup SimpleFIN connection")

@router.post("/sync", response_model=SyncResponse)
async def sync_transactions(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Sync transactions from SimpleFIN API
    """
    if not current_user.simplefin_access_url:
        raise HTTPException(
            status_code=400, 
            detail="SimpleFIN not configured. Please setup SimpleFIN connection first."
        )
    
    try:
        async with SimpleFINService() as service:
            # Fetch transactions from SimpleFIN
            transactions = await service.sync_user_transactions(current_user.simplefin_access_url)
            
            # Process transactions in background
            background_tasks.add_task(
                process_simplefin_transactions,
                transactions,
                current_user.id,
                db
            )
            
            return SyncResponse(
                success=True,
                transactions_imported=len(transactions),
                message=f"Importing {len(transactions)} transactions in background"
            )
            
    except SimpleFINError as e:
        logger.error(f"SimpleFIN sync error for user {current_user.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during SimpleFIN sync: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to sync transactions")

@router.get("/status")
async def get_simplefin_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get SimpleFIN connection status for current user
    """
    return {
        "connected": bool(current_user.simplefin_access_url),
        "access_url_configured": bool(current_user.simplefin_access_url)
    }

@router.delete("/disconnect")
async def disconnect_simplefin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect SimpleFIN integration
    """
    current_user.simplefin_access_url = None
    db.commit()
    
    return {"message": "SimpleFIN connection removed successfully"}

async def process_simplefin_transactions(
    transactions: List[dict],
    user_id: str,
    db: Session
):
    """
    Background task to process and store SimpleFIN transactions
    """
    try:
        imported_count = 0
        
        for txn_data in transactions:
            # Check if transaction already exists
            existing_txn = db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.external_id == txn_data['external_id']
            ).first()
            
            if existing_txn:
                # Update existing transaction if needed
                existing_txn.description = txn_data['description']
                existing_txn.amount = txn_data['amount']
                existing_txn.date = txn_data['date']
                existing_txn.pending = txn_data['pending']
                continue
            
            # Find or create account
            account = db.query(Account).filter(
                Account.user_id == user_id,
                Account.external_id == txn_data['account_id']
            ).first()
            
            if not account:
                account = Account(
                    user_id=user_id,
                    name=txn_data['account_name'],
                    account_type='checking',  # Default type
                    external_id=txn_data['account_id'],
                    institution=txn_data['organization']
                )
                db.add(account)
                db.flush()  # Get account ID
            
            # Create new transaction
            transaction = Transaction(
                user_id=user_id,
                account_id=account.id,
                description=txn_data['description'],
                amount=txn_data['amount'],
                date=txn_data['date'],
                external_id=txn_data['external_id'],
                pending=txn_data['pending'],
                source='simplefin'
            )
            
            db.add(transaction)
            imported_count += 1
        
        db.commit()
        logger.info(f"Successfully imported {imported_count} transactions for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing SimpleFIN transactions: {str(e)}")
        db.rollback()
        raise
