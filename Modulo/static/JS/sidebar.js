function toggleSidebar() {
    document.querySelector("#sidebar .sidebar-header").classList.toggle("collapsive");
    document.querySelector(".sidebar-item-principal").classList.toggle("collapsive");
    document.querySelector("#sidebar").classList.toggle("collapsive");
    document.querySelector("#Inicio").classList.toggle("collapsive");
    document.querySelectorAll("#sidebar ul li a").forEach(link => {link.classList.toggle("collapsive");});
    let toggle = document.querySelector('#sidebar ul li a'); // Selecciona el enlace
}

function removeCollapsive() {
    let sidebar = document.querySelector("#sidebar");
    let sidebar_item_principal =document.querySelector(".sidebar-item-principal");
    let Inicio = document.querySelector("#Inicio");
    let sidebar_header = document.querySelector("#sidebar .sidebar-header");
    let accordions = document.querySelectorAll("#sidebar ul li a")
    if (sidebar.classList.contains("collapsive")) {
        sidebar.classList.remove("collapsive");
        Inicio.classList.remove("collapsive");
        sidebar_item_principal.classList.remove("collapsive");
        sidebar_header.classList.remove("collapsive");
        accordions.forEach(link => {link.classList.remove("collapsive");});
    }
}