import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ClientesService } from '../../services/clientes.service';
import { Cliente } from '../../models/cliente';

@Component({
  selector: 'app-clientes-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './clientes-form.component.html',
  styleUrls: ['./clientes-form.component.css'],
})
export class ClientesFormComponent {
  editingId: string | null = null;
  form = this.fb.group({
    TipoDocumentoID: ['', Validators.required],
    DocumentoId: ['', Validators.required],
    Nombre_Cliente: ['', Validators.required],
    Activo: [true],
    Fecha_Inicio: ['', Validators.required],
    Fecha_Retiro: [''],
    Direccion: [''],
    Telefono: [''],
    CorreoElectronico: [''],
    BuzonFacturacion: [''],
    TipoCliente: [''],
    Ciudad: [''],
    Departamento: [''],
    Pais: [''],
    Nacional: [false],
    ContactoID: [''],
  });

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private clientesService: ClientesService
  ) {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.editingId = id;
      this.clientesService.get(id).subscribe((data) => {
        this.form.patchValue(data as any);
      });
    }
  }

  onSubmit() {
    if (this.form.invalid) return;
    const data: Cliente = this.form.value as Cliente;
    const navigateBack = () => this.router.navigate(['/clientes']);
    if (this.editingId) {
      this.clientesService.update(this.editingId, data).subscribe(navigateBack);
    } else {
      this.clientesService.create(data).subscribe(navigateBack);
    }
  }
}
