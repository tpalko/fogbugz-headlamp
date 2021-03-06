"""2016-08-21 03:31:07.005081 add category_id to fbcase

Revision ID: 445fb3758c9c
Revises: 88dcd9df2c53
Create Date: 2016-08-21 03:31:07.005081

"""

# revision identifiers, used by Alembic.
revision = '445fb3758c9c'
down_revision = '88dcd9df2c53'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fbcase', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'fbcase', 'category', ['category_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'fbcase', type_='foreignkey')
    op.drop_column('fbcase', 'category_id')
    ### end Alembic commands ###
