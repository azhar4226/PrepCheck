"""Add subject_id to users table

Revision ID: add_user_subject_id
Revises: c6bf334dca4e
Create Date: 2025-07-09 20:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_user_subject_id'
down_revision = 'c6bf334dca4e'
branch_labels = None
depends_on = None

def upgrade():
    # Add subject_id column to users table
    op.add_column('users', sa.Column('subject_id', sa.Integer(), nullable=True))
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_users_subject_id',
        'users', 'subjects',
        ['subject_id'], ['id']
    )

def downgrade():
    # Drop foreign key constraint
    op.drop_constraint('fk_users_subject_id', 'users', type_='foreignkey')
    
    # Drop subject_id column
    op.drop_column('users', 'subject_id')
