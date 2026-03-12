import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

interface Actividad {
  Act_PagareId: number;
  Descripcion_Act: string;
}

@Component({
  selector: 'app-act-maestro-index',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './act-maestro-index.component.html',
  styleUrls: ['./act-maestro-index.component.css'],
})
export class ActMaestroIndexComponent implements OnInit {
  actividades: Actividad[] = [];
  selectedIds = new Set<number>();
  originalValues: { [id: number]: string } = {};

  constructor(private router: Router) {}

  ngOnInit(): void {
    // TODO: cargar actividades desde la API
  }

  toggleSelectAll(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedIds.clear();
    if (checked) {
      this.actividades.forEach(a => this.selectedIds.add(a.Act_PagareId));
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
    const actividad = this.actividades.find(a => a.Act_PagareId === id);
    if (!actividad) return;
    this.originalValues[id] = actividad.Descripcion_Act;
    actividad['editing'] = true;
  }

  cancelEdit() {
    if (this.selectedIds.size !== 1) return;
    const id = Array.from(this.selectedIds)[0];
    const actividad = this.actividades.find(a => a.Act_PagareId === id);
    if (!actividad) return;
    actividad.Descripcion_Act = this.originalValues[id] || actividad.Descripcion_Act;
    actividad['editing'] = false;
    this.selectedIds.delete(id);
  }

  saveRow(actividad: Actividad) {
    // TODO: realizar petición al backend
    actividad['editing'] = false;
    this.selectedIds.delete(actividad.Act_PagareId);
  }

  deleteSelected() {
    if (this.selectedIds.size === 0) {
      alert('No has seleccionado ningún elemento para eliminar.');
      return;
    }
    // TODO: llamada delete
  }

  downloadSelected() {
    if (this.selectedIds.size === 0) {
      alert('¡Selecciona al menos una actividad para descargar!');
      return;
    }
    // TODO: llamada descarga
  }

  goToCreate() {
    this.router.navigate(['/act-maestro/crear']);
  }
}
