"""empty message

Revision ID: 948da03336e0
Revises: 0aa1b9fd913a
Create Date: 2016-08-24 23:30:11.967399

"""

# revision identifiers, used by Alembic.
revision = '948da03336e0'
down_revision = '0aa1b9fd913a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fogbugzusercase', sa.Column('fhours_override', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('fogbugzusercase', sa.Column('frate_override', sa.Float(), nullable=False, server_default='0.0'))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fogbugzusercase', 'frate_override')
    op.drop_column('fogbugzusercase', 'fhours_override')
    ### end Alembic commands ###