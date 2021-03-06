"""Add body_html column in 'Post'

Revision ID: 48db81755aab
Revises: 5a5d4af1b881
Create Date: 2018-01-06 12:59:40.359584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48db81755aab'
down_revision = '5a5d4af1b881'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    # ### end Alembic commands ###
