// static/js/rg90/interface_compras.js
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#rg90c-form");           // Form de compras
  const resultDiv = document.querySelector("#rg90c-result");    // Resultado de compras
  const inputArchivo = document.querySelector("#archivo");      // Input de CSV
  const btnValidar = document.querySelector("#validar-btn");    // Botón validar

  function mostrarResultado(html) {
    resultDiv.innerHTML = html;
  }

  // ✅ 1️⃣ Generación y validación de RG90 para compras
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const params = new URLSearchParams(formData);

      mostrarResultado("<p>⏳ Generando y validando RG90 de compras...</p>");
      try {
        const response = await fetch("/rg90/compras", {
          method: "POST",
          body: params,
        });
        const data = await response.json();

        if (data.ok) {
          mostrarResultado(`
            <p style="color:green;"><strong>✅ Archivo de compras validado correctamente</strong></p>
            <a href="/static/rg90/${data.archivo}" download>📦 Descargar ZIP</a>
          `);
        } else {
          let html = "<p style='color:red;'><strong>❌ Se encontraron errores en el archivo de compras:</strong></p><ul>";
          for (const error of data.errores) {
            html += `<li>${error}</li>`;
          }
          html += "</ul>";
          mostrarResultado(html);
        }
      } catch (err) {
        mostrarResultado("<p style='color:red;'>Error al procesar la solicitud de compras</p>");
        console.error(err);
      }
    });
  }

  // ✅ 2️⃣ Validación de archivo de compras local
  if (btnValidar && inputArchivo) {
    btnValidar.addEventListener("click", async () => {
      const archivo = inputArchivo.files[0];
      if (!archivo) {
        mostrarResultado("<p style='color:red;'>❌ Por favor seleccione un archivo CSV primero</p>");
        return;
      }

      mostrarResultado("<p>⏳ Validando archivo de compras local...</p>");
      try {
        const texto = await archivo.text();
        const response = await fetch("/rg90/compras/validar_local", {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({contenido_csv: texto}),
        });
        const data = await response.json();

        if (data.ok) {
          mostrarResultado(`<p style="color:green;"><strong>✅ Archivo de compras validado correctamente</strong></p>`);
        } else {
          let html = "<p style='color:red;'><strong>❌ Se encontraron errores en el archivo de compras local:</strong></p><ul>";
          for (const error of data.errores) {
            html += `<li>${error}</li>`;
          }
          html += "</ul>";
          mostrarResultado(html);
        }
      } catch (err) {
        mostrarResultado("<p style='color:red;'>Error al procesar el archivo de compras local.</p>");
        console.error(err);
      }
    });
  }
});
