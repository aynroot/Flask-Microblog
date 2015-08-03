"""add password column to users

Revision ID: 52eaac95d35b
Revises: 2d9db72badd8
Create Date: 2015-08-04 00:03:17.259020

"""

# revision identifiers, used by Alembic.
revision = '52eaac95d35b'
down_revision = '2d9db72badd8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('password', sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column('users', 'password')
