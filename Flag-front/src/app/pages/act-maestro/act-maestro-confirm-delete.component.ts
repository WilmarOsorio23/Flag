import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-act-maestro-confirm-delete',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './act-maestro-confirm-delete.component.html',
  styleUrls: ['./act-maestro-confirm-delete.component.css'],
})
export class ActMaestroConfirmDeleteComponent {
  @Input() itemIds: number[] = [];

  confirm() {
    // TODO: perform delete
  }
}
