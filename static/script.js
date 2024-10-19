// Función para establecer la fecha actual en el campo de entrada
function setCurrentDate() {
    const dateInput = document.getElementById('date-input');
    const today = new Date().toISOString().split('T')[0]; // Obtiene la fecha en formato YYYY-MM-DD
    dateInput.value = today; // Establece el valor del campo de fecha a la fecha actual
}

// Llama a la función al cargar la página
window.onload = setCurrentDate;



// productos

