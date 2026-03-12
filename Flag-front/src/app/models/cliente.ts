export interface Cliente {
  TipoDocumentoID: string;
  DocumentoId: string;
  Nombre_Cliente: string;
  Activo: boolean;
  Fecha_Inicio: string;
  Fecha_Retiro?: string;
  Direccion?: string;
  Telefono?: string;
  CorreoElectronico?: string;
  BuzonFacturacion?: string;
  TipoCliente?: string;
  Ciudad?: string;
  Departamento?: string;
  Pais?: string;
  Nacional?: boolean;
  ContactoID?: string;
}

export interface ClienteKey {
  TipoDocumentoID: string;
  DocumentoId: string;
}
