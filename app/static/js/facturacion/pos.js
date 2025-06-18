let productos = [];
let clienteSeleccionado = null;
let cantidadPendiente = null;
let pagos = [];
let enviandoFactura = false; // Flag para evitar doble envío

// Formatea números como guaraníes con puntos de miles
function formatearGuaranies(numero) {
  return numero.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
}

document.addEventListener("DOMContentLoaded", () => {

  // Búsqueda de producto por código o nombre al presionar Enter
  const buscadorProducto = document.getElementById("buscadorProducto");
  if (buscadorProducto) {
    buscadorProducto.addEventListener("keypress", async (e) => {
      if (e.key !== "Enter") return;
      e.preventDefault();

      const texto = e.target.value.trim();
      if (!texto) return;

      if (/^\+\d+$/.test(texto)) {
        cantidadPendiente = parseInt(texto.slice(1), 10);
        e.target.value = "";
        return;
      }

      const cantidad = cantidadPendiente || 1;
      cantidadPendiente = null;

      try {
        const res = await fetch(`/facturacion/api/buscar_producto?codigo=${encodeURIComponent(texto)}`);
        const data = await res.json();

        if (data && data.codigo) {
          agregarProducto(data, cantidad);
          e.target.value = "";
        } else {
          alert("Producto no encontrado.");
        }
      } catch (err) {
        alert("Error al buscar producto.");
        console.error(err);
      }
    });
  }

  // --- Cliente ---
  const buscadorCliente = document.getElementById("buscadorCliente");
  if (buscadorCliente) {
    buscadorCliente.addEventListener("input", async function () {
      const q = this.value.trim();
      const lista = document.getElementById("resultadoClientes");
      if (!lista) return;
      lista.innerHTML = "";

      if (q.length < 2) return;

      try {
        const res = await fetch(`/api/clientes/buscar?q=${encodeURIComponent(q)}`);
        const data = await res.json();

        if (!data.length) {
          lista.innerHTML = '<li class="list-group-item text-muted">Sin resultados</li>';
          return;
        }

        data.forEach(cliente => {
          const li = document.createElement("li");
          li.className = "list-group-item list-group-item-action";
          li.textContent = `${cliente.nombre} (${cliente.documento})`;
          li.onclick = () => seleccionarCliente(cliente);
          lista.appendChild(li);
        });
      } catch (err) {
        console.error("Error al buscar cliente", err);
      }
    });
  }

  // --- Cobro ---
  const pagoMontoInput = document.getElementById("pago_monto");
  const pagoMetodoSelect = document.getElementById("pago_metodo");
  const pagoDescripcionInput = document.getElementById("pago_descripcion");
  if (pagoMontoInput) pagoMontoInput.addEventListener("input", calcularVuelto);
  if (pagoMetodoSelect) pagoMetodoSelect.addEventListener("change", calcularVuelto);
  if (pagoDescripcionInput) pagoDescripcionInput.addEventListener("input", calcularVuelto);

  const agregarPagoBtn = document.getElementById("agregarPago");
  if (agregarPagoBtn) agregarPagoBtn.addEventListener("click", agregarPago);

  // Envío del formulario cobro
  const formCobro = document.getElementById("formCobro");
  if (formCobro) {
    formCobro.addEventListener("submit", async function (e) {
      e.preventDefault();

      if (enviandoFactura) return; // Evita doble envío
      enviandoFactura = true;

      const btnEnviar = e.target.querySelector('button[type="submit"]');
      if (btnEnviar) btnEnviar.disabled = true;

      const total = parseFloat(document.getElementById("cobro_total").value) || 0;
      const pagado = pagos.reduce((acc, p) => acc + p.monto, 0);

      if (pagado < total) {
        alert("El monto pagado no cubre el total.");
        enviandoFactura = false;
        if (btnEnviar) btnEnviar.disabled = false;
        return;
      }

      try {
        await finalizarFactura();
      } finally {
        enviandoFactura = false;
        if (btnEnviar) btnEnviar.disabled = false;
      }
    });
  } else {
    console.warn("No se encontró el formulario con id 'formCobro'");
  }

  // Atajos de teclado para abrir modales (F5 para cliente, F6 para cobro)
  document.addEventListener("keydown", (e) => {
    if (e.code === "F5") {
      e.preventDefault();
      abrirModalCliente();
    } else if (e.code === "F6") {
      e.preventDefault();
      abrirModalCobro();
    }
  });
}); // fin DOMContentLoaded

// Funciones independientes que no dependen de DOM al cargar

function agregarProducto(producto, cantidad) {
  const existente = productos.find(p => p.codigo === producto.codigo);
  if (existente) {
    existente.cantidad += cantidad;
  } else {
    productos.push({
      codigo: producto.codigo,
      nombre: producto.nombre,
      precio: producto.precio,
      cantidad: cantidad
    });
  }
  renderTabla();
}

function renderTabla() {
  const tbody = document.getElementById("tablaProductos");
  if (!tbody) return;
  tbody.innerHTML = "";
  let total = 0;

  productos.forEach((p, index) => {
    const subtotal = p.precio * p.cantidad;
    total += subtotal;

    tbody.innerHTML += `
      <tr>
        <td>${p.codigo}</td>
        <td>${p.nombre}</td>
        <td>${p.cantidad}</td>
        <td>${formatearGuaranies(p.precio.toFixed(0))}</td>
        <td>${formatearGuaranies(subtotal.toFixed(0))}</td>
        <td><button class="btn btn-sm btn-danger" onclick="eliminarProducto(${index})">X</button></td>
      </tr>
    `;
  });

  const totalFactura = document.getElementById("totalFactura");
  const totalACobrar = document.getElementById("total_a_cobrar");
  const cobroTotal = document.getElementById("cobro_total");

  if (totalFactura) totalFactura.innerText = formatearGuaranies(total.toFixed(0));
  if (totalACobrar) totalACobrar.innerText = formatearGuaranies(total.toFixed(0));
  if (cobroTotal) cobroTotal.value = total.toFixed(0);
}

function eliminarProducto(index) {
  productos.splice(index, 1);
  renderTabla();
}

function abrirModalCliente() {
  const modal = new bootstrap.Modal(document.getElementById("modalCliente"));
  modal.show();
  const buscadorCliente = document.getElementById("buscadorCliente");
  if (buscadorCliente) buscadorCliente.value = "";
  const resultadoClientes = document.getElementById("resultadoClientes");
  if (resultadoClientes) resultadoClientes.innerHTML = "";
  if (buscadorCliente) buscadorCliente.focus();
}

function seleccionarCliente(cliente) {
  clienteSeleccionado = cliente;
  const clienteNombre = document.getElementById("clienteNombre");
  if (clienteNombre) clienteNombre.innerText = cliente.nombre;
  const modalCliente = document.getElementById("modalCliente");
  if (modalCliente) bootstrap.Modal.getInstance(modalCliente).hide();
}

async function registrarNuevoCliente() {
  const nombre = document.getElementById("nuevoNombre")?.value.trim() || "";
  const documento = document.getElementById("nuevoDocumento")?.value.trim() || "";
  const telefono = document.getElementById("nuevoTelefono")?.value.trim() || "";
  const email = document.getElementById("nuevoEmail")?.value.trim() || "";

  if (!nombre) {
    alert("El nombre es obligatorio");
    return;
  }

  try {
    const res = await fetch('/api/clientes/crear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre, documento, telefono, email })
    });

    const data = await res.json();
    if (data.success) {
      seleccionarCliente(data.cliente);
    } else {
      alert("Error al registrar cliente: " + (data.error || "Error desconocido"));
    }
  } catch (err) {
    alert("Error al registrar cliente.");
    console.error(err);
  }
}

function abrirModalCobro() {
  pagos = []; // Reiniciar pagos al abrir modal
  actualizarListaPagos();

  if (document.getElementById("pago_monto")) document.getElementById("pago_monto").value = "";
  if (document.getElementById("pago_descripcion")) document.getElementById("pago_descripcion").value = "";
  const vueltoMonto = document.getElementById("vuelto_monto");
  if (vueltoMonto) vueltoMonto.innerText = "0";

  cargarMetodosPago();

  const total = productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0);
  const totalACobrar = document.getElementById("total_a_cobrar");
  if (totalACobrar) totalACobrar.innerText = formatearGuaranies(total.toFixed(0));
  const cobroTotal = document.getElementById("cobro_total");
  if (cobroTotal) cobroTotal.value = total.toFixed(0);

  calcularVuelto();

  const modal = new bootstrap.Modal(document.getElementById("modalCobro"));
  modal.show();
}

function agregarPago() {
  const monto = parseFloat(document.getElementById("pago_monto")?.value) || 0;
  const metodo_id = parseInt(document.getElementById("pago_metodo")?.value);
  const descripcion = document.getElementById("pago_descripcion")?.value.trim() || '';

  if (monto <= 0 || !metodo_id) {
    alert("Debe ingresar un monto válido y seleccionar método.");
    return;
  }

  pagos.push({ monto, metodo_pago_id: metodo_id, descripcion });

  if (document.getElementById("pago_monto")) document.getElementById("pago_monto").value = "";
  if (document.getElementById("pago_descripcion")) document.getElementById("pago_descripcion").value = "";

  actualizarListaPagos();
  calcularVuelto();
}

function actualizarListaPagos() {
  const tbody = document.getElementById("tablaPagos");
  if (!tbody) return;
  tbody.innerHTML = "";

  pagos.forEach((p, i) => {
    const metodoNombre = document.querySelector(`#pago_metodo option[value="${p.metodo_pago_id}"]`)?.textContent || 'Método desconocido';
    tbody.innerHTML += `
      <tr>
        <td>${metodoNombre}</td>
        <td>${formatearGuaranies(p.monto.toFixed(0))}</td>
        <td>${p.descripcion || 'Sin descripción'}</td>
        <td><button class="btn btn-sm btn-danger" onclick="eliminarPago(${i})">X</button></td>
      </tr>
    `;
  });

  const totalPagado = pagos.reduce((acc, p) => acc + p.monto, 0);
  const totalPagadoEl = document.getElementById("total_pagado");
  if (totalPagadoEl) totalPagadoEl.innerText = formatearGuaranies(totalPagado.toFixed(0));
}

function eliminarPago(index) {
  pagos.splice(index, 1);
  actualizarListaPagos();
  calcularVuelto();
}

function calcularVuelto() {
  const total = parseFloat(document.getElementById('cobro_total')?.value) || 0;
  const pagado = pagos.reduce((acc, p) => acc + p.monto, 0);
  const vuelto = pagado - total;

  const vueltoMonto = document.getElementById('vuelto_monto');
  if (vueltoMonto) vueltoMonto.innerText = vuelto >= 0 ? formatearGuaranies(vuelto.toFixed(0)) : "0";
}

async function finalizarFactura() {
  if (productos.length === 0) {
    alert("Agrega al menos un producto.");
    return;
  }

  const total = productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0);
  const impuesto = Math.round(total * 0.10);

  const detalles = productos.map(p => ({
    codigo: p.codigo,
    cantidad: p.cantidad,
    precio_unitario: p.precio,
    subtotal: p.precio * p.cantidad
  }));

  const datos = {
    cliente_id: clienteSeleccionado ? clienteSeleccionado.id : null,
    total,
    impuesto,
    detalles,
    pagos
  };

  try {
    const res = await fetch("/facturacion/guardar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });

    const data = await res.json();
    if (data.success) {
      // Calcular vuelto con datos del backend (o tomar el que envía)
      const vueltoFinal = data.vuelto ?? pagos.reduce((acc, p) => acc + p.monto, 0) - total;

      // Redirigir con el vuelto en query param
      window.location.href = `/facturacion?vuelto=${vueltoFinal.toFixed(0)}`;
    } else {
      alert("Error al guardar factura: " + (data.error || "Error desconocido"));
    }
  } catch (err) {
    alert("Error al guardar factura.");
    console.error(err);
  }
}

function reiniciarFactura() {
  productos = [];
  clienteSeleccionado = null;
  const clienteNombre = document.getElementById("clienteNombre");
  if (clienteNombre) clienteNombre.innerText = "Consumidor Final";
  renderTabla();
}

// Carga métodos de pago en el select al abrir modal cobro
async function cargarMetodosPago() {
  try {
    const res = await fetch('/api/metodos_pago');
    const data = await res.json();

    const select = document.getElementById("pago_metodo");
    if (!select) return;
    select.innerHTML = '';

    data.forEach(metodo => {
      const option = document.createElement('option');
      option.value = metodo.id;
      option.textContent = metodo.nombre;
      select.appendChild(option);
    });
  } catch (err) {
    console.error("Error al cargar métodos de pago", err);
  }
}
