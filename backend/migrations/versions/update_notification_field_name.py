"""Update notification field name from quiz_reminders to test_reminders

Revision ID: update_notification_field
Revises: 
Create Date: 2025-07-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'update_notification_field'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Update notification field name from quiz to test"""
    # Check if the old column exists before renaming
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'notification_quiz_reminders' in columns and 'notification_test_reminders' not in columns:
        # Rename the column
        op.alter_column('users', 'notification_quiz_reminders', new_column_name='notification_test_reminders')
        print("✅ Renamed notification_quiz_reminders to notification_test_reminders")
    elif 'notification_test_reminders' in columns:
        print("✅ notification_test_reminders already exists")
    else:
        # Create the new column if neither exists
        op.add_column('users', sa.Column('notification_test_reminders', sa.Boolean(), nullable=True, default=True))
        print("✅ Created notification_test_reminders column")


def downgrade():
    """Revert notification field name from test to quiz"""
    # Check if the new column exists before renaming back
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'notification_test_reminders' in columns:
        # Rename back to original
        op.alter_column('users', 'notification_test_reminders', new_column_name='notification_quiz_reminders')
        print("✅ Reverted notification_test_reminders to notification_quiz_reminders")
