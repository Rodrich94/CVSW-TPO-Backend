"""Se agregan diagrama, licencia, cupo al modelo de base de datos

Revision ID: ffdddb4811dc
Revises: a7bba6ab880f
Create Date: 2024-09-18 14:21:50.841275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffdddb4811dc'
down_revision = 'a7bba6ab880f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diagramas_mensuales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_ini', sa.Date(), nullable=False),
    sa.Column('fecha_fin', sa.Date(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('id_servicio', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['id_servicio'], ['servicios.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cupos_mensuales',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_ini', sa.Date(), nullable=False),
    sa.Column('fecha_fin', sa.Date(), nullable=False),
    sa.Column('total', sa.Double(), nullable=False),
    sa.Column('remanente', sa.Double(), nullable=False),
    sa.Column('id_servicio', sa.Integer(), nullable=False),
    sa.Column('legajo_autorizante', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['id_servicio'], ['servicios.id'], ),
    sa.ForeignKeyConstraint(['legajo_autorizante'], ['empleados.legajo'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('licencias',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('fecha_desde', sa.Date(), nullable=False),
    sa.Column('fecha_hasta', sa.Date(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('legajo_empleado', sa.String(length=20), nullable=False),
    sa.Column('legajo_autorizante', sa.String(length=20), nullable=False),
    sa.ForeignKeyConstraint(['legajo_autorizante'], ['empleados.legajo'], ),
    sa.ForeignKeyConstraint(['legajo_empleado'], ['empleados.legajo'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('licencias')
    op.drop_table('cupos_mensuales')
    op.drop_table('diagramas_mensuales')
    # ### end Alembic commands ###