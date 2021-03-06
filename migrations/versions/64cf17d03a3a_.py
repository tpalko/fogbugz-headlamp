"""2016-08-05 11:00:23.502195 add ixPerson to fogbugzuser, ixFixFor to milestone

Revision ID: 64cf17d03a3a
Revises: f573d87520f3
Create Date: 2016-08-05 11:00:23.502195

"""

# revision identifiers, used by Alembic.
revision = '64cf17d03a3a'
down_revision = 'f573d87520f3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'fogbugzuser', ['ixPerson'])
    op.create_unique_constraint(None, 'milestone', ['ixFixFor'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'milestone', type_='unique')
    op.drop_constraint(None, 'fogbugzuser', type_='unique')
    ### end Alembic commands ###
