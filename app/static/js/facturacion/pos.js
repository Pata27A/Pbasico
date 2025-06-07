let productos = [];
let clienteSeleccionado = null;

// Buscar producto por código o nombre
document.getElementById("buscadorProducto").addEventListener("keypress", async (e) => {
  if (e.key === "Enter") {
    e.preventDefault();
    const texto = e.target.value.trim();
    if (texto === "") return;

    let cantidad = 1;
    let codigo = texto;

    if (texto.startsWith("+")) {
      const partes = texto.split(" ");
      cantidad = parseInt(partes[0].substring(1)) || 1;
      codigo = partes.slice(1).join(" ");
    }

    try {
      const res = await fetch(`/facturacion/api/buscar_producto?codigo=${codigo}`);
      const data = await res.json();

      if (data && data.id) {
        agregarProducto(data, cantidad);
        e.target.value = "";
      } else {
        alert("Producto no encontrado.");
      }
    } catch {
      alert("Error al buscar producto.");
    }
  }
});

// Agregar producto a la tabla
function agregarProducto(producto, cantidad) {
  const existente = productos.find(p => p.id === producto.id);
  if (existente) {
    existente.cantidad += cantidad;
  } else {
    productos.push({
      id: producto.id,
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

    const fila = `
      <tr>
        <td>${p.id}</td>
        <td>${p.nombre}</td>
        <td>${p.cantidad}</td>
        <td>${p.precio}</td>
        <td>${subtotal.toFixed(0)}</td>
        <td><button class="btn btn-sm btn-danger" onclick="eliminarProducto(${index})">X</button></td>
      </tr>
    `;
    tbody.innerHTML += fila;
  });

  document.getElementById("totalFactura").innerText = total.toFixed(0);
  document.getElementById("cobro_total").value = total.toFixed(0);
}

function eliminarProducto(index) {
  productos.splice(index, 1);
  renderTabla();
}

// Abrir modal cliente
function abrirModalCliente() {
  const modal = new bootstrap.Modal(document.getElementById("modalCliente"));
  document.getElementById("busquedaCliente").value = "";
  document.getElementById("resultadosCliente").innerHTML = "";
  modal.show();
}

// Buscar clientes en tiempo real
document.getElementById("busquedaCliente").addEventListener("input", async function () {
  const texto = this.value.trim();
  const contenedor = document.getElementById("resultadosCliente");
  contenedor.innerHTML = "";

  if (texto.length < 2) return;

  try {
    const res = await fetch(`/facturacion/api/buscar_cliente?texto=${texto}`);
    const data = await res.json();

    data.forEach(cliente => {
      const div = document.createElement("div");
      div.classList.add("cliente-item", "mb-1", "p-2", "border");
      div.textContent = `${cliente.nombre} (${cliente.documento || "Sin doc"})`;
      div.style.cursor = "pointer";
      div.onclick = () => seleccionarCliente(cliente);
      contenedor.appendChild(div);
    });
  } catch {
    contenedor.innerHTML = "<div>Error buscando clientes</div>";
  }
});

function seleccionarCliente(cliente) {
  clienteSeleccionado = cliente;
  document.getElementById("clienteNombre").innerText = cliente.nombre;
  bootstrap.Modal.getInstance(document.getElementById("modalCliente")).hide();
}

// Registrar nuevo cliente
document.getElementById("formCliente").addEventListener("submit", async function (e) {
  e.preventDefault();
  const form = new FormData(this);

  try {
    const res = await fetch("/facturacion/api/registrar_cliente", {
      method: "POST",
      body: form
    });
    const data = await res.json();

    if (data && data.id) {
      seleccionarCliente(data);
    } else {
      alert("Error al registrar cliente.");
    }
  } catch {
    alert("Error en conexión.");
  }
});

// Abrir modal de cobro
function abrirModalCobro() {
  const modal = new bootstrap.Modal(document.getElementById("modalCobro"));
  document.getElementById("cobro_pago").value = "";
  document.getElementById("cobro_descripcion").value = "";
  modal.show();
}

// Confirmar cobro
document.getElementById("formCobro").addEventListener("submit", function (e) {
  e.preventDefault();
  const total = parseInt(document.getElementById("cobro_total").value) || 0;
  const pagado = parseInt(document.getElementById("cobro_pago").value) || 0;
  if (pagado < total) {
    alert("El monto pagado es menor al total.");
    return;
  }

  finalizarFactura();
});

// Finalizar factura
async function finalizarFactura() {
  if (productos.length === 0) {
    alert("Agrega al menos un producto.");
    return;
  }

  const datos = {
    cliente_id: clienteSeleccionado ? clienteSeleccionado.id : null,
    productos: productos.map(p => ({
      id: p.id,
      cantidad: p.cantidad,
      precio: p.precio
    })),
    metodo_pago_id: parseInt(document.getElementById("cobro_metodo").value),
    descripcion_pago: document.getElementById("cobro_descripcion").value
  };

  try {
    const res = await fetch("/facturacion/guardar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });

    const data = await res.json();
    if (data && data.success) {
      window.location.href = `/facturacion/imprimir/${data.factura_id}`;
    } else {
      alert("Error al guardar factura.");
    }
  } catch {
    alert("Error al guardar.");
  }
}

// Reiniciar factura
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
