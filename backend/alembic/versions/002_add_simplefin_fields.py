"""Add SimpleFIN integration fields

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add SimpleFIN access URL to users table
    op.add_column('users', sa.Column('simplefin_access_url', sa.Text(), nullable=True))
    
    # Update accounts table for SimpleFIN integration
    op.add_column('accounts', sa.Column('external_id', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('institution', sa.String(length=255), nullable=True))
    
    # Drop old SimpleFIN field if it exists
    try:
        op.drop_column('accounts', 'simplefin_account_id')
    except:
        pass  # Column might not exist
    
    # Update transactions table for SimpleFIN integration
    op.add_column('transactions', sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('transactions', sa.Column('external_id', sa.String(length=255), nullable=True))
    op.add_column('transactions', sa.Column('pending', sa.Boolean(), nullable=True))
    op.add_column('transactions', sa.Column('source', sa.String(length=50), nullable=True))
    
    # Rename transaction_date to date for simplicity
    try:
        op.alter_column('transactions', 'transaction_date', new_column_name='date')
    except:
        pass  # Column might already be renamed
    
    # Drop posted_date and simplefin_transaction_id if they exist
    try:
        op.drop_column('transactions', 'posted_date')
    except:
        pass
    
    try:
        op.drop_column('transactions', 'simplefin_transaction_id')
    except:
        pass
    
    # Add foreign key constraint for user_id in transactions
    op.create_foreign_key(
        'fk_transactions_user_id',
        'transactions', 'users',
        ['user_id'], ['id']
    )
    
    # Set default values for new columns
    op.execute("UPDATE transactions SET pending = false WHERE pending IS NULL")
    op.execute("UPDATE transactions SET source = 'manual' WHERE source IS NULL")
    
    # Make user_id not nullable after setting values
    op.execute("UPDATE transactions SET user_id = (SELECT user_id FROM accounts WHERE accounts.id = transactions.account_id) WHERE user_id IS NULL")
    op.alter_column('transactions', 'user_id', nullable=False)
    op.alter_column('transactions', 'pending', nullable=False)
    op.alter_column('transactions', 'source', nullable=False)


def downgrade() -> None:
    # Remove SimpleFIN fields from users
    op.drop_column('users', 'simplefin_access_url')
    
    # Remove SimpleFIN fields from accounts
    op.drop_column('accounts', 'external_id')
    op.drop_column('accounts', 'institution')
    
    # Remove SimpleFIN fields from transactions
    op.drop_constraint('fk_transactions_user_id', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'user_id')
    op.drop_column('transactions', 'external_id')
    op.drop_column('transactions', 'pending')
    op.drop_column('transactions', 'source')
    
    # Rename date back to transaction_date
    try:
        op.alter_column('transactions', 'date', new_column_name='transaction_date')
    except:
        pass
    
    # Add back old columns
    op.add_column('accounts', sa.Column('simplefin_account_id', sa.String(length=255), nullable=True))
    op.add_column('transactions', sa.Column('posted_date', sa.Date(), nullable=True))
    op.add_column('transactions', sa.Column('simplefin_transaction_id', sa.String(length=255), nullable=True))
