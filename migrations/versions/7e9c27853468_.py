"""2016-08-03 02:22:06.150485 drop role from auth_user

Revision ID: 7e9c27853468
Revises: afa544c08c8b
Create Date: 2016-08-03 02:22:06.150485

"""

# revision identifiers, used by Alembic.
revision = '7e9c27853468'
down_revision = 'afa544c08c8b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('auth_user', 'role')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auth_user', sa.Column('role', sa.SMALLINT(), autoincrement=False, nullable=False))
    ### end Alembic commands ###
