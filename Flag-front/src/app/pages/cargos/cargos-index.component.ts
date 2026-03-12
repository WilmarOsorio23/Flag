import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

interface Cargo {
  CargoId: number;
  Descripcion: string;
}

@Component({
  selector: 'app-cargos-index',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './cargos-index.component.html',
  styleUrls: ['./cargos-index.component.css'],
})
export class CargosIndexComponent implements OnInit {
  cargos: Cargo[] = [];
  selectedIds = new Set<number>();
  originalValues: { [id: number]: string } = {};

  constructor(private router: Router) {}

  ngOnInit(): void {
    // TODO: load cargos from backend
  }

  toggleSelectAll(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedIds.clear();
    if (checked) {
      this.cargos.forEach(c => this.selectedIds.add(c.CargoId));
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
    const cargo = this.cargos.find(c => c.CargoId === id);
    if (!cargo) return;
    this.originalValues[id] = cargo.Descripcion;
    cargo['editing'] = true;
  }

  cancelEdit() {
    if (this.selectedIds.size !== 1) return;
    const id = Array.from(this.selectedIds)[0];
    const cargo = this.cargos.find(c => c.CargoId === id);
    if (!cargo) return;
    cargo.Descripcion = this.originalValues[id] || cargo.Descripcion;
    cargo['editing'] = false;
    this.selectedIds.delete(id);
  }

  saveRow(cargo: Cargo) {
    // TODO: send request to backend
    cargo['editing'] = false;
    this.selectedIds.delete(cargo.CargoId);
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
      alert('¡Selecciona al menos un cargo para descargar!');
      return;
    }
    // TODO: download call
  }

  goToCreate() {
    this.router.navigate(['/cargos/crear']);
  }
}
