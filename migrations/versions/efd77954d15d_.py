"""2018-11-20 02:51:53.438522 add status to fogbugzusercase

Revision ID: efd77954d15d
Revises: c50c43ab21bc
Create Date: 2018-11-20 02:51:53.438522

"""

# revision identifiers, used by Alembic.
revision = 'efd77954d15d'
down_revision = 'c50c43ab21bc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fogbugzusercase', sa.Column('status', sa.String(length=255), nullable=False, server_default='Unset'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fogbugzusercase', 'status')
    ### end Alembic commands ###
