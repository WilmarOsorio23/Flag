import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-centros-costos-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './centros-costos-confirm-delete.component.html',
  styleUrls: ['./centros-costos-confirm-delete.component.css'],
})
export class CentrosCostosConfirmDeleteComponent {
  @Input() itemIds: number[] = [];

  confirm() {
    // TODO: perform delete
  }
}
