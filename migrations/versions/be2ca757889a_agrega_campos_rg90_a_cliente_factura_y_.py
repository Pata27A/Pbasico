"""Agrega campos RG90 a Cliente, Factura y Cobranza

Revision ID: be2ca757889a
Revises: d5e619c8314a
Create Date: 2025-06-18 16:16:26.950003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be2ca757889a'
down_revision = 'd5e619c8314a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_identificacion', sa.String(length=2), nullable=True))

    with op.batch_alter_table('cobranzas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_cuenta_tarjeta', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('banco_financiera', sa.String(length=250), nullable=True))

    with op.batch_alter_table('facturas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tipo_comprobante', sa.String(length=3), nullable=False, server_default='109'))
        batch_op.add_column(sa.Column('monto_gravado', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('monto_exonerado', sa.Float(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('imputa_iva', sa.String(length=1), nullable=False, server_default='N'))
        batch_op.add_column(sa.Column('imputa_ire', sa.String(length=1), nullable=False, server_default='N'))
        batch_op.add_column(sa.Column('imputa_irp_rsp', sa.String(length=1), nullable=False, server_default='N'))
        batch_op.add_column(sa.Column('no_imputa', sa.String(length=1), nullable=False, server_default='N'))
        batch_op.add_column(sa.Column('numero_comprobante_asociado', sa.String(length=20), nullable=True))
        # No eliminar 'estado' aquí si no querés hacerlo


    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table('facturas', schema=None) as batch_op:
        batch_op.drop_column('numero_comprobante_asociado')
        batch_op.drop_column('no_imputa')
        batch_op.drop_column('imputa_irp_rsp')
        batch_op.drop_column('imputa_ire')
        batch_op.drop_column('imputa_iva')
        batch_op.drop_column('monto_exonerado')
        batch_op.drop_column('monto_gravado')
        batch_op.drop_column('tipo_comprobante')
        # No re-agregar 'estado' si no la eliminaste

    with op.batch_alter_table('cobranzas', schema=None) as batch_op:
        batch_op.drop_column('banco_financiera')
        batch_op.drop_column('numero_cuenta_tarjeta')

    with op.batch_alter_table('clientes', schema=None) as batch_op:
        batch_op.drop_column('tipo_identificacion')


    # ### end Alembic commands ###
