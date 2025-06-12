let productos = [];
let clienteSeleccionado = null;
let cantidadPendiente = null;

// Buscar producto por código o nombre
document.getElementById("buscadorProducto").addEventListener("keypress", async (e) => {
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
        <td>${p.precio}</td>
        <td>${subtotal.toFixed(0)}</td>
        <td><button class="btn btn-sm btn-danger" onclick="eliminarProducto(${index})">X</button></td>
      </tr>
    `;
  });

  document.getElementById("totalFactura").innerText = total.toFixed(0);
  document.getElementById("cobro_total").value = total.toFixed(0);
}

function eliminarProducto(index) {
  productos.splice(index, 1);
  renderTabla();
}

// Cliente
function abrirModalCliente() {
  const modal = new bootstrap.Modal(document.getElementById("modalCliente"));
  modal.show();
  document.getElementById("buscadorCliente").value = "";
  document.getElementById("resultadoClientes").innerHTML = "";
  document.getElementById("buscadorCliente").focus();
}

document.getElementById("buscadorCliente").addEventListener("input", async function () {
  const q = this.value.trim();
  const lista = document.getElementById("resultadoClientes");
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

function seleccionarCliente(cliente) {
  clienteSeleccionado = cliente;
  document.getElementById("clienteNombre").innerText = cliente.nombre;
  bootstrap.Modal.getInstance(document.getElementById("modalCliente")).hide();
}

// Registrar nuevo cliente
async function registrarNuevoCliente() {
  const nombre = document.getElementById("nuevoNombre").value.trim();
  const documento = document.getElementById("nuevoDocumento").value.trim();
  const telefono = document.getElementById("nuevoTelefono").value.trim();
  const email = document.getElementById("nuevoEmail").value.trim();

  if (!nombre) return alert("El nombre es obligatorio");

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

// Cobro
function abrirModalCobro() {
  document.getElementById("cobro_pago").value = "";
  document.getElementById("cobro_descripcion").value = "";
  document.getElementById("vuelto_monto").innerText = "0";
  cargarMetodosPago();

  // 🚩 Este bloque es lo que te estaba faltando:
  const total = productos.reduce((acc, p) => acc + p.precio * p.cantidad, 0);
  document.getElementById("total_a_cobrar").innerText = total.toFixed(0);
  document.getElementById("cobro_total").value = total.toFixed(0); // mantenemos para el cálculo posterior
  document.getElementById("cobro_pago").value = total.toFixed(0);  // opcional: precargamos el monto

  calcularVuelto(); // actualizamos el vuelto inicial

  const modal = new bootstrap.Modal(document.getElementById("modalCobro"));
  modal.show();
}


document.getElementById("cobro_pago").addEventListener("input", calcularVuelto);

function calcularVuelto() {
  let total = parseFloat(document.getElementById('cobro_total').value) || 0;
  let pagado = parseFloat(document.getElementById('cobro_pago').value) || 0;
  let vuelto = pagado - total;

  document.getElementById('vuelto_monto').innerText = vuelto >= 0 ? vuelto.toFixed(0) : "0";
}

document.getElementById("formCobro").addEventListener("submit", function (e) {
  e.preventDefault();

  const total = parseInt(document.getElementById("cobro_total").value) || 0;
  const pagado = parseInt(document.getElementById("cobro_pago").value) || 0;

  if (pagado < total) {
    alert("El monto pagado es menor al total.");
    return;
  }

  finalizarFactura(pagado);
});

// Finalizar factura
async function finalizarFactura(montoPagado) {
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

  const pagos = [{
    monto: montoPagado,
    metodo_pago_id: parseInt(document.getElementById("cobro_metodo").value),
    descripcion: document.getElementById("cobro_descripcion").value || ''
  }];

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
      window.location.href = `/facturacion/imprimir/${data.factura_id}`;
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
  document.getElementById("clienteNombre").innerText = "Consumidor Final";
  renderTabla();
}

// Atajos de teclado
document.addEventListener("keydown", (e) => {
  if (e.code === "F5") {
    e.preventDefault();
    abrirModalCliente();
  } else if (e.code === "F6") {
    e.preventDefault();
    abrirModalCobro();
  }
});

async function cargarMetodosPago() {
  try {
    const res = await fetch('/api/metodos_pago');
    const data = await res.json();

    const select = document.getElementById("cobro_metodo");
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
