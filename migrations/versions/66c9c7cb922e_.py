"""2016-11-05 00:46:51.796498 add frefunded to deliverable

Revision ID: 66c9c7cb922e
Revises: b123e8aba1a1
Create Date: 2016-11-05 00:46:51.796498

"""

# revision identifiers, used by Alembic.
revision = '66c9c7cb922e'
down_revision = 'b123e8aba1a1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('deliverable', sa.Column('frefunded', sa.Float(), server_default='0.0', nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('deliverable', 'frefunded')
    ### end Alembic commands ###
