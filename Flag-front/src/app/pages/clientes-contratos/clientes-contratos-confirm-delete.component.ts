import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-clientes-contratos-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './clientes-contratos-confirm-delete.component.html',
  styleUrls: ['./clientes-contratos-confirm-delete.component.css'],
})
export class ClientesContratosConfirmDeleteComponent {
  @Input() itemIds: number[] = [];

  confirm() {
    // TODO: perform delete
  }
}
