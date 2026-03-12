import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-clientes-contratos-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './clientes-contratos-form.component.html',
  styleUrls: ['./clientes-contratos-form.component.css'],
})
export class ClientesContratosFormComponent {
  form = this.fb.group({
    ClienteContratoId: ['', Validators.required],
    Descripcion: ['', Validators.required],
  });

  constructor(private fb: FormBuilder, private router: Router) {}

  onSubmit() {
    if (this.form.invalid) return;
    // TODO: enviar datos al backend
    this.router.navigate(['/clientes-contratos']);
  }
}
