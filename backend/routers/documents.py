from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import Document

router = APIRouter()

# Pydantic models
class DocumentResponse(BaseModel):
    id: str
    name: str
    document_type: Optional[str]
    file_size: Optional[int]
    mime_type: Optional[str]
    tags: Optional[List[str]]
    created_at: str

@router.get("/", response_model=List[DocumentResponse])
async def get_documents(
    current_user_id: str = Depends(lambda: "placeholder"),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(
        Document.user_id == current_user_id
    ).order_by(Document.created_at.desc()).all()
    
    return [
        DocumentResponse(
            id=str(doc.id),
            name=doc.name,
            document_type=doc.document_type,
            file_size=doc.file_size,
            mime_type=doc.mime_type,
            tags=doc.tags,
            created_at=doc.created_at.isoformat()
        )
        for doc in documents
    ]
