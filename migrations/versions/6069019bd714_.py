"""empty message

Revision ID: 6069019bd714
Revises: d52a366882a6
Create Date: 2016-08-05 14:23:55.707492

"""

# revision identifiers, used by Alembic.
revision = '6069019bd714'
down_revision = 'd52a366882a6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fogbugzuser', sa.Column('sFullname', sa.String(length=255), nullable=False))
    op.drop_column('fogbugzuser', 'sPerson')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fogbugzuser', sa.Column('sPerson', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.drop_column('fogbugzuser', 'sFullname')
    ### end Alembic commands ###