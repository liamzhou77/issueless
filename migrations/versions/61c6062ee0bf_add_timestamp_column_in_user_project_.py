"""Add timestamp column in user_project table

Revision ID: 61c6062ee0bf
Revises: c7db1b809c58
Create Date: 2020-06-04 21:49:52.894425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '61c6062ee0bf'
down_revision = 'c7db1b809c58'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_project', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.execute("UPDATE user_project SET timestamp = '2019-8-22';")
    op.alter_column('user_project', 'timestamp', nullable=False)
    op.create_index(
        op.f('ix_user_project_timestamp'), 'user_project', ['timestamp'], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_project_timestamp'), table_name='user_project')
    op.drop_column('user_project', 'timestamp')
    # ### end Alembic commands ###
