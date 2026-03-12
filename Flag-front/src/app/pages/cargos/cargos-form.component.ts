import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-cargos-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cargos-form.component.html',
  styleUrls: ['./cargos-form.component.css'],
})
export class CargosFormComponent {
  form = this.fb.group({
    CargoId: ['', Validators.required],
    Descripcion: ['', Validators.required],
  });

  constructor(private fb: FormBuilder, private router: Router) {}

  onSubmit() {
    if (this.form.invalid) return;
    // TODO: enviar datos al backend
    this.router.navigate(['/cargos']);
  }
}
