import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login.component';
import { ActMaestroIndexComponent } from './pages/act-maestro/act-maestro-index.component';
import { ActMaestroFormComponent } from './pages/act-maestro/act-maestro-form.component';
import { CargosIndexComponent } from './pages/cargos/cargos-index.component';
import { CargosFormComponent } from './pages/cargos/cargos-form.component';
import { CentrosCostosIndexComponent } from './pages/centros-costos/centros-costos-index.component';
import { CentrosCostosFormComponent } from './pages/centros-costos/centros-costos-form.component';
import { CertificacionIndexComponent } from './pages/certificacion/certificacion-index.component';
import { CertificacionFormComponent } from './pages/certificacion/certificacion-form.component';
import { ClientesIndexComponent } from './pages/clientes/clientes-index.component';
import { ClientesFormComponent } from './pages/clientes/clientes-form.component';
import { ClientesConfirmDeleteComponent } from './pages/clientes/clientes-confirm-delete.component';
import { ClientesContratosIndexComponent } from './pages/clientes-contratos/clientes-contratos-index.component';
import { ClientesContratosFormComponent } from './pages/clientes-contratos/clientes-contratos-form.component';

export const routes: Routes = [
  { path: '', redirectTo: 'login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'act-maestro', component: ActMaestroIndexComponent },
  { path: 'act-maestro/crear', component: ActMaestroFormComponent },
  { path: 'act-maestro/editar/:id', component: ActMaestroFormComponent },
  { path: 'cargos', component: CargosIndexComponent },
  { path: 'cargos/crear', component: CargosFormComponent },
  { path: 'cargos/editar/:id', component: CargosFormComponent },
  { path: 'centros-costos', component: CentrosCostosIndexComponent },
  { path: 'centros-costos/crear', component: CentrosCostosFormComponent },
  { path: 'centros-costos/editar/:id', component: CentrosCostosFormComponent },
  { path: 'certificacion', component: CertificacionIndexComponent },
  { path: 'certificacion/crear', component: CertificacionFormComponent },
  { path: 'certificacion/editar/:id', component: CertificacionFormComponent },
  { path: 'clientes', component: ClientesIndexComponent },
  { path: 'clientes/crear', component: ClientesFormComponent },
  { path: 'clientes/editar/:id', component: ClientesFormComponent },
  { path: 'clientes-contratos', component: ClientesContratosIndexComponent },
  { path: 'clientes-contratos/crear', component: ClientesContratosFormComponent },
  { path: 'clientes-contratos/editar/:id', component: ClientesContratosFormComponent },


];
