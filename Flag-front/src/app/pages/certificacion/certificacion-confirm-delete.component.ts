import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-certificacion-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './certificacion-confirm-delete.component.html',
  styleUrls: ['./certificacion-confirm-delete.component.css'],
})
export class CertificacionConfirmDeleteComponent {
  @Input() itemIds: number[] = [];

  confirm() {
    // TODO: perform delete
  }
}
