/*
		Designed by: SELECTO
		Original image: https://dribbble.com/shots/5311359-Diprella-Login
*/

let switchCtn = document.querySelector("#switch-cnt");
let switchC1 = document.querySelector("#switch-c1");
let switchC2 = document.querySelector("#switch-c2");
let switchCircle = document.querySelectorAll(".switch__circle");
let switchBtn = document.querySelectorAll(".switch-btn");
let aContainer = document.querySelector("#a-container");
let bContainer = document.querySelector("#b-container");
let allButtons = document.querySelectorAll(".submit");

let getButtons = (e) => e.preventDefault()

let changeForm = (e) => {

    switchCtn.classList.add("is-gx");
    setTimeout(function(){
        switchCtn.classList.remove("is-gx");
    }, 1500)

    switchCtn.classList.toggle("is-txr");
    switchCircle[0].classList.toggle("is-txr");
    switchCircle[1].classList.toggle("is-txr");

    switchC1.classList.toggle("is-hidden");
    switchC2.classList.toggle("is-hidden");
    aContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-txl");
    bContainer.classList.toggle("is-z200");
}

let mainF = (e) => {
    for (var i = 0; i < allButtons.length; i++)
        allButtons[i].addEventListener("click", getButtons );
    for (var i = 0; i < switchBtn.length; i++)
        switchBtn[i].addEventListener("click", changeForm)
}

// Función para validar el formulario de inicio de sesión
function validarFormulario(e) {
    const username = document.querySelector('#username').value;
    const password = document.querySelector('#password').value;
    const mensajesError = [];

    // Validar usuario
    if (!username) {
        mensajesError.push('El usuario es requerido');
    }

    // Validar contraseña
    if (!password) {
        mensajesError.push('La contraseña es requerida');
    } else if (password.length < 8) {
        mensajesError.push('La contraseña debe tener al menos 8 caracteres');
    }

    // Si hay errores, mostrarlos y prevenir el envío del formulario
    if (mensajesError.length > 0) {
        e.preventDefault();
        mostrarErrores(mensajesError);
    }
}

// Función para validar formato de email
function validarEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Función para mostrar mensajes de error
function mostrarErrores(mensajes) {
    const contenedorMensajes = document.querySelector('.messages');
    contenedorMensajes.innerHTML = '';

    mensajes.forEach(mensaje => {
        const alertaError = document.createElement('div');
        alertaError.className = 'alert alert-danger';
        alertaError.textContent = mensaje;
        contenedorMensajes.appendChild(alertaError);
    });
}

// Función para limpiar mensajes de error cuando el usuario empiece a escribir
function limpiarErrores() {
    const contenedorMensajes = document.querySelector('.messages');
    if (contenedorMensajes) {
        contenedorMensajes.innerHTML = '';
    }
}

// Agregar eventos de validación al formulario
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const inputs = document.querySelectorAll('input');

    if (loginForm) {
        loginForm.addEventListener('submit', validarFormulario);
    }

    inputs.forEach(input => {
        input.addEventListener('input', limpiarErrores);
    });

    // Mantener la funcionalidad existente
    mainF();
});

window.addEventListener("load", mainF);
