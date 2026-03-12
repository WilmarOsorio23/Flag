import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ClientesService } from '../../services/clientes.service';

@Component({
  selector: 'app-clientes-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './clientes-confirm-delete.component.html',
  styleUrls: ['./clientes-confirm-delete.component.css'],
})
export class ClientesConfirmDeleteComponent {
  @Input() clienteName = '';
  @Input() clienteId: string | null = null;
  @Output() deleted = new EventEmitter<void>();

  constructor(private clientesService: ClientesService) {}

  confirm() {
    if (this.clienteId) {
      this.clientesService.delete(this.clienteId).subscribe(() => {
        this.deleted.emit();
      });
    }
  }
}
