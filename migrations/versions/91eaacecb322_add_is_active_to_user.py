"""Add is_active to user

Revision ID: 91eaacecb322
Revises: 095badf57331
Create Date: 2025-12-08 13:31:16.712536

"""
from alembic import op
import sqlalchemy as sa
revision = '91eaacecb322'
down_revision = '095badf57331'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('is_active', sa.Boolean(), nullable=False))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('is_active')
