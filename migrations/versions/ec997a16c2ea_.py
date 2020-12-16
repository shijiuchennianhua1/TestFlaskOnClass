"""empty message

Revision ID: ec997a16c2ea
Revises: 8b0851da8555
Create Date: 2020-12-06 21:43:20.021208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec997a16c2ea'
down_revision = '8b0851da8555'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tools', sa.Column('introduction', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tools', 'introduction')
    # ### end Alembic commands ###
