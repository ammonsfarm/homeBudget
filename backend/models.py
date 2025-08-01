from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Text, ForeignKey, ARRAY
from sqlalchemy.types import DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    # SimpleFIN integration
    simplefin_access_url = Column(Text)  # Store SimpleFIN access URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    budget_categories = relationship("BudgetCategory", back_populates="user", cascade="all, delete-orphan")
    budget_periods = relationship("BudgetPeriod", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    net_worth_snapshots = relationship("NetWorthSnapshot", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit_card, investment, etc.
    balance = Column(DECIMAL(15, 2), default=0.00)
    currency = Column(String(3), default="USD")
    # SimpleFIN integration fields
    external_id = Column(String(255))  # SimpleFIN account ID
    institution = Column(String(255))  # Bank/institution name
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class BudgetCategory(Base):
    __tablename__ = "budget_categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey("budget_categories.id"))
    color = Column(String(7))  # hex color code
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budget_categories")
    parent_category = relationship("BudgetCategory", remote_side=[id])
    budget_items = relationship("BudgetItem", back_populates="category", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="category")

class BudgetPeriod(Base):
    __tablename__ = "budget_periods"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="budget_periods")
    budget_items = relationship("BudgetItem", back_populates="budget_period", cascade="all, delete-orphan")

class BudgetItem(Base):
    __tablename__ = "budget_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_period_id = Column(UUID(as_uuid=True), ForeignKey("budget_periods.id"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("budget_categories.id"), nullable=False)
    allocated_amount = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    rollover_from_previous = Column(DECIMAL(15, 2), default=0.00)
    rollover_enabled = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    budget_period = relationship("BudgetPeriod", back_populates="budget_items")
    category = relationship("BudgetCategory", back_populates="budget_items")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Add user_id for easier queries
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)  # Simplified to single date field
    category_id = Column(UUID(as_uuid=True), ForeignKey("budget_categories.id"))
    # SimpleFIN integration fields
    external_id = Column(String(255))  # SimpleFIN transaction ID
    pending = Column(Boolean, default=False)  # Is transaction pending
    source = Column(String(50), default='manual')  # 'manual' or 'simplefin'
    # Other fields
    is_split = Column(Boolean, default=False)
    parent_transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"))
    memo = Column(Text)
    payee = Column(String(255))
    is_reconciled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("BudgetCategory", back_populates="transactions")
    parent_transaction = relationship("Transaction", remote_side=[id])

class NetWorthSnapshot(Base):
    __tablename__ = "net_worth_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    total_assets = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    total_liabilities = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    net_worth = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="net_worth_snapshots")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    document_type = Column(String(100))  # will, insurance, bank_statement, etc.
    file_path = Column(String(500))
    encrypted_key = Column(Text)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    tags = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="documents")
