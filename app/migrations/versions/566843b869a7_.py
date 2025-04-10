"""empty message

Revision ID: 566843b869a7
Revises: df9ea93d06cc
Create Date: 2025-04-10 21:06:45.803060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '566843b869a7'
down_revision: Union[str, None] = 'df9ea93d06cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('product_properties', 'value_int')
    op.drop_column('product_properties', 'value_str')
    op.drop_column('product_properties', 'value_uid')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('product_properties', sa.Column('value_uid', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('product_properties', sa.Column('value_str', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('product_properties', sa.Column('value_int', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
