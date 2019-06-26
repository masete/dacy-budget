"""empty message

Revision ID: de05d767cbe2
Revises: f0526fb51dc9
Create Date: 2019-06-26 22:19:45.875478

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de05d767cbe2'
down_revision = 'f0526fb51dc9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('transaction',
    sa.Column('id', sa.String(length=32), nullable=False),
    sa.Column('account', sa.String(length=80), nullable=False),
    sa.Column('date', sa.DateTime(), nullable=False),
    sa.Column('narration', sa.String(length=120), nullable=False),
    sa.Column('debit', sa.Float(), nullable=True),
    sa.Column('credit', sa.Float(), nullable=True),
    sa.Column('balance', sa.Float(), nullable=True),
    sa.Column('added_date', sa.DateTime(), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('sub_category', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('transaction')
    # ### end Alembic commands ###
