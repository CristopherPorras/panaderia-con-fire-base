// Función para establecer la fecha actual en el campo de entrada
function setCurrentDate() {
    const dateInput = document.getElementById('date-input');
    const today = new Date().toISOString().split('T')[0]; // Obtiene la fecha en formato YYYY-MM-DD
    dateInput.value = today; // Establece el valor del campo de fecha a la fecha actual
}

// Llama a la función al cargar la página
window.onload = setCurrentDate;


// Lógica para habilitar cantidades y actualizar el total
document.querySelectorAll("#productos-container .producto-opcion").forEach(opcion => {
    const checkbox = opcion.querySelector('input[type="checkbox"]');
    const cantidadInput = opcion.querySelector('input[type="number"]');

    checkbox.addEventListener('change', () => {
        cantidadInput.disabled = !checkbox.checked;
        if (!checkbox.checked) {
            cantidadInput.value = ''; // Limpia la cantidad si el producto se desmarca
        }
        actualizarTotal();
    });

    cantidadInput.addEventListener('input', actualizarTotal);
});

function actualizarTotal() {
    let total = 0;
    document.querySelectorAll("#productos-container .producto-opcion").forEach(opcion => {
        const checkbox = opcion.querySelector('input[type="checkbox"]');
        const cantidadInput = opcion.querySelector('input[type="number"]');
        const label = opcion.querySelector('label');
        const precio = parseFloat(label.textContent.split('-')[1].trim().replace('COP', '').replace(/\./g, ''));

        if (checkbox.checked && cantidadInput.value) {
            total += precio * parseFloat(cantidadInput.value);
        }
    });

    // ✅ Mostrar total formateado con puntos (COP)
    const totalFormateado = new Intl.NumberFormat('es-CO').format(total);
    document.getElementById('total_factura').value = totalFormateado + " COP";

    // ✅ Enviar limpio al backend
    document.getElementById('total_factura_sin_formato').value = total.toFixed(2);
}
