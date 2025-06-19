from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer

# Para identificar que es una migración automática
revision = 'factura_format_set'
down_revision = 'be2ca757889a'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()

    # Selecciona todas las facturas ordenadas por ID ascendente (más antigua primero)
    facturas = connection.execute(
        sa.text("SELECT id FROM facturas ORDER BY id ASC")
    ).fetchall()

    # Asignar nuevo número en formato 001-001-0000001
    for index, factura in enumerate(facturas, start=1):
        nuevo_numero = f"001-001-{index:07d}"
        connection.execute(
            sa.text("UPDATE facturas SET numero = :nuevo_numero WHERE id = :factura_id"),
            {"nuevo_numero": nuevo_numero, "factura_id": factura.id}
        )

def downgrade():
    # Esta reversión es destructiva. No hay forma fácil de recuperar los números viejos originales.
    pass


