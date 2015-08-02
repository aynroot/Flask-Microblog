"""initial

Revision ID: 14acf484b1f8
Revises: None
Create Date: 2015-08-02 21:05:23.368356

"""

# revision identifiers, used by Alembic.
revision = '14acf484b1f8'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('nickname', sa.String(length=64), nullable=True),
                    sa.Column('email', sa.String(length=120), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_nickname'), 'users', ['nickname'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_users_nickname'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
