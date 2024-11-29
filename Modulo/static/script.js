document.addEventListener('DOMContentLoaded', function() {

    // Prevenir envío del formulario al presionar Enter en campos INPUT o TEXTAREA
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('keydown', function(event) {
            if (event.key === "Enter") {
                const activeElement = document.activeElement;
                if (activeElement.tagName === "INPUT" || activeElement.tagName === "TEXTAREA") {
                    event.preventDefault(); // Prevenir envío
                }
            }
        });
    });
});