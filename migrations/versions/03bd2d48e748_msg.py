"""msg

Revision ID: 03bd2d48e748
Revises: 
Create Date: 2020-01-31 23:27:30.099751

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03bd2d48e748'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('lastname', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('property',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('area', sa.Integer(), nullable=False),
    sa.Column('bedroom', sa.Integer(), nullable=False),
    sa.Column('parking', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('star', sa.Boolean(), nullable=False),
    sa.Column('locality', sa.String(), nullable=False),
    sa.Column('lat', sa.Float(), nullable=True),
    sa.Column('long', sa.Float(), nullable=True),
    sa.Column('images_count', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookmarked',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('comment', sa.Text(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('property_pic',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('path', sa.String(), nullable=False),
    sa.Column('property_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['property.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('property_pic')
    op.drop_table('comment')
    op.drop_table('bookmarked')
    op.drop_table('property')
    op.drop_table('users')
    # ### end Alembic commands ###
