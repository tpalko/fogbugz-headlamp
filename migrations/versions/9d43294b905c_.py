"""2016-11-05 01:04:44.434429 add invoice_id, refund_invoice_id to deliverable

Revision ID: 9d43294b905c
Revises: 66c9c7cb922e
Create Date: 2016-11-05 01:04:44.434429

"""

# revision identifiers, used by Alembic.
revision = '9d43294b905c'
down_revision = '66c9c7cb922e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deliverable', sa.Column('invoice_id', sa.Integer(), nullable=True))
    op.add_column('deliverable', sa.Column('refund_invoice_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'deliverable', 'invoice', ['refund_invoice_id'], ['id'])
    op.create_foreign_key(None, 'deliverable', 'invoice', ['invoice_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'deliverable', type_='foreignkey')
    op.drop_constraint(None, 'deliverable', type_='foreignkey')
    op.drop_column('deliverable', 'refund_invoice_id')
    op.drop_column('deliverable', 'invoice_id')
    ### end Alembic commands ###
