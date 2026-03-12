import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-centros-costos-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './centros-costos-form.component.html',
  styleUrls: ['./centros-costos-form.component.css'],
})
export class CentrosCostosFormComponent {
  form = this.fb.group({
    CentroCostoId: ['', Validators.required],
    Descripcion: ['', Validators.required],
  });

  constructor(private fb: FormBuilder, private router: Router) {}

  onSubmit() {
    if (this.form.invalid) return;
    // TODO: enviar datos al backend
    this.router.navigate(['/centros-costos']);
  }
}
