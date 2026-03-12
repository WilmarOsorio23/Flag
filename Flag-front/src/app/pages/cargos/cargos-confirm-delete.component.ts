import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-cargos-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './cargos-confirm-delete.component.html',
  styleUrls: ['./cargos-confirm-delete.component.css'],
})
export class CargosConfirmDeleteComponent {
  @Input() itemIds: number[] = [];

  confirm() {
    // TODO: perform delete
  }
}
