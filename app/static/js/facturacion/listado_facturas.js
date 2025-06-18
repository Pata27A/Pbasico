document.addEventListener('DOMContentLoaded', () => {
  const btnBuscar = document.getElementById('btnBuscar');

  btnBuscar.addEventListener('click', () => {
    const desde = document.getElementById('fecha_desde').value;
    const hasta = document.getElementById('fecha_hasta').value;

    fetch(`/facturas/api?desde=${desde}&hasta=${hasta}`)
      .then(res => res.json())
      .then(data => {
        const tbody = document.querySelector('#tablaFacturas tbody');
        tbody.innerHTML = '';
        if (data.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" class="text-center">No se encontraron facturas</td></tr>';
          return;
        }
        data.forEach(factura => {
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td>${factura.id}</td>
            <td>${factura.fecha}</td>
            <td>${factura.cliente || 'Consumidor Final'}</td>
            <td>Gs. ${factura.total.toLocaleString('es-PY')}</td>
            <td>
              <a href="/facturas/imprimir/${factura.id}" target="_blank" class="btn btn-sm btn-outline-primary">
                Ver ticket
              </a>
            </td>
          `;
          tbody.appendChild(tr);
        });
      })
      .catch(err => {
        console.error('Error al cargar facturas:', err);
      });
  });
});
