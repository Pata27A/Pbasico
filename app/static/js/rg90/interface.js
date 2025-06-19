document.addEventListener("DOMContentLoaded", () => {
  // Referencias
  const form = document.querySelector("#rg90-form");
  const resultDiv = document.querySelector("#rg90-result");
  const inputArchivo = document.querySelector("#archivo");
  const btnValidar = document.querySelector("#validar-btn");

  // Función para mostrar mensajes
  function mostrarResultado(html) {
    resultDiv.innerHTML = html;
  }

  // Enviar período para generar archivo y validar
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
      const params = new URLSearchParams(formData);

      mostrarResultado("<p>⏳ Generando y validando archivo RG90...</p>");

      try {
        const response = await fetch("/rg90/ajax", {
          method: "POST",
          body: params,
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        const data = await response.json();

        if (data.ok) {
          mostrarResultado(`
            <p style="color:green;">✅ Archivo validado correctamente.</p>
            <a href="/static/rg90/${data.archivo}" download>📦 Descargar ZIP</a>
          `);
        } else {
          let html = `<p style='color:red;'>❌ Se encontraron errores:</p><ul>`;
          for (const error of data.errores) {
            html += `<li>${error}</li>`;
          }
          html += `</ul>`;
          mostrarResultado(html);
        }
      } catch (err) {
        mostrarResultado(`<p style='color:red;'>Error al procesar la solicitud</p>`);
        console.error(err);
      }
    });
  }

  // Validar archivo CSV local seleccionado
  if (btnValidar && inputArchivo) {
    btnValidar.addEventListener("click", async () => {
      const archivo = inputArchivo.files[0];
      if (!archivo) {
        mostrarResultado("<p style='color:red;'>❌ Por favor seleccione un archivo CSV primero.</p>");
        return;
      }

      mostrarResultado("<p>⏳ Validando archivo CSV local...</p>");

      try {
        const texto = await archivo.text();

        // Enviar contenido CSV al servidor para validar
        const response = await fetch("/rg90/validar_local", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ contenido_csv: texto }),
        });

        const data = await response.json();

        if (data.ok) {
          mostrarResultado(`<p style="color:green;">✅ Archivo local validado correctamente.</p>`);
        } else {
          let html = `<p style='color:red;'>❌ Se encontraron errores en el archivo local:</p><ul>`;
          for (const error of data.errores) {
            html += `<li>${error}</li>`;
          }
          html += `</ul>`;
          mostrarResultado(html);
        }
      } catch (err) {
        mostrarResultado(`<p style='color:red;'>Error al procesar el archivo local.</p>`);
        console.error(err);
      }
    });
  }
});
