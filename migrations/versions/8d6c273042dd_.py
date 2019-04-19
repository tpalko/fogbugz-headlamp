"""2016-08-26 04:52:38.832470 add binvoice, bpaid, festimate to deliverable, drop milestone_id from deliverable, add deliverable_id to fbcase

Revision ID: 8d6c273042dd
Revises: a191fdf88f87
Create Date: 2016-08-26 04:52:38.832470

"""

# revision identifiers, used by Alembic.
revision = '8d6c273042dd'
down_revision = 'a191fdf88f87'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deliverable', sa.Column('binvoiced', sa.Boolean(), server_default='f', nullable=False))
    op.add_column('deliverable', sa.Column('bpaid', sa.Boolean(), server_default='f', nullable=False))
    op.add_column('deliverable', sa.Column('festimate', sa.Float(), server_default='0.0', nullable=False))
    op.drop_constraint(u'deliverable_milestone_id_fkey', 'deliverable', type_='foreignkey')
    op.drop_column('deliverable', 'milestone_id')
    op.add_column('fbcase', sa.Column('deliverable_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'fbcase', 'deliverable', ['deliverable_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'fbcase', type_='foreignkey')
    op.drop_column('fbcase', 'deliverable_id')
    op.add_column('deliverable', sa.Column('milestone_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key(u'deliverable_milestone_id_fkey', 'deliverable', 'milestone', ['milestone_id'], ['id'])
    op.drop_column('deliverable', 'festimate')
    op.drop_column('deliverable', 'bpaid')
    op.drop_column('deliverable', 'binvoiced')
    ### end Alembic commands ###
