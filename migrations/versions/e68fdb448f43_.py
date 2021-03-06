"""2018-12-19 00:38:21.713141 set fbcase.sticket nullable

Revision ID: e68fdb448f43
Revises: 09f561c71104
Create Date: 2018-12-19 00:38:21.713141

"""

# revision identifiers, used by Alembic.
revision = 'e68fdb448f43'
down_revision = 'efd77954d15d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('fbcase', 'sticket',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('fbcase', 'sticket',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    ### end Alembic commands ###
