function guaranies(valor) {
    return new Intl.NumberFormat('es-PY', { style: 'currency', currency: 'PYG' }).format(valor);
}

async function buscarCaja() {
    const fecha = document.getElementById('fecha').value;
    if (!fecha) return alert('Debe seleccionar una fecha');

    const res = await fetch(`/reportes/caja/datos?fecha=${fecha}`);
    const data = await res.json();

    const resultado = document.getElementById('resultado');
    const sinCaja = document.getElementById('sinCaja');
    const tbody = document.querySelector('#tablaMovimientos tbody');

    if (!data.success) {
        alert(data.error || 'Error al obtener datos');
        return;
    }

    if (!data.caja) {
        resultado.style.display = 'none';
        sinCaja.style.display = 'block';
        return;
    }

    sinCaja.style.display = 'none';
    resultado.style.display = 'block';

    document.getElementById('cajaFecha').textContent = data.caja.fecha;
    document.getElementById('cajaApertura').textContent = guaranies(data.caja.monto_apertura);
    document.getElementById('cajaSaldo').textContent = guaranies(data.caja.saldo_final);

    tbody.innerHTML = '';
    for (let mov of data.movimientos) {
        let fila = `<tr>
            <td>${mov.fecha}</td>
            <td>${mov.tipo}</td>
            <td>${guaranies(mov.monto)}</td>
            <td>${mov.descripcion}</td>
        </tr>`;
        tbody.innerHTML += fila;
    }
}

function exportarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    doc.text("Reporte de Caja", 10, 10);

    const fecha = document.getElementById('cajaFecha').textContent;
    const apertura = document.getElementById('cajaApertura').textContent;
    const saldo = document.getElementById('cajaSaldo').textContent;

    doc.text(`Fecha: ${fecha}`, 10, 20);
    doc.text(`Monto Apertura: ${apertura}`, 10, 30);
    doc.text(`Saldo Final: ${saldo}`, 10, 40);

    const rows = [];
    document.querySelectorAll('#tablaMovimientos tbody tr').forEach(tr => {
        const cells = tr.querySelectorAll('td');
        rows.push(Array.from(cells).map(td => td.textContent));
    });

    doc.autoTable({
        startY: 50,
        head: [['Fecha', 'Tipo', 'Monto', 'Descripción']],
        body: rows
    });

    doc.save(`reporte_caja_${fecha}.pdf`);
}
