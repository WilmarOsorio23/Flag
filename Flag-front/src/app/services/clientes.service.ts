import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Cliente } from '../models/cliente';

@Injectable({ providedIn: 'root' })
export class ClientesService {
  private endpoint = '/api/clientes';

  constructor(private api: ApiService) {}

  getAll(): Observable<Cliente[]> {
    return this.api.getAll<Cliente>(this.endpoint);
  }

  get(id: string): Observable<Cliente> {
    return this.api.get<Cliente>(this.endpoint, id);
  }

  create(data: Cliente): Observable<Cliente> {
    return this.api.create<Cliente>(this.endpoint, data);
  }

  update(id: string, data: Cliente): Observable<Cliente> {
    return this.api.update<Cliente>(this.endpoint, id, data);
  }

  delete(id: string): Observable<void> {
    return this.api.delete(this.endpoint, id);
  }
}
