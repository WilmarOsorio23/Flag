import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Cliente } from '../../models/cliente';
import { ClientesService } from '../../services/clientes.service';

@Component({
  selector: 'app-clientes-index',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './clientes-index.component.html',
  styleUrls: ['./clientes-index.component.css'],
})
export class ClientesIndexComponent implements OnInit {
  clientes: Cliente[] = [];
  selectedIds = new Set<string>(); // composite key as string
  originalValues: { [key: string]: Partial<Cliente> } = {};

  constructor(
    private router: Router,
    private clientesService: ClientesService
  ) {}

  ngOnInit(): void {
    this.load();
  }

  load() {
    this.clientesService.getAll().subscribe((data) => {
      this.clientes = data;
    });
  }

  private makeKey(c: Cliente) {
    return `${c.TipoDocumentoID}-${c.DocumentoId}`;
  }

  toggleSelectAll(event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    this.selectedIds.clear();
    if (checked) {
      this.clientes.forEach(c => this.selectedIds.add(this.makeKey(c)));
    }
  }

  toggleSelection(cliente: Cliente, event: Event) {
    const checked = (event.target as HTMLInputElement).checked;
    const key = this.makeKey(cliente);
    if (checked) this.selectedIds.add(key);
    else this.selectedIds.delete(key);
  }

  enableEdit() {
    if (this.selectedIds.size !== 1) {
      alert('Selecciona solo un registro para editar.');
      return;
    }
    const key = Array.from(this.selectedIds)[0];
    const cliente = this.clientes.find(c => this.makeKey(c) === key);
    if (!cliente) return;
    this.originalValues[key] = { ...cliente };
    (cliente as any).editing = true;
  }

  cancelEdit() {
    if (this.selectedIds.size !== 1) return;
    const key = Array.from(this.selectedIds)[0];
    const cliente = this.clientes.find(c => this.makeKey(c) === key);
    if (!cliente) return;
    Object.assign(cliente, this.originalValues[key] || {});
    (cliente as any).editing = false;
    this.selectedIds.delete(key);
  }

  saveRow(cliente: Cliente) {
    // TODO: compute ID correctly for composite keys
    const id = cliente.DocumentoId as any;
    this.clientesService.update(id, cliente).subscribe(() => {
      (cliente as any).editing = false;
      this.selectedIds.delete(this.makeKey(cliente));
    });
  }

  deleteSelected() {
    if (this.selectedIds.size === 0) {
      alert('No has seleccionado ningún elemento para eliminar.');
      return;
    }
    // Here we simply delete the first selected for demo; adjust for multiple
    const key = Array.from(this.selectedIds)[0];
    const cliente = this.clientes.find(c => this.makeKey(c) === key);
    if (!cliente) return;
    const id = cliente.DocumentoId as any;
    this.clientesService.delete(id).subscribe(() => {
      this.load();
      this.selectedIds.clear();
    });
  }

  downloadSelected() {
    if (this.selectedIds.size === 0) {
      alert('¡Selecciona al menos un cliente para descargar!');
      return;
    }
    // TODO: download call
  }

  goToCreate() {
    this.router.navigate(['/clientes/crear']);
  }
}
