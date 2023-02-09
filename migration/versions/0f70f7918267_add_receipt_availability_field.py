"""add receipt availability field

Revision ID: 0f70f7918267
Revises: 076b5298863f
Create Date: 2023-02-06 15:17:04.535232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f70f7918267'
down_revision = '076b5298863f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('item', sa.Column(
        'receipt_availability', sa.Boolean(), nullable=True))
    op.execute("update item set receipt_availability = false")
    op.alter_column('item', 'receipt_availability', nullable=False)


def downgrade() -> None:
    op.drop_column('item', 'receipt_availability')
