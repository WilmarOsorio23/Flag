document.addEventListener('DOMContentLoaded', function () {
    // Configuración del dropdown
    // 1. Actualiza texto del botón del dropdown empleado
    function updateDropdownLabel(dropdownId, checkboxes) {
        const button = document.getElementById(dropdownId);
        const selectedText = button.getAttribute('data-selected-text');
        const selectedOptions = Array.from(checkboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.nextSibling.textContent.trim());
        button.textContent = selectedOptions.length > 0 
            ? selectedOptions.join(', ') 
            : selectedText;
    }

    // 2. Inicializar checkboxes de empleados
    const empleadoCheckboxes = document.querySelectorAll('#dropdownEmpleado + .dropdown-menu input[type="checkbox"]');
    empleadoCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateDropdownLabel('dropdownEmpleado', empleadoCheckboxes);
            actualizarPagarés();
        });
    });

    updateDropdownLabel('dropdownEmpleado', empleadoCheckboxes); // Inicial

    // 3. Establecer fecha actual
    document.querySelectorAll('.fecha-creacion-input').forEach(input => {
        const fechaActual = new Date();
        const ano = fechaActual.getFullYear();
        const mes = String(fechaActual.getMonth() + 1).padStart(2, '0');
        const dia = String(fechaActual.getDate()).padStart(2, '0');
        input.value = `${ano}-${mes}-${dia}`;
    });


    /**************************** */

    function actualizarEstadoBotones() {
        const checkboxes = listaPagares.querySelectorAll('input[type="checkbox"]');
        const hayPagares = checkboxes.length > 0;
    
        const btnEliminar = document.getElementById('btn-eliminar-pagares');
        const btnActualizar = document.getElementById('btn-actualizar-pagares');
    
        // Habilita o deshabilita los botones según si hay pagarés
        btnEliminar.disabled = !hayPagares;
        btnActualizar.disabled = !hayPagares;
    }

    // 4. Obtener todos los pagarés desde el HTML oculto
    const pagares = Array.from(document.querySelectorAll('#pagares-data div')).map(pagare => ({
        id: pagare.dataset.pagareId,  // <== IMPORTANTE
        documento: pagare.dataset.documento.trim(),
        tipo: pagare.dataset.tipo,
        fecha: pagare.dataset.fecha,
        estado: pagare.dataset.estado
    }));

    const listaPagares = document.getElementById('lista-pagares');
    const dropdownPagaresBtn = document.getElementById('dropdownPagares');

    // 5. Función para cargar todos los pagarés sin filtro
    function cargarTodosLosPagarés() {
        listaPagares.innerHTML = '';
        pagares.forEach(pagare => {
            const li = document.createElement('li');
            li.className = 'dropdown-item';
            li.innerHTML = `
                <input type="checkbox" 
                    name="pagare" 
                    value="${pagare.id}"
                    id="pagare_${pagare.id}">
                <label for="pagare_${pagare.id}" class="ms-2">
                    ${pagare.tipo} | ${pagare.fecha} | #${pagare.id} | ${pagare.estado}
                </label>
            `;
            listaPagares.appendChild(li);
        });
        actualizarEstadoBotones();
    }

    // 6. Función para actualizar pagarés según empleados seleccionados
    function actualizarPagarés() {
        const documentosSeleccionados = Array.from(empleadoCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value.trim());
            

        const contenedorPagares = document.getElementById('contenedor-pagares');
        const accionesPagares = document.getElementById('acciones-pagares');


        let pagaresFiltrados = pagares;
    
        if (documentosSeleccionados.length > 0) {
            pagaresFiltrados = pagares.filter(p => 
                documentosSeleccionados.includes(p.documento)
            );
        }

        listaPagares.innerHTML = '';
        if (pagaresFiltrados.length > 0) {
            contenedorPagares.style.display = 'block';
            accionesPagares.style.setProperty('display', 'flex', 'important');

            pagaresFiltrados.forEach(pagare => {
                const li = document.createElement('li');
                li.className = 'dropdown-item';
                li.innerHTML = `
                    <input type="checkbox" 
                        name="pagare" 
                        value="${pagare.id}"
                        id="pagare_${pagare.id}">
                    <label for="pagare_${pagare.id}" class="ms-2">
                        ${pagare.tipo} | ${pagare.fecha} | #${pagare.id} | ${pagare.estado}
                    </label>
                `;
                listaPagares.appendChild(li);
            });
        } else {
            contenedorPagares.style.display = 'none';
            accionesPagares.style.setProperty('display', 'none', 'important');
            dropdownPagaresBtn.disabled = true;
            listaPagares.innerHTML = '<li class="dropdown-item text-muted">No hay pagarés para este empleado</li>';
        }
        actualizarEstadoBotones();
    }

    // 7. Inicializar la lista al cargar
    actualizarPagarés();

    

    //**************************************** */
    /*****************eliminar pagares del select */

    document.getElementById('btn-eliminar-pagares').addEventListener('click', function () {
        const checkboxesSeleccionados = listaPagares.querySelectorAll('input[type="checkbox"]:checked');
        const accionesPagare = document.getElementById('acciones-pagares');
    
        if (checkboxesSeleccionados.length === 0) {
            mostrarMensaje('Seleccione al menos un pagaré para eliminar.');
            return;
        }
    
        // Mostrar confirmación estilizada
        mostrarConfirmacion(
            '¿Está seguro de que desea eliminar los pagarés seleccionados? Esta acción no se puede deshacer.',
            () => {
                const idsSeleccionados = Array.from(checkboxesSeleccionados).map(cb => cb.value);
    
                fetch('/pagare/eliminar/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({ ids: idsSeleccionados })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Eliminar visualmente del DOM y array pagares
                        checkboxesSeleccionados.forEach(checkbox => {
                            const id = checkbox.value;
    
                            const index = pagares.findIndex(p => p.id === id);
                            if (index !== -1) pagares.splice(index, 1);
    
                            const li = checkbox.closest('li');
                            if (li) li.remove();
                        });
    
                        // Verificar si ya no hay pagarés
                        if (listaPagares.querySelectorAll('input[type="checkbox"]').length === 0) {
                            document.getElementById('contenedor-pagares').style.display = 'none';
                            accionesPagare.style.setProperty('display', 'none', 'important');
                            document.getElementById('dropdownPagares').disabled = true;
    
                            // Deshabilitar botones de eliminar y actualizar
                            document.getElementById('btn-eliminar-pagares').disabled = true;
                            document.getElementById('btn-actualizar-pagares').disabled = true;
                        }
    
                        actualizarEstadoBotones();
                        mostrarMensaje('Pagaré(s) eliminado(s) correctamente.');
                    } else {
                        mostrarMensaje('Error al eliminar: ' + data.message);
                    }
                })
                .catch(error => {
                    mostrarMensaje('Error al enviar la solicitud: ' + error);
                });
            },
            () => {
                mostrarMensaje('Eliminación cancelada.');
            }
        );
    });
    

    function getCSRFToken() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return '';
    }
    


    /********************************* */
    /*********boton actualizar mostrar selects agregar actividad tabla pagare y botones de guardar y cancelar**/
    const actualizarBtn = document.getElementById('btn-actualizar-pagares');
    const actividadWrapper = document.querySelector('.actividad-ejecutado-wrapper');
    const guardarBtn = document.getElementById('guardar-pagares-btn');
    const cancelarBtn = document.getElementById('cancelar-pagares-btn');

    if (actualizarBtn) {
        console.log("Botón encontrado");

        actualizarBtn.addEventListener('click', function () {
            console.log("Click en botón Actualizar");

            const checkboxesSeleccionados = document.querySelectorAll('#lista-pagares input[type="checkbox"]:checked');

            if (checkboxesSeleccionados.length > 0) {
                console.log("Hay pagarés seleccionados");

                if (actividadWrapper) {
                    actividadWrapper.style.display = 'block';
                    console.log("Se muestra el contenedor de actividades");
                }

                 // Mostrar botones de guardar y cancelar
                if (guardarBtn && cancelarBtn) {
                    guardarBtn.classList.remove('d-none');
                    cancelarBtn.classList.remove('d-none');
                    console.log("Botones Guardar y Cancelar mostrados");
                }
            } else {
                console.log("Ningún pagaré seleccionado");
                mostrarMensaje("Por favor selecciona al menos un pagaré para agregar actualizar.");
            }
        });

    } else {
        console.log("Botón de actualizar no encontrado");
    }


    if (cancelarBtn) {
        cancelarBtn.addEventListener('click', function () {
            const guardarBtn = document.getElementById('guardar-pagares-btn');
            const actividadWrapper = document.querySelector('.actividad-ejecutado-wrapper');

            if (guardarBtn) guardarBtn.classList.add('d-none');
            cancelarBtn.classList.add('d-none');
            if (actividadWrapper) actividadWrapper.style.display = 'none';

            console.log("Se canceló la edición de pagarés");
        });
    }


/**************** */

    function waitForElement(selector, callback, maxAttempts = 50, interval = 100) {
        let attempts = 0;
        const checkInterval = setInterval(() => {
            const element = document.querySelector(selector);
            if (element) {
                clearInterval(checkInterval);
                callback(element);
            } else if (attempts >= maxAttempts) {
                clearInterval(checkInterval);
                console.error(`Elemento ${selector} no encontrado después de ${maxAttempts} intentos`);
            }
            attempts++;
        }, interval);
    }

    function calcularPorcentajeEjecucion(documento) {
        const card = document.querySelector(`.card[data-doc="${documento}"]`);
        if (!card) return;
    
        const totalPlaneado = card.querySelector('.total-planeado');
        const totalEjecutado = card.querySelector('.total-ejecutado');
        const porcentajeEjecucion = card.querySelector('.ejecucion');
    
        if (totalPlaneado && totalEjecutado && porcentajeEjecucion) {
            const planeado = parseFloat(totalPlaneado.value) || 0;
            const ejecutado = parseFloat(totalEjecutado.value) || 0;
            const porcentaje = planeado > 0 ? (ejecutado / planeado) * 100 : 0;
    
            porcentajeEjecucion.value = porcentaje.toFixed(2) + '%';
        }
    }
/***************************** */



function llenarFormularioPagares(data) {
    const { pagares, planeadas, ejecutadas } = data;

    if (!data || !data.pagares) {
        console.error("No se recibieron datos válidos del servidor:", data);
        return;
    }

    console.log("Datos recibidos para llenar formularios:", data);

    pagares.forEach(pagare => {
        const doc = pagare.documento;
        console.log(`Procesando pagaré: ${doc}`);

        const setValue = (id, value) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value || '';
                console.log(`Set ${id} = ${value}`);
            }
        };

        setValue(`fecha_creacion_${doc}`, pagare.fecha_creacion);
        setValue(`valor_pagare_${doc}`, pagare.valor_pagare);
        setValue(`meses_condonacion_${doc}`, pagare.meses_condonacion);
        setValue(`valor_capacitacion_${doc}`, pagare.valor_capacitacion || '0.00');
        setValue(`estado_${doc}`, pagare.estado || 'proceso');
        setValue(`descripcion_${doc}`, pagare.descripcion || '');

        const inputPagareId = document.getElementById(`pagare_id_${doc}`);
        if (inputPagareId) {
            inputPagareId.value = pagare.id;
        }

        const setDateValue = (id, dateStr) => {
            const element = document.getElementById(id);
            if (element && dateStr) {
                element.value = dateStr.substring(0, 10);
            }
        };

        setDateValue(`fecha_fin_${doc}`, pagare.fecha_fin);
        setDateValue(`fecha_inicio_${doc}`, pagare.fecha_inicio);

        const inputTipoPagare = document.getElementById(`tipo_pagare_${doc}`);
        if (inputTipoPagare && pagare.tipo_pagare) {
            inputTipoPagare.value = pagare.tipo_pagare.id;
        }

        setDateValue(`ejecucion_${doc}`, pagare.porcentaje_ejecucion);

        const inputEjecucion = document.getElementById(`ejecucion_${doc}`);
        if (inputEjecucion) {
            const porcentaje = parseFloat(pagare.ejecucion || 0).toFixed(2);
            inputEjecucion.value = `${porcentaje}%`;

            const inputFechaInicio = document.getElementById(`fecha_inicio_${doc}`);
            if (inputFechaInicio) {
                inputFechaInicio.disabled = (porcentaje !== "100.00");
            }
        }

        // === Actividades planeadas ===
        const contenedorPlaneadas = document.getElementById(`actividades-${doc}`);
        if (contenedorPlaneadas) {
            contenedorPlaneadas.innerHTML = '';
            const actividadesPlaneadas = planeadas.filter(p => p.pagare_id === pagare.id);

            actividadesPlaneadas.forEach(item => {
                const fila = document.createElement('tr');
                fila.setAttribute('data-actividad-id', item.actividad_id);
                fila.innerHTML = `
                    <td>${item.actividad_nombre}</td>
                    <td>
                        <input type="number" 
                            name="horas_${doc}_${item.actividad_id}" 
                            value="${item.horas_planeadas}" 
                            class="form-control horas-planeadas"
                            disabled>
                    </td>
                    <td>
                        <button type="button" class="btn btn-danger btn-sm btn-remover" disabled>
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                contenedorPlaneadas.appendChild(fila);
            });

            const totalHorasPlaneadas = actividadesPlaneadas.reduce((sum, item) => sum + Number(item.horas_planeadas), 0);
            const totalInput = document.getElementById(`total-planeado-${doc}`);
            if (totalInput) {
                totalInput.value = totalHorasPlaneadas;
                const tfoot = totalInput.closest('tfoot');
                if (tfoot) tfoot.style.display = 'table-footer-group';
            }
        }

        // === Actividades ejecutadas ===
        const contenedorEjecutadas = document.getElementById(`ejecutado-${doc}`);
        if (contenedorEjecutadas) {
            contenedorEjecutadas.innerHTML = '';
            const actividadesEjecutadas = ejecutadas.filter(e => e.pagare_id === pagare.id);

            actividadesEjecutadas.forEach(item => {
                const fila = document.createElement('tr');
                fila.setAttribute('data-actividad-id', item.actividad_id);
                fila.classList.add('fila-ejecutado');
                fila.innerHTML = `
                    <td>${item.actividad_nombre}</td>
                    <td>
                        <input type="number" 
                            id="horas_ejecutadas_${doc}_${item.actividad_id}"
                            name="horas_ejecutadas_${doc}_${item.actividad_id}" 
                            value="${item.horas_ejecutadas}" 
                            class="form-control horas-ejecutadas">
                        <input type="hidden" 
                            name="actividad_ejecutada_id_${doc}[]" 
                            value="${item.actividad_id}">
                    </td>
                    <td>
                        <button type="button" class="btn btn-danger btn-sm btn-remover">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                `;
                contenedorEjecutadas.appendChild(fila);
            });
        }
        calcularTotalEjecutado();
    });
    document.querySelectorAll('.card.mb-4').forEach(card => {
        const totalPlaneado = card.querySelector('.total-planeado');
        const totalEjecutado = card.querySelector('.total-ejecutado');
        const fechaInicio = card.querySelector('.fecha-inicio');

        if (totalPlaneado && totalEjecutado && fechaInicio) {
            const planeado = parseFloat(totalPlaneado.value) || 0;
            const ejecutado = parseFloat(totalEjecutado.value) || 0;

            if (planeado === ejecutado) {
                fechaInicio.disabled = false;
            } else {
                fechaInicio.disabled = true;
                fechaInicio.value = '';
            }
        }
    });
}



actualizarBtn.addEventListener('click', function() {
    console.log("Click en botón Actualizar");
    
    const checkboxes = document.querySelectorAll('#lista-pagares input[type="checkbox"]:checked');
    const idsSeleccionados = Array.from(checkboxes).map(cb => cb.value);
    
    if (idsSeleccionados.length > 0) {
        console.log("Pagarés seleccionados:", idsSeleccionados);
        
        // Mostrar formularios
        if (actividadWrapper) actividadWrapper.style.display = 'block';
        guardarBtn.classList.remove('d-none');
        cancelarBtn.classList.remove('d-none');
        
        fetch('/pagares/obtener_datos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ pagare_ids: idsSeleccionados })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Error en la respuesta del servidor');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log("Datos recibidos del servidor:", data);
            llenarFormularioPagares(data);
        })
        .catch(error => {
            console.error("Error al obtener pagarés:", error);
            mostrarMensaje(`Error: ${error.message}`);
        });
    } else {
        mostrarMensaje("Por favor selecciona al menos un pagaré para actualizar.");
    }
});


/************************************ */

// Evento para guardar pagarés
document.getElementById('guardar-pagares-btn').addEventListener('click', function (e) {
    e.preventDefault();
    const data = {};
    const filas = document.querySelectorAll('.fila-condonacion');

    filas.forEach(fila => {
        const doc = fila.querySelector('input[data-doc]').dataset.doc;
        const pagareId = fila.querySelector('input.pagare-id[data-doc="' + doc + '"]').value;

        const descripcionInput = fila.querySelector(`#descripcion_${doc}`);
        if (!descripcionInput || descripcionInput.value.trim() === '') {
            mostrarMensaje(`El campo "Descripción" es obligatorio para el documento ${doc}.`);
            return;
        }

        data[doc] = {
            pagare_id: pagareId,
            fecha_creacion: fila.querySelector(`#fecha_creacion_${doc}`).value,
            tipo_pagare: fila.querySelector(`#tipo_pagare_${doc}`).value,
            descripcion: descripcionInput.value.trim(),
            fecha_inicio: fila.querySelector(`#fecha_inicio_${doc}`).value || '',
            fecha_fin: fila.querySelector(`#fecha_fin_${doc}`).value || '',
            meses_condonacion: fila.querySelector(`#meses_condonacion_${doc}`).value,
            valor_pagare: fila.querySelector(`#valor_pagare_${doc}`).value,
            ejecucion: fila.querySelector(`#ejecucion_${doc}`).value.replace('%', ''),
            valor_capacitacion: fila.querySelector(`#valor_capacitacion_${doc}`).value,
            estado: fila.querySelector(`#estado_${doc}`).value,
            ejecutadas: []
        };

        // Recoger actividades ejecutadas VISIBLES
        const filasEjecutado = document.querySelectorAll(`#ejecutado-${doc} .fila-ejecutado`);
        filasEjecutado.forEach(row => {
            const actividadId = row.dataset.actividadId;
            const horasInput = row.querySelector('.horas-ejecutadas');
            if (actividadId && horasInput) {
                data[doc].ejecutadas.push({
                    actividad_id: actividadId,
                    horas: horasInput.value || 0
                });
            }
        });
    });

    console.log("📤 Enviando datos a Django:", data);

    fetch('/pagares/actualizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log("✅ Respuesta del servidor:", result);
        if (result.error) {
            mostrarMensaje('Error: ' + result.error);
        } else {
            mostrarMensaje(result.mensaje || 'Actualización exitosa');
            setTimeout(() => window.location.reload(), 1500);
        }    
    })
    .catch(error => {
        console.error("❌ Error al actualizar:", error);
        mostrarMensaje('Error al actualizar los pagarés');
    });
});

// Manejo de eliminación de filas (CORREGIDO)
document.addEventListener('click', function (e) {
    if (e.target.closest('.btn-remover-ejecutado')) {
        e.preventDefault();
        const boton = e.target.closest('.btn-remover-ejecutado');
        const fila = boton.closest('tr');
        
        if (fila) {
            const actividadId = fila.dataset.actividadId;
            const tbody = fila.closest('tbody');
            const doc = tbody ? tbody.id.replace('ejecutado-', '') : '';
            
            // Registrar eliminación
            if (doc && actividadId) {
                if (!eliminadasPorDoc[doc]) eliminadasPorDoc[doc] = [];
                eliminadasPorDoc[doc].push(parseInt(actividadId));
            }
            
            fila.remove();
            
            if (tbody) {
                actualizarTotalEjecutado(tbody.id);
            }
        }
    }
});

// Función para actualizar total ejecutado



// Si estás usando CSRF y no tienes esta función:
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}



// Función para obtener token CSRF
function getCSRFToken() {
    return document.querySelector('[name="csrfmiddlewaretoken"]')?.value || '';
}

// Función para esperar elementos dinámicos
function waitForElement(selector, callback, maxAttempts = 50, interval = 100) {
    let attempts = 0;
    const checkInterval = setInterval(() => {
        const element = document.querySelector(selector);
        if (element) {
            clearInterval(checkInterval);
            callback(element);
        } else if (attempts >= maxAttempts) {
            clearInterval(checkInterval);
            console.error(`Elemento ${selector} no encontrado después de ${maxAttempts} intentos`);
        }
        attempts++;
    }, interval);
}
    
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrfToken = csrfInput ? csrfInput.value : '';


    
    /***********************/

    



    /************************************************ */

    function configurarRecalculoValorCapacitacion() {
        document.querySelectorAll('.ejecucion').forEach(inputEjecucion => {
            const documento = inputEjecucion.dataset.documento;
    
            inputEjecucion.addEventListener('input', () => {
                const valorPagareInput = document.querySelector(`[name="valor_pagare_${documento}"]`);
                const valorCapacitacionInput = document.querySelector(`[name="valor_capacitacion_${documento}"]`);
    
                if (!valorPagareInput || !valorCapacitacionInput) return;
    
                let valorPagare = parseFloat(valorPagareInput.value);
                let porcentajeTexto = inputEjecucion.value.replace('%', '').trim();
                let porcentaje = parseFloat(porcentajeTexto);
    
                if (isNaN(valorPagare) || isNaN(porcentaje)) {
                    valorCapacitacionInput.value = "0.00";
                    return;
                }
    
                const resultado = (valorPagare * porcentaje / 100).toFixed(2);
                valorCapacitacionInput.value = resultado;
            });
        });
    }

    


    /*********************************************** */



    // Función calcular meses condonacion
    function calcularMeses(fechaInicioInput, fechaFinInput, mesesCondonacionInput) {
        const fechaInicioVal = fechaInicioInput.value;
        const fechaFinVal = fechaFinInput.value;
        
        console.log('Valores:', {fechaInicioVal, fechaFinVal});
        
        if (fechaInicioVal && fechaFinVal) {
            const fechaInicio = new Date(fechaInicioVal);
            const fechaFin = new Date(fechaFinVal);
            
            if (fechaInicio > fechaFin) {
                mesesCondonacionInput.value = 'Inválido';
                return;
            }

            let meses = (fechaFin.getFullYear() - fechaInicio.getFullYear()) * 12;
            meses += fechaFin.getMonth() - fechaInicio.getMonth();
            
            // Ajuste por días
            if (fechaFin.getDate() < fechaInicio.getDate()) {
                meses--;
            }

            mesesCondonacionInput.value = meses > 0 ? meses : 0;
            console.log('Resultado:', meses);
        } else {
            mesesCondonacionInput.value = '';
        }
    }

    
        // Configurar eventos para todas las filas
    document.querySelectorAll('.fila-condonacion').forEach(fila => {
        const fechaInicioInput = fila.querySelector('.fecha-inicio');
        const fechaFinInput = fila.querySelector('.fecha-fin');
        const mesesInput = fila.querySelector('.meses-condonacion');

        const calcularFechaFin = () => {
            if (!fechaInicioInput.value || fechaInicioInput.disabled) {
                // Si la fecha inicio está vacía o deshabilitada, reiniciar fecha fin
                fechaFinInput.value = '';
                return;
            }

            if (!mesesInput.value) {
                fechaFinInput.value = '';
                return;
            }

            const fechaInicio = new Date(fechaInicioInput.value);
            const meses = parseInt(mesesInput.value) || 0;

            // Calcular nueva fecha fin
            const nuevaFecha = new Date(fechaInicio);
            nuevaFecha.setMonth(nuevaFecha.getMonth() + meses);

            // Ajustar día si es necesario (ej: 31 de enero + 1 mes)
            if (nuevaFecha.getDate() !== fechaInicio.getDate()) {
                nuevaFecha.setDate(0); // Último día del mes anterior
            }

            // Formatear a YYYY-MM-DD
            const year = nuevaFecha.getFullYear();
            const month = String(nuevaFecha.getMonth() + 1).padStart(2, '0');
            const day = String(nuevaFecha.getDate()).padStart(2, '0');

            fechaFinInput.value = `${year}-${month}-${day}`;
        };

        // Eventos para cambios
        fechaInicioInput.addEventListener('change', calcularFechaFin);
        mesesInput.addEventListener('input', calcularFechaFin);

        // Detectar si la fecha inicio se deshabilita
        fechaInicioInput.addEventListener('input', () => {
            if (fechaInicioInput.disabled) {
                fechaFinInput.value = ''; // Reiniciar fecha fin si fecha inicio está deshabilitada
            }
        });
    });

    // calcular valor capacitacion
    document.querySelectorAll('.fila-condonacion').forEach(fila => {
        const valorPagareInput = fila.querySelector('.valor-pagare');
        const ejecucionInput = fila.querySelector('.ejecucion');
        const valorCapacitacionInput = fila.querySelector('.valor-capacitacion');

        const calcularCapacitacion = () => {
            const valorPagare = parseFloat(valorPagareInput.value) || 0;
            const porcentajeEjecucion = parseFloat(ejecucionInput.value) || 0;
            
            // Validar porcentaje (0-100)
            if (porcentajeEjecucion < 0 || porcentajeEjecucion > 100) {
                valorCapacitacionInput.value = 'Error: % inválido';
                return;
            }

            // Calcular valor (valor * porcentaje)
            const valor = valorPagare * (porcentajeEjecucion / 100);
            valorCapacitacionInput.value = valor.toLocaleString('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 2
            });
        };

        // Escuchar cambios en ambos inputs
        valorPagareInput.addEventListener('input', calcularCapacitacion);
        ejecucionInput.addEventListener('input', calcularCapacitacion);
    });


    //funcion calcular horas, ejecutadas, planeadas
    function calcularTotalPlaneado() {
        document.querySelectorAll('.card.mb-4').forEach(empleadoCard => {
            const inputsHoras = empleadoCard.querySelectorAll('.horas-planeadas');
            const totalPlaneado = empleadoCard.querySelector('.total-planeado');
            
            if (totalPlaneado) {
                let total = 0;
                inputsHoras.forEach(input => total += parseFloat(input.value) || 0);
                totalPlaneado.value = total.toFixed(2);
            }
        });
    }
    
    // Calcular inicialmente
    calcularTotalPlaneado();

    // Función para calcular total ejecutado
    function calcularTotalEjecutado() {
        document.querySelectorAll('.card.mb-4').forEach(empleadoCard => {
            const inputsEjecutadas = empleadoCard.querySelectorAll('.horas-ejecutadas');
            const totalEjecutado = empleadoCard.querySelector('.total-ejecutado');
            
            if (totalEjecutado) {
                let total = 0;
                inputsEjecutadas.forEach(input => {
                    // Tratar campos vacíos como 0
                    const valor = input.value.trim() === "" ? 0 : parseFloat(input.value) || 0;
                    total += valor;
                });
                totalEjecutado.value = total.toFixed(2);
            }
        });
    }

    // Event listeners para ejecutado
    document.querySelectorAll('.horas-planeadas, .horas-ejecutadas').forEach(input => {
        input.addEventListener('input', () => {
            calcularTotalPlaneado();
            calcularTotalEjecutado();
            calcularPorcentajeEjecucion();
        });
    });

    // Calcular inicialmente
    calcularTotalEjecutado();

    function calcularPorcentajeEjecucion() {
        document.querySelectorAll('.card.mb-4').forEach(empleadoCard => {
            const totalPlaneado = empleadoCard.querySelector('.total-planeado');
            const totalEjecutado = empleadoCard.querySelector('.total-ejecutado');
            const porcentajeEjecucion = empleadoCard.querySelector('.ejecucion');
    
            if (totalPlaneado && totalEjecutado && porcentajeEjecucion) {
                const planeado = parseFloat(totalPlaneado.value) || 0;
                const ejecutado = parseFloat(totalEjecutado.value) || 0;
                const porcentaje = planeado > 0 ? (ejecutado / planeado) * 100 : 0;
                
                porcentajeEjecucion.value = porcentaje.toFixed(2) + '%';
            }
        });
    }
    
    // Ejecutar al cargar la página
    window.addEventListener('load', () => {
        calcularPorcentajeEjecucion();
    });

    document.querySelectorAll('.card.mb-4').forEach(empleadoCard => {
        empleadoCard.querySelectorAll('.horas-planeadas, .horas-ejecutadas').forEach(input => {
            input.addEventListener('input', () => {
                calcularTotalPlaneado();
                calcularTotalEjecutado();
                calcularPorcentajeEjecucion();
            });
        });
    });

    // Para cada tarjeta de empleado
    document.querySelectorAll('.tarjeta-empleado').forEach(tarjeta => {
        const horasPlaneadas = tarjeta.querySelectorAll('.horas-planeadas');
        const horasEjecutadas = tarjeta.querySelectorAll('.horas-ejecutadas');
        const totalPlaneado = tarjeta.querySelector('.total-planeado');
        const totalEjecutado = tarjeta.querySelector('.total-ejecutado');
        const porcentajeEjecucion = tarjeta.querySelector('.porcentaje-ejecucion');
        const fechaInicio = tarjeta.querySelector('.fecha-inicio');

        function calcularTotal(campos, salida) {
            let total = 0;
            campos.forEach(input => {
                const valor = parseFloat(input.value) || 0;
                total += valor;
            });
            salida.value = total;
        }

        function actualizarEstadoPorcentaje() {
            if (!totalPlaneadoInput || !totalEjecutadoInput || !porcentajeEjecucion || !fechaInicio) {
                // Al menos uno de los elementos no existe, evita romper la ejecución
                console.warn('⛔ No se encontraron todos los elementos necesarios para actualizarEstado()');
                return;
            }
            const totalPlan = parseFloat(totalPlaneado.value) || 0;
            const totalEj = parseFloat(totalEjecutado.value) || 0;

            if (totalPlan === 0) {
                porcentajeEjecucion.value = "0%";
                fechaInicio.disabled = true;
                fechaInicio.value = '';
                return;
            }

            const porcentaje = Math.round((totalEj / totalPlan) * 100);
            porcentajeEjecucion.value = `${porcentaje}%`;

            if (porcentaje === 100) {
                fechaInicio.disabled = false;
            } else {
                fechaInicio.disabled = true;
                fechaInicio.value = '';
            }
        }

        horasPlaneadas.forEach(input => {
            input.addEventListener('input', () => {
                calcularTotal(horasPlaneadas, totalPlaneado);
                actualizarEstadoPorcentaje();
            });
        });

        horasEjecutadas.forEach(input => {
            input.addEventListener('input', () => {
                calcularTotal(horasEjecutadas, totalEjecutado);
                actualizarEstadoPorcentaje();
            });
        });

        // Al cargar la página
        calcularTotal(horasPlaneadas, totalPlaneado);
        calcularTotal(horasEjecutadas, totalEjecutado);
        actualizarEstadoPorcentaje();
    });

    //****************************/



    // Función para calcular totales
    function calcularTotales(documento) {
        const card = document.querySelector(`.card[data-doc="${documento}"]`);
        if (!card) return;

        // Calcular total planeado
        let totalPlaneado = 0;
        card.querySelectorAll('.horas-planeadas').forEach(input => {
            totalPlaneado += parseFloat(input.value) || 0;
        });
        card.querySelector('.total-planeado').value = totalPlaneado.toFixed(2);

        // Calcular total ejecutado
        let totalEjecutado = 0;
        card.querySelectorAll('.horas-ejecutadas').forEach(input => {
            totalEjecutado += parseFloat(input.value) || 0;
        });
        card.querySelector('.total-ejecutado').value = totalEjecutado.toFixed(2);

        // Calcular porcentaje de ejecución
        const porcentaje = totalPlaneado > 0 ? (totalEjecutado / totalPlaneado) * 100 : 0;
        card.querySelector('.ejecucion').value = porcentaje.toFixed(2) + '%';

        const fechaInicio = card.querySelector('.fecha-inicio');
        if (totalPlaneado === 0 || porcentaje < 100) {
            fechaInicio.disabled = true;
            fechaInicio.value = '';
        } else {
            fechaInicio.disabled = false;
        }


        const valorPagareInput = card.querySelector('.valor-pagare');
        const valorCapacitacionInput = card.querySelector('.valor-capacitacion');

        if (valorPagareInput && valorCapacitacionInput) {
            const valorPagare = parseFloat(valorPagareInput.value) || 0;
            const valorCapacitacion = valorPagare * (porcentaje / 100);
            valorCapacitacionInput.value = valorCapacitacion.toLocaleString('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 2
            });
        }
    }

    

    // Evento delegado para inputs dinámicos
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('horas-planeadas') || e.target.classList.contains('horas-ejecutadas')) {
            const documento = e.target.closest('.card').dataset.doc;
            calcularTotales(documento);
        }
    });


    document.querySelectorAll('.valor-pagare').forEach(input => {
        input.addEventListener('input', () => {
            const documento = input.dataset.documento;
            calcularTotales(documento);
        });
    });



    //***********************************************************/
        




    ///*****************************agregar actividades**************** */

    document.querySelectorAll('.btn-agregar-actividades').forEach(btn => {
        btn.addEventListener('click', function() {
            const documento = this.dataset.documento;
            const card = this.closest('.card');
            const checkboxes = card.querySelectorAll('.actividad-checkbox:checked');
    
            checkboxes.forEach(checkbox => {
                const actividadId = checkbox.value;
                const actividadNombre = checkbox.dataset.nombre;
                
                if (!card.querySelector(`#actividades-${documento} tr[data-actividad-id="${actividadId}"]`)) {
                    const newRow = document.createElement('tr');
                    newRow.dataset.actividadId = actividadId;
                    newRow.innerHTML = `
                        <td>${actividadNombre}</td>
                        <td>
                            <input type="number" 
                                   class="form-control horas-planeadas" 
                                   name="horas_${documento}_${actividadId}"
                                   value="">
                        </td>
                        <td>
                            <button class="btn btn-danger btn-sm btn-remover">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    card.querySelector(`#actividades-${documento}`).appendChild(newRow);
                }
                
                // Forzar actualización
                actualizarEstado();
            });
    
            checkboxes.forEach(cb => cb.checked = false);
            actualizarEstado(documento);
            sincronizarEjecutado(documento);
        });
    });


    //agregar acctividades a la tabla pagare ejecutado
    document.querySelectorAll('.btn-agregar-ejecutado').forEach(btn => {
        btn.addEventListener('click', function() {
            const documento = this.dataset.documento;
            const card = this.closest('.card');
            const checkboxes = card.querySelectorAll('.actividad-ejecutado-checkbox:checked');
    
            checkboxes.forEach(checkbox => {
                const actividadId = checkbox.value;
                const actividadNombre = checkbox.dataset.nombre;
                
                
                const tablaEjecutado = card.querySelector(`#ejecutado-${documento}`);
                
                if (!tablaEjecutado.querySelector(`tr[data-actividad-id="${actividadId}"]`)) {
                    const newRow = document.createElement('tr');
                    newRow.dataset.actividadId = actividadId;
                    newRow.classList.add('fila-ejecutado');
                    newRow.innerHTML = `
                        <td>${actividadNombre}</td>
                        <td>
                            <input type="number" 
                                   class="form-control horas-ejecutadas" 
                                   name="horas_ejecutadas_${documento}_${actividadId}"
                                   value="">
                        </td>
                        <td>
                            <button class="btn btn-danger btn-sm btn-remover-ejecutado">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    `;
                    tablaEjecutado.appendChild(newRow);
                }
    
                actualizarEstado();
            });
    
            checkboxes.forEach(cb => cb.checked = false);
            actualizarTotalEjecutado(documento);
        });
    });
    
    
    //evento de eliminacion tabla pagare ejecutado
    // Eliminar filas (Versión Corregida)
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-remover-ejecutado')) {
            const row = e.target.closest('tr');
            const tablaEjecutado = row.closest('tbody');
            const documento = tablaEjecutado.id.split('-')[1]; // Obtener documento del ID
            
            row.remove();
            actualizarTotalEjecutado(documento);
        }
    });

    // Función para actualizar totales (Ejemplo)
    function actualizarTotalEjecutado(documento) {
        const totalInput = document.querySelector(`#total-ejecutado-${documento}`);
        const horas = Array.from(document.querySelectorAll(`#ejecutado-${documento} .horas-ejecutadas`))
                        .reduce((sum, input) => sum + (parseFloat(input.value) || 0), 0);
        totalInput.value = horas;
    }
            
    
    // evento de eliminación tabla pagare planeado
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-remover')) {
            const row = e.target.closest('tr');
            const documento = row.closest('.card').dataset.doc;
            
            // Eliminar de ambas tablas
            const actividadId = row.dataset.actividadId;
            row.remove();
            document.querySelector(`#ejecutado-${documento} tr[data-actividad-id="${actividadId}"]`)?.remove();
            
            // Actualizar totales
            calcularTotales(documento);

            actualizarEstado(documento);
        }
    });
        

        // Función mejorada para actualizar estado
        function actualizarEstado(documento) {
            const card = document.querySelector(`.card[data-doc="${documento}"]`);
            if (!card) return;
        
            const elementos = {
                tbody: card.querySelector(`#actividades-${documento}`),
                tfoot: card.querySelector('tfoot'),
                noActividades: card.querySelector('.no-actividades')
            };
        
            const tieneActividades = elementos.tbody?.querySelectorAll('tr[data-actividad-id]').length > 0;
        
            // Control de visibilidad, con verificación
            if (elementos.tfoot) {
                elementos.tfoot.style.display = tieneActividades ? '' : 'none';
            }
        
            if (elementos.noActividades) {
                elementos.noActividades.style.display = tieneActividades ? 'none' : '';
            }
        }
        
        





        // Función principal de sincronización
        function sincronizarEjecutado(documento) {
            const card = document.querySelector(`.card[data-doc="${documento}"]`);
            if (!card) return;
        
            const tbodyPlaneado = card.querySelector(`#actividades-${documento}`);
            const tbodyEjecutado = card.querySelector(`#ejecutado-${documento}`);
            
            // Obtener actividades actuales
            const actividades = Array.from(tbodyPlaneado.querySelectorAll('tr[data-actividad-id]')).map(tr => ({
                id: tr.dataset.actividadId,
                nombre: tr.querySelector('td:first-child').textContent.trim(),
                horas: tr.querySelector('.horas-planeadas').value
            }));
        
            // Reconstruir ejecutado
            tbodyEjecutado.innerHTML = '';
            actividades.forEach(act => {
                const row = document.createElement('tr');
                row.dataset.actividadId = act.id;
                row.innerHTML = `
                    <td>${act.nombre}</td>
                    <td>
                        <input type="number" 
                               class="form-control horas-ejecutadas" 
                               name="ejecutado_${documento}_${act.id}"
                               value="0"
                               data-actividad-id="${act.id}">
                    </td>
                `;
                tbodyEjecutado.appendChild(row);
            });
            
            calcularTotales(documento); // Actualizar totales después de sincronizar
        }

        //funcion crear fila tabla
        function crearFilaPlaneado(documento, id, nombre) {
            const tr = document.createElement('tr');
            tr.dataset.actividadId = id;
            tr.innerHTML = `
                <td>${nombre}</td>
                <td>
                    <input type="number" 
                        name="horas_${documento}_${id}" 
                        class="form-control horas-planeadas" 
                        value="0">
                </td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm btn-remover">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            return tr;
        }


        //funcion para guardar los datos de pagare
        window.guardarPagare = function() {
            mostrarMensaje('Creando Pagare');
            const pagaresData = [];
            let todoCorrecto = true;
            
            // Recorrer cada empleado/card
            document.querySelectorAll('.card[data-doc]').forEach(card => {
                const doc = card.dataset.doc;
                console.log(`Procesando empleado: ${doc}`);
                

                
                // 1. Elementos obligatorios
                const elementosObligatorios = {
                    tipo_pagare: card.querySelector(`[name="tipo_pagare_${doc}"]`),
                    fecha_creacion: card.querySelector(`#fecha_creacion_${doc}`),
                    valor_pagare: card.querySelector('.valor-pagare'),
                    estado: card.querySelector(`[name="estado_${doc}"]`),
                    meses_condonacion: card.querySelector('.meses-condonacion'),
                    descripcion:card.querySelector(`#descripcion_${doc}`),
                };
                

                // Verificar que existen
                if (Object.values(elementosObligatorios).some(el => !el)) {
                    mostrarMensaje('Faltan campos obligatorios: Tipo Pagare, Valor Pagare, Estado, Meses condonación ' + doc);
                    todoCorrecto = false;
                    return;
                }

                // VALIDACIÓN: verificar que todos los campos obligatorios estén presentes y llenos
                if (!elementosObligatorios.tipo_pagare?.value || 
                    !elementosObligatorios.fecha_creacion?.value || 
                    !elementosObligatorios.valor_pagare?.value || 
                    !elementosObligatorios.meses_condonacion?.value ||
                    !elementosObligatorios.descripcion?.value ||
                    !elementosObligatorios.estado?.value) {

                    console.log('Campos vacíos en:', {
                        tipo_pagare: elementosObligatorios.tipo_pagare?.value,
                        fecha_creacion: elementosObligatorios.fecha_creacion?.value,
                        valor_pagare: elementosObligatorios.valor_pagare?.value,
                        meses_condonacion: elementosObligatorios.meses_condonacion?.value,
                        estado: elementosObligatorios.estado?.value,
                        descripcion: elementosObligatorios.descripcion?.value
                    });

                    mostrarMensaje(`Faltan campos obligatorios para el documento ${doc}. Verifica Tipo Pagaré, Fecha Creación, Valor Pagaré, Meses condonación, Descripción y Estado.`);
                    todoCorrecto = false;
                    return;
                }

                // Verificar que haya al menos una actividad planeada
                const actividadesPlaneadas = card.querySelectorAll(`#actividades-${doc} tr[data-actividad-id]`);
                if (actividadesPlaneadas.length === 0) {
                    mostrarMensaje(`Debe ingresar al menos una actividad planeada para el documento ${doc}`);
                    todoCorrecto = false;
                    return;
                }


                const pagareData = {
                    documento: doc,
                    general: {
                        fecha_creacion: elementosObligatorios.fecha_creacion.value,
                        tipo_pagare: elementosObligatorios.tipo_pagare.value,
                        descripcion: elementosObligatorios.descripcion.value,
                        fecha_inicio: card.querySelector('.fecha-inicio')?.value || null,
                        fecha_fin:card.querySelector('.fecha-fin')?.value || null,
                        meses_condonacion: elementosObligatorios.meses_condonacion.value,                        
                        valor_pagare:elementosObligatorios.valor_pagare.value,
                        estado: elementosObligatorios.estado.value,
                        ejecucion: card.querySelector(`#ejecucion_${doc}`)?.value || null
                    },
                    planeado: [],
                    ejecutado: []
                };
        
                // Recoger actividades planeadas
                card.querySelectorAll('#actividades-' + doc + ' tr[data-actividad-id]').forEach(row => {
                    const actividadId = row.dataset.actividadId;
                    pagareData.planeado.push({
                        actividad_id: actividadId,
                        horas: row.querySelector('.horas-planeadas').value
                    });
                });
        
                // Recoger actividades ejecutadas
                card.querySelectorAll('#ejecutado-' + doc + ' tr[data-actividad-id]').forEach(row => {
                    const actividadId = row.dataset.actividadId;
                    pagareData.ejecutado.push({
                        actividad_id: actividadId,
                        horas: row.querySelector('.horas-ejecutadas').value
                    });
                });
        
                pagaresData.push(pagareData);
            });


            if (!todoCorrecto) {
                console.warn('Validaciones fallidas. Deteniendo guardado.');
                return;
            }

            // Antes del fetch, agrega:
            console.log('Datos a enviar:', JSON.stringify(pagaresData, null, 2));

            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
            // Enviar datos al servidor
            fetch('/guardar_pagare/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(pagaresData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.estado === 'exito') {
                    mostrarMensaje('¡Datos guardados correctamente!');
                    window.location.reload();
                } else {
                    mostrarMensaje('Error: ' + data.mensaje);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarMensaje('Error de conexión con el servidor');
            });
        }


        document.querySelectorAll('.btn-guardar-pagare').forEach(btn => {
            btn.addEventListener('click', window.guardarPagare);
        });

        function mostrarMensaje(texto) {
            let contenedor = document.getElementById('mensaje-alerta');
        
            // Si no existe, lo creamos
            if (!contenedor) {
                contenedor = document.createElement('div');
                contenedor.id = 'mensaje-alerta';
                document.body.appendChild(contenedor);
            }
        
            // Estilos inline desde JS para ventana flotante
            contenedor.style.position = 'fixed';
            contenedor.style.top = '50%';
            contenedor.style.left = '50%';
            contenedor.style.transform = 'translate(-50%, -50%)';
            contenedor.style.backgroundColor = '#fff';
            contenedor.style.border = '2px solid #007bff';
            contenedor.style.padding = '20px 30px';
            contenedor.style.zIndex = '9999';
            contenedor.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.3)';
            contenedor.style.borderRadius = '10px';
            contenedor.style.fontSize = '16px';
            contenedor.style.color = '#333';
            contenedor.style.maxWidth = '90%';
            contenedor.style.textAlign = 'center';
        
            contenedor.textContent = texto;
            contenedor.style.display = 'block';
        
            // Cierre automático a los 4 segundos
            setTimeout(() => {
                contenedor.style.display = 'none';
            }, 5000);
        }

        function mostrarConfirmacion(mensaje, callbackAceptar, callbackCancelar) {
            // Crear contenedor si no existe
            let contenedor = document.getElementById('mensaje-confirmacion');
        
            if (!contenedor) {
                contenedor = document.createElement('div');
                contenedor.id = 'mensaje-confirmacion';
                document.body.appendChild(contenedor);
            }
        
            // Estilos similares a mostrarMensaje
            contenedor.style.position = 'fixed';
            contenedor.style.top = '50%';
            contenedor.style.left = '50%';
            contenedor.style.transform = 'translate(-50%, -50%)';
            contenedor.style.backgroundColor = '#fff';
            contenedor.style.border = '2px solid #007bff';
            contenedor.style.padding = '20px 30px';
            contenedor.style.zIndex = '9999';
            contenedor.style.boxShadow = '0 0 20px rgba(0, 0, 0, 0.3)';
            contenedor.style.borderRadius = '10px';
            contenedor.style.fontSize = '16px';
            contenedor.style.color = '#333';
            contenedor.style.maxWidth = '90%';
            contenedor.style.textAlign = 'center';
        
            // Contenido HTML con botones
            contenedor.innerHTML = `
                <p style="margin-bottom: 20px;">${mensaje}</p>
                <button id="btn-confirmar" style="margin-right: 10px; padding: 6px 16px; background-color: #007bff; color: #fff; border: none; border-radius: 5px;">Sí</button>
                <button id="btn-cancelar" style="padding: 6px 16px; background-color: #ccc; border: none; border-radius: 5px;">Cancelar</button>
            `;
        
            // Mostrar contenedor
            contenedor.style.display = 'block';
        
            // Listeners para los botones
            document.getElementById('btn-confirmar').addEventListener('click', () => {
                contenedor.style.display = 'none';
                callbackAceptar();
            });
        
            document.getElementById('btn-cancelar').addEventListener('click', () => {
                contenedor.style.display = 'none';
                if (callbackCancelar) callbackCancelar();
            });
        }
        
        




});