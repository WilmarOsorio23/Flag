import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

interface CentroCosto {
  CentroCostoId: number;
  Descripcion: string;
}

@Component({
  selector: 'app-centros-costos-index',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './centros-costos-index.component.html',
  styleUrls: ['./centros-costos-index.component.css'],
})
export class CentrosCostosIndexComponent implements OnInit {
  centros: CentroCosto[] = [];
  selectedIds = new Set<number>();
  originalValues: { [id: number]: string } = {};

  constructor(private router: Router) {}

  ngOnInit(): void {
    // TODO: load centros costos from backend
  }

  toggleSelectAll(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedIds.clear();
    if (checked) {
      this.centros.forEach(c => this.selectedIds.add(c.CentroCostoId));
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
    const centro = this.centros.find(c => c.CentroCostoId === id);
    if (!centro) return;
    this.originalValues[id] = centro.Descripcion;
    centro['editing'] = true;
  }

  cancelEdit() {
    if (this.selectedIds.size !== 1) return;
    const id = Array.from(this.selectedIds)[0];
    const centro = this.centros.find(c => c.CentroCostoId === id);
    if (!centro) return;
    centro.Descripcion = this.originalValues[id] || centro.Descripcion;
    centro['editing'] = false;
    this.selectedIds.delete(id);
  }

  saveRow(centro: CentroCosto) {
    // TODO: send request to backend
    centro['editing'] = false;
    this.selectedIds.delete(centro.CentroCostoId);
  }

  deleteSelected() {
    if (this.selectedIds.size === 0) {
      alert('No has seleccionado ningún elemento para eliminar.');
      return;
    }
    // TODO: delete call
  }

  downloadSelected() {
    if (this.selectedIds.size === 0) {
      alert('¡Selecciona al menos un centro para descargar!');
      return;
    }
    // TODO: download call
  }

  goToCreate() {
    this.router.navigate(['/centros-costos/crear']);
  }
}
