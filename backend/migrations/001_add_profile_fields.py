"""Add profile fields to User model

Revision ID: 001_add_profile_fields
Revises: 
Create Date: 2025-06-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_profile_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to users table
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('profile_picture_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('users', sa.Column('gender', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, default='UTC'))
    op.add_column('users', sa.Column('notification_email', sa.Boolean(), nullable=True, default=True))
    op.add_column('users', sa.Column('notification_quiz_reminders', sa.Boolean(), nullable=True, default=True))
    op.add_column('users', sa.Column('theme_preference', sa.String(length=20), nullable=True, default='light'))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('email_verification_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_token', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade():
    # Remove added columns
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'password_reset_expires')
    op.drop_column('users', 'password_reset_token')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'theme_preference')
    op.drop_column('users', 'notification_quiz_reminders')
    op.drop_column('users', 'notification_email')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'country')
    op.drop_column('users', 'gender')
    op.drop_column('users', 'date_of_birth')
    op.drop_column('users', 'profile_picture_url')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'phone')
