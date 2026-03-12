import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

interface Certificacion {
  CertificacionId: number;
  Descripcion: string;
}

@Component({
  selector: 'app-certificacion-index',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './certificacion-index.component.html',
  styleUrls: ['./certificacion-index.component.css'],
})
export class CertificacionIndexComponent implements OnInit {
  items: Certificacion[] = [];
  selectedIds = new Set<number>();
  originalValues: { [id: number]: string } = {};

  constructor(private router: Router) {}

  ngOnInit(): void {
    // TODO: cargar certificaciones desde el backend
  }

  toggleSelectAll(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedIds.clear();
    if (checked) {
      this.items.forEach(i => this.selectedIds.add(i.CertificacionId));
    }
  }

  toggleSelection(id: number, event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    if (checked) this.selectedIds.add(id);
    else this.selectedIds.delete(id);
  }

  enableEdit() {
    if (this.selectedIds.size !== 1) {
      alert('Selecciona solo un registro para editar.');
      return;
    }
    const id = Array.from(this.selectedIds)[0];
    const item = this.items.find(i => i.CertificacionId === id);
    if (!item) return;
    this.originalValues[id] = item.Descripcion;
    item['editing'] = true;
  }

  cancelEdit() {
    if (this.selectedIds.size !== 1) return;
    const id = Array.from(this.selectedIds)[0];
    const item = this.items.find(i => i.CertificacionId === id);
    if (!item) return;
    item.Descripcion = this.originalValues[id] || item.Descripcion;
    item['editing'] = false;
    this.selectedIds.delete(id);
  }

  saveRow(item: Certificacion) {
    // TODO: enviar petición al backend
    item['editing'] = false;
    this.selectedIds.delete(item.CertificacionId);
  }

  deleteSelected() {
    if (this.selectedIds.size === 0) {
      alert('No has seleccionado ningún elemento para eliminar.');
      return;
    }
    // TODO: llamada de eliminación
  }

  downloadSelected() {
    if (this.selectedIds.size === 0) {
      alert('¡Selecciona al menos un elemento para descargar!');
      return;
    }
    // TODO: llamada de descarga
  }

  goToCreate() {
    this.router.navigate(['/certificacion/crear']);
  }
}
