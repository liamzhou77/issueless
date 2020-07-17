"""Make priority column and assignee_id column in issues table be nullable

Revision ID: 25fc3a09eb5c
Revises: 3894db5800cb
Create Date: 2020-06-30 22:59:05.060405

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25fc3a09eb5c'
down_revision = '3894db5800cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('issues', 'assignee_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        'issues', 'priority', existing_type=sa.VARCHAR(length=6), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        'issues', 'priority', existing_type=sa.VARCHAR(length=6), nullable=False
    )
    op.alter_column('issues', 'assignee_id', existing_type=sa.INTEGER(), nullable=False)
    # ### end Alembic commands ###