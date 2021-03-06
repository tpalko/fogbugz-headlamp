"""2016-08-05 13:58:39.384847 drop tables fogbugzusercase, case, fogbugzuserbug, bug

Revision ID: cdbf19d8c639
Revises: 95814f6dbb4d
Create Date: 2016-08-05 13:58:39.384847

"""

# revision identifiers, used by Alembic.
revision = 'cdbf19d8c639'
down_revision = '95814f6dbb4d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fogbugzusercase')
    op.drop_table('case')
    op.drop_table('fogbugzuserbug')
    op.drop_table('bug')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('bug',
    sa.Column('id', sa.INTEGER(), server_default=sa.text(u"nextval('bug_id_seq'::regclass)"), nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('ixBug', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ixFixFor', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('sBug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('ixPersonResolvedBy', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ixFixFor'], [u'milestone.ixFixFor'], name=u'bug_ixFixFor_fkey'),
    sa.ForeignKeyConstraint(['ixPersonResolvedBy'], [u'fogbugzuser.ixPerson'], name=u'bug_ixPersonResolvedBy_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'bug_pkey'),
    sa.UniqueConstraint('ixBug', name=u'bug_ixBug_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('fogbugzuserbug',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('ixPerson', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ixBug', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('fHours', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['ixBug'], [u'bug.ixBug'], name=u'fogbugzuserbug_ixBug_fkey'),
    sa.ForeignKeyConstraint(['ixPerson'], [u'fogbugzuser.ixPerson'], name=u'fogbugzuserbug_ixPerson_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'fogbugzuserbug_pkey')
    )
    op.create_table('fogbugzusercase',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('ixPerson', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ixBug', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('fHours', postgresql.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['ixBug'], [u'case.ixBug'], name=u'fogbugzusercase_ixBug_fkey'),
    sa.ForeignKeyConstraint(['ixPerson'], [u'fogbugzuser.ixPerson'], name=u'fogbugzusercase_ixPerson_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'fogbugzusercase_pkey')
    )
    op.create_table('case',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('date_created', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('date_modified', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('ixBug', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ixFixFor', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('sBug', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('ixPersonResolvedBy', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['ixFixFor'], [u'milestone.ixFixFor'], name=u'case_ixFixFor_fkey'),
    sa.ForeignKeyConstraint(['ixPersonResolvedBy'], [u'fogbugzuser.ixPerson'], name=u'case_ixPersonResolvedBy_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'case_pkey'),
    sa.UniqueConstraint('ixBug', name=u'case_ixBug_key')
    )
    ### end Alembic commands ###
