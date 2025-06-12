let chart = null;

function formatearNumero(num) {
  return num.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("btnConsultar").addEventListener("click", cargarReporte);
  document.getElementById("btnExportar").addEventListener("click", exportarCSV);

  document.querySelectorAll(".filtro").forEach(btn => {
    btn.addEventListener("click", () => aplicarFiltro(btn.dataset.filtro));
  });
});

async function cargarReporte() {
  const desde = document.getElementById("fecha_desde").value;
  const hasta = document.getElementById("fecha_hasta").value;

  if (!desde || !hasta) {
    alert("Debes seleccionar ambas fechas.");
    return;
  }

  try {
    const res = await fetch(`/reportes/ganancia/datos?desde=${desde}&hasta=${hasta}`);
    const data = await res.json();

    if (data.success) {
      const fila = `<tr>
        <td>${formatearNumero(data.ingresos)}</td>
        <td>${formatearNumero(data.egresos)}</td>
        <td>${formatearNumero(data.ganancia)}</td>
      </tr>`;
      document.getElementById("tablaReporte").innerHTML = fila;
      renderGrafico(data);
    } else {
      alert(data.error);
    }
  } catch (err) {
    console.error("Error al cargar reporte:", err);
    alert("Error al cargar reporte.");
  }
}

function renderGrafico(data) {
  const ctx = document.getElementById('graficoGanancia').getContext('2d');
  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Ingresos', 'Egresos', 'Ganancia Neta'],
      datasets: [{
        label: 'Monto',
        data: [data.ingresos, data.egresos, data.ganancia],
        backgroundColor: ['#28a745', '#dc3545', '#007bff']
      }]
    },
    options: {
      scales: {
        y: {
          ticks: {
            callback: function(value) {
              return formatearNumero(value);
            }
          }
        }
      }
    }
  });
}

function exportarCSV() {
  const filas = document.querySelectorAll("#tablaReporte tr");
  let csv = "Ingresos,Egresos,Ganancia Neta\n";

  filas.forEach(tr => {
    const cols = tr.querySelectorAll("td");
    if (cols.length === 3) {
      // Para el CSV mejor dejamos números sin formato para evitar problemas al importar
      csv += `${cols[0].innerText.replace(/\./g, '')},${cols[1].innerText.replace(/\./g, '')},${cols[2].innerText.replace(/\./g, '')}\n`;
    }
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "reporte_ganancia.csv";
  a.click();
  URL.revokeObjectURL(url);
}

function aplicarFiltro(filtro) {
  const hoy = new Date();
  let desde, hasta;

  if (filtro === 'hoy') {
    desde = hasta = hoy.toISOString().split('T')[0];
  } else if (filtro === 'semana') {
    const primerDia = new Date(hoy);
    primerDia.setDate(hoy.getDate() - hoy.getDay() + 1);
    const ultimoDia = new Date(primerDia);
    ultimoDia.setDate(primerDia.getDate() + 6);
    desde = primerDia.toISOString().split('T')[0];
    hasta = ultimoDia.toISOString().split('T')[0];
  } else if (filtro === 'mes') {
    desde = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01`;
    hasta = `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-31`;
  }

  document.getElementById("fecha_desde").value = desde;
  document.getElementById("fecha_hasta").value = hasta;

  cargarReporte();
}
