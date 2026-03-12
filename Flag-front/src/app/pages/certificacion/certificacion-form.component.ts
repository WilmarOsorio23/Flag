import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-certificacion-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './certificacion-form.component.html',
  styleUrls: ['./certificacion-form.component.css'],
})
export class CertificacionFormComponent {
  form = this.fb.group({
    CertificacionId: ['', Validators.required],
    Descripcion: ['', Validators.required],
  });

  constructor(private fb: FormBuilder, private router: Router) {}

  onSubmit() {
    if (this.form.invalid) return;
    // TODO: enviar datos al backend
    this.router.navigate(['/certificacion']);
  }
}
