document.addEventListener('DOMContentLoaded', function () {
    console.log("🟢 JS Informe Otros Sí activo");

    const clienteSelect = document.getElementById('id_Nombre_Cliente');
    const contratoSelect = document.getElementById('id_Contrato');

    if (!clienteSelect || !contratoSelect) {
        console.warn("⚠️ No se encontraron los campos Cliente o Contrato.");
        return;
    }

    clienteSelect.addEventListener('change', function () {
        const clienteId = this.value;  // ahora tomamos el ID directamente
        console.log("➡️ Cliente seleccionado:", clienteId);
    
        contratoSelect.innerHTML = '<option value="">Cargando contratos...</option>';
    
        if (clienteId) {
            fetch(`/contratos_otros_si/obtener-contratos/${clienteId}/`)
                .then(response => {
                    if (!response.ok) throw new Error("No se pudo obtener los contratos del cliente");
                    return response.json();
                })
                .then(data => {
                    console.log("📦 Contratos recibidos:", data);
                    contratoSelect.innerHTML = '<option value="">Seleccione un contrato</option>';
                    data.contratos.forEach(c => {
                        const option = document.createElement('option');
                        option.value = c.nombre;
                        option.textContent = c.nombre;
                        contratoSelect.appendChild(option);
                    });
                })
                .catch(error => {
                    console.error('❌ Error cargando contratos:', error);
                    contratoSelect.innerHTML = '<option value="">Error cargando contratos</option>';
                });
        } else {
            contratoSelect.innerHTML = '<option value="">Seleccione un cliente primero</option>';
        }
    });
});
