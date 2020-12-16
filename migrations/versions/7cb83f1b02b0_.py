"""empty message

Revision ID: 7cb83f1b02b0
Revises: d8e5d9fecbaa
Create Date: 2020-12-06 20:25:27.956564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7cb83f1b02b0'
down_revision = 'd8e5d9fecbaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tools',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('contents', sa.Text(), nullable=True),
    sa.Column('file_name', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tools_file_name'), 'tools', ['file_name'], unique=False)
    op.create_index(op.f('ix_tools_user_id'), 'tools', ['user_id'], unique=False)
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tool_id', sa.Integer(), nullable=True),
    sa.Column('contents', sa.Text(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['tool_id'], ['tools.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comment_tool_id'), 'comment', ['tool_id'], unique=False)
    op.create_index(op.f('ix_comment_user_id'), 'comment', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comment_user_id'), table_name='comment')
    op.drop_index(op.f('ix_comment_tool_id'), table_name='comment')
    op.drop_table('comment')
    op.drop_index(op.f('ix_tools_user_id'), table_name='tools')
    op.drop_index(op.f('ix_tools_file_name'), table_name='tools')
    op.drop_table('tools')
    # ### end Alembic commands ###