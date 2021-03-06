"""Remove user_projects table's timestamp column and change indexes

Revision ID: 7d5bf549ec5b
Revises: 812ebd486003
Create Date: 2020-06-28 22:59:43.534812

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7d5bf549ec5b'
down_revision = '812ebd486003'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('timestamp', 'notifications', ['is_read'], unique=False)
    op.drop_index('ix_user_project_timestamp', table_name='user_project')
    op.drop_column('user_project', 'timestamp')
    op.create_index('full_name', 'users', ['first_name', 'last_name'], unique=False)
    op.drop_index('user_name', table_name='users')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('user_name', 'users', ['first_name', 'last_name'], unique=False)
    op.drop_index('full_name', table_name='users')
    op.add_column(
        'user_project',
        sa.Column(
            'timestamp', postgresql.TIMESTAMP(), autoincrement=False, nullable=False
        ),
    )
    op.create_index(
        'ix_user_project_timestamp', 'user_project', ['timestamp'], unique=False
    )
    op.drop_index('timestamp', table_name='notifications')
    # ### end Alembic commands ###
