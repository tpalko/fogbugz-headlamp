"""empty message

Revision ID: d52a366882a6
Revises: 94c9eeb7d570
Create Date: 2016-08-05 14:19:25.234256

"""

# revision identifiers, used by Alembic.
revision = 'd52a366882a6'
down_revision = '94c9eeb7d570'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fbcase', sa.Column('sTitle', sa.String(length=255), nullable=False))
    op.drop_column('fbcase', 'sBug')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fbcase', sa.Column('sBug', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('fbcase', 'sTitle')
    ### end Alembic commands ###
