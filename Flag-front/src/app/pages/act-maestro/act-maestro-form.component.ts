import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-act-maestro-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './act-maestro-form.component.html',
  styleUrls: ['./act-maestro-form.component.css'],
})
export class ActMaestroFormComponent {
  form = this.fb.group({
    Act_PagareId: ['', Validators.required],
    Descripcion_Act: ['', Validators.required],
  });

  constructor(private fb: FormBuilder, private router: Router) {}

  onSubmit() {
    if (this.form.invalid) return;
    // TODO: enviar datos al backend
    this.router.navigate(['/act-maestro']);
  }
}
