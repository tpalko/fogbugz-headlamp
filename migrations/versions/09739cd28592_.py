"""2016-08-05 14:53:46.416861 add sproject to project, drop sProject from project

Revision ID: 09739cd28592
Revises: 5c8ad242f237
Create Date: 2016-08-05 14:53:46.416861

"""

# revision identifiers, used by Alembic.
revision = '09739cd28592'
down_revision = '5c8ad242f237'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('sproject', sa.String(length=255), nullable=True))
    op.drop_column('project', 'sProject')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('project', sa.Column('sProject', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.drop_column('project', 'sproject')
    ### end Alembic commands ###
