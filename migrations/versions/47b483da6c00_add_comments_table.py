"""Add comments table

Revision ID: 47b483da6c00
Revises: 17f8d20c0242
Create Date: 2020-07-16 02:21:35.849175

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47b483da6c00'
down_revision = '17f8d20c0242'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=10000), nullable=False),
        sa.Column('timestamp', sa.Float(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issues.id'],),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'],),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_comments_timestamp'), 'comments', ['timestamp'], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comments_timestamp'), table_name='comments')
    op.drop_table('comments')
    # ### end Alembic commands ###
