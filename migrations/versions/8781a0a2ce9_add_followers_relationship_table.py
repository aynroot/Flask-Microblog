"""add followers relationship table

Revision ID: 8781a0a2ce9
Revises: 52eaac95d35b
Create Date: 2015-08-06 23:14:36.587854

"""

# revision identifiers, used by Alembic.
revision = '8781a0a2ce9'
down_revision = '52eaac95d35b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('followers',
        sa.Column('follower_id', sa.Integer(), nullable=True),
        sa.Column('followed_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], )
    )


def downgrade():
    op.drop_table('followers')
