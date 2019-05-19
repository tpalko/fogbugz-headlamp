"""2018-11-18 19:23:27.249708 drop status, ixperson from fogbugzusercase

Revision ID: d7497deb5f0f
Revises: 57c76677278c
Create Date: 2018-11-18 19:23:27.249708

"""

# revision identifiers, used by Alembic.
revision = 'd7497deb5f0f'
down_revision = '57c76677278c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'fogbugzusercase_ixperson_fkey', 'fogbugzusercase', type_='foreignkey')
    op.drop_column('fogbugzusercase', 'status')
    op.drop_column('fogbugzusercase', 'ixperson')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fogbugzusercase', sa.Column('ixperson', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('fogbugzusercase', sa.Column('status', sa.VARCHAR(length=20), server_default=sa.text(u"'Unset'::character varying"), autoincrement=False, nullable=False))
    op.create_foreign_key(u'fogbugzusercase_ixperson_fkey', 'fogbugzusercase', 'fogbugzuser', ['ixperson'], ['ixperson'])
    ### end Alembic commands ###