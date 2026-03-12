import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { HttpClient, HttpErrorResponse, HttpClientModule } from '@angular/common/http';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    HttpClientModule,
  ],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent {
  errorMessage = '';
  nextParam = '/';

  loginForm = this.fb.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
  });

  constructor(
    private fb: FormBuilder,
    private http: HttpClient,
    private router: Router
  ) {
    const params = new URLSearchParams(window.location.search);
    this.nextParam = params.get('next') || '/';
  }

  onSubmit() {
    if (!this.loginForm.valid) {
      return;
    }

    this.errorMessage = '';

    this.http
      .post('/login/', this.loginForm.value, { observe: 'response' })
      .subscribe({
        next: (res) => {
          if (res.status === 200 || res.status === 302) {
            this.router.navigateByUrl(this.nextParam);
          }
        },
        error: (err: HttpErrorResponse) => {
          // show generic error
          this.errorMessage =
            'Usuario/Email o contraseña incorrectos.';
        },
      });
  }
}
