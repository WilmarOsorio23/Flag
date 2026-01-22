function toggleSidebar() {
    document.querySelector("#sidebar .sidebar-header").classList.toggle("collapsive");
    document.querySelector(".sidebar-item-principal").classList.toggle("collapsive");
    document.querySelector("#sidebar").classList.toggle("collapsive");
    document.querySelector(".toggle-btn").classList.toggle("collapsive");
    document.querySelector("#Inicio").classList.toggle("collapsive");
    document.querySelector(".img-fluid").classList.toggle("collapsive");
    document.querySelector(".img-icon").classList.toggle("collapsive");
    document.querySelectorAll("#sidebar ul li a").forEach(link => {link.classList.toggle("collapsive");});
    let toggle = document.querySelector('#sidebar ul li a'); // Selecciona el enlace
}

function removeCollapsive() {
    let sidebar = document.querySelector("#sidebar");
    let sidebar_item_principal =document.querySelector(".sidebar-item-principal");
    let Inicio = document.querySelector("#Inicio");
    let sidebar_header = document.querySelector(".img-fluid");
    let accordions = document.querySelectorAll("#sidebar ul li a")
    let icon = document.querySelector(".img-icon")
    if (sidebar.classList.contains("collapsive")) {
        sidebar.classList.remove("collapsive");
        Inicio.classList.remove("collapsive");
        icon.classList.remove("collapsive");
        sidebar_item_principal.classList.remove("collapsive");
        sidebar_header.classList.remove("collapsive");
        accordions.forEach(link => {link.classList.remove("collapsive");});
    }
}