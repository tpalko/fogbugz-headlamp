"""2016-08-03 02:16:59.231019 add is_active to auth_user, drop status from auth_user

Revision ID: afa544c08c8b
Revises: None
Create Date: 2016-08-03 02:16:59.231019

"""

# revision identifiers, used by Alembic.
revision = 'afa544c08c8b'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auth_user', sa.Column('is_active', sa.Boolean(), nullable=False))
    op.drop_column('auth_user', 'status')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('auth_user', sa.Column('status', sa.SMALLINT(), autoincrement=False, nullable=False))
    op.drop_column('auth_user', 'is_active')
    ### end Alembic commands ###
