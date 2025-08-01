from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import date

from database import get_db
from models import NetWorthSnapshot

router = APIRouter()

# Pydantic models
class NetWorthSnapshotCreate(BaseModel):
    snapshot_date: date
    total_assets: Decimal
    total_liabilities: Decimal
    notes: Optional[str] = None

class NetWorthSnapshotResponse(BaseModel):
    id: str
    snapshot_date: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    notes: Optional[str]
    created_at: str

@router.get("/", response_model=List[NetWorthSnapshotResponse])
async def get_net_worth_snapshots(
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get all net worth snapshots for the current user"""
    snapshots = db.query(NetWorthSnapshot).filter(
        NetWorthSnapshot.user_id == current_user_id
    ).order_by(NetWorthSnapshot.snapshot_date.desc()).all()
    
    return [
        NetWorthSnapshotResponse(
            id=str(snapshot.id),
            snapshot_date=snapshot.snapshot_date,
            total_assets=snapshot.total_assets,
            total_liabilities=snapshot.total_liabilities,
            net_worth=snapshot.net_worth,
            notes=snapshot.notes,
            created_at=snapshot.created_at.isoformat()
        )
        for snapshot in snapshots
    ]

@router.post("/", response_model=NetWorthSnapshotResponse)
async def create_net_worth_snapshot(
    snapshot: NetWorthSnapshotCreate,
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Create a new net worth snapshot"""
    net_worth = snapshot.total_assets - snapshot.total_liabilities
    
    db_snapshot = NetWorthSnapshot(
        user_id=current_user_id,
        snapshot_date=snapshot.snapshot_date,
        total_assets=snapshot.total_assets,
        total_liabilities=snapshot.total_liabilities,
        net_worth=net_worth,
        notes=snapshot.notes
    )
    
    db.add(db_snapshot)
    db.commit()
    db.refresh(db_snapshot)
    
    return NetWorthSnapshotResponse(
        id=str(db_snapshot.id),
        snapshot_date=db_snapshot.snapshot_date,
        total_assets=db_snapshot.total_assets,
        total_liabilities=db_snapshot.total_liabilities,
        net_worth=db_snapshot.net_worth,
        notes=db_snapshot.notes,
        created_at=db_snapshot.created_at.isoformat()
    )
