"""empty message

Revision ID: ed1d86e63c59
Revises: 445fb3758c9c
Create Date: 2016-08-21 03:55:33.237109

"""

# revision identifiers, used by Alembic.
revision = 'ed1d86e63c59'
down_revision = '445fb3758c9c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fbcase', sa.Column('scategory', sa.String(length=255), nullable=False))
    op.add_column('fbcase', sa.Column('sticket', sa.String(length=255), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fbcase', 'sticket')
    op.drop_column('fbcase', 'scategory')
    ### end Alembic commands ###
