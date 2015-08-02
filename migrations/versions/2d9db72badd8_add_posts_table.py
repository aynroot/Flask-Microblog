"""add posts table

Revision ID: 2d9db72badd8
Revises: 14acf484b1f8
Create Date: 2015-08-02 22:11:54.638663

"""

# revision identifiers, used by Alembic.
revision = '2d9db72badd8'
down_revision = '14acf484b1f8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('posts',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('body', sa.String(length=140), nullable=True),
                    sa.Column('timestamp', sa.DateTime(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('posts')
