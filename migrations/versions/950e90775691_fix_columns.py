"""fix columns

Revision ID: 950e90775691
Revises: a4fc52c2c575
Create Date: 2018-09-01 09:23:04.237277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '950e90775691'
down_revision = 'a4fc52c2c575'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Customers', ['email', 'phone'])
    op.add_column('Orders', sa.Column('schedule_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Orders', 'Schedules', ['schedule_id'], ['id'])
    op.alter_column('SCHDetails', 'schedule_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'SCHDetails', 'Schedules', ['schedule_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'SCHDetails', type_='foreignkey')
    op.alter_column('SCHDetails', 'schedule_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_constraint(None, 'Orders', type_='foreignkey')
    op.drop_column('Orders', 'schedule_id')
    op.drop_constraint(None, 'Customers', type_='unique')
    # ### end Alembic commands ###