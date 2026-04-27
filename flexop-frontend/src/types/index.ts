// ─── Autenticación ───────────────────────────────────────────────
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: 'OPERARIO' | 'SUPERVISOR' | 'GERENTE' | 'ADMIN';
  empresa: number | null;
  activo: boolean;
}

// ─── Paginación ───────────────────────────────────────────────────
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// ─── Empresa ─────────────────────────────────────────────────────
export interface Empresa {
  id: number;
  nombre: string;
  razon_social: string;
  ruc: string;
  direccion: string;
  telefono: string;
  email: string;
  activo: boolean;
}

// ─── Usuarios ────────────────────────────────────────────────────
export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  rol: 'OPERARIO' | 'SUPERVISOR' | 'GERENTE' | 'ADMIN';
  empresa: number | null;
  empresa_detalle?: Empresa;
  activo: boolean;
  fecha_ingreso: string;
}

// ─── Máquinas ────────────────────────────────────────────────────
export interface TipoMaquina {
  id: number;
  nombre: string;
  descripcion: string;
  empresa: number;
  activo: boolean;
  created_at: string;
}

export interface Maquina {
  id: number;
  nombre: string;
  codigo: string;
  tipo: number;
  tipo_detalle?: TipoMaquina;
  empresa: number;
  estado: 'OPERANDO' | 'PARADA' | 'MANTENIMIENTO' | 'INACTIVA';
  eficiencia_objetivo: number;
  descripcion: string;
  activo: boolean;
  created_at: string;
}

export interface Producto {
  id: number;
  nombre: string;
  codigo: string;
  descripcion: string;
  unidad_medida: string;
  empresa: number;
  activo: boolean;
}

// ─── Operaciones ─────────────────────────────────────────────────
export interface Turno {
  id: number;
  nombre: string;
  hora_inicio: string;
  hora_fin: string;
  empresa: number;
  activo: boolean;
}

export interface Habilidad {
  id: number;
  nombre: string;
  descripcion: string;
  empresa: number;
}

export interface Operario {
  id: number;
  usuario: number;
  usuario_detalle?: Usuario;
  habilidades: number[];
  habilidades_detalle?: Habilidad[];
  turno: number | null;
  turno_detalle?: Turno;
  activo: boolean;
}

export interface Asignacion {
  id: number;
  operario: number;
  operario_detalle?: Operario;
  maquina: number;
  maquina_detalle?: Maquina;
  turno: number;
  turno_detalle?: Turno;
  estado: 'PENDIENTE' | 'ACTIVA' | 'FINALIZADA' | 'CANCELADA';
  fecha_inicio: string | null;
  fecha_fin: string | null;
  created_at: string;
}

export interface Incidencia {
  id: number;
  asignacion: number;
  tipo: string;
  descripcion: string;
  estado: 'ABIERTA' | 'EN_PROCESO' | 'RESUELTA';
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  created_at: string;
  resuelta_at: string | null;
}

// ─── Métricas ────────────────────────────────────────────────────
export interface RegistroProduccion {
  id: number;
  asignacion: number;
  cantidad: number;
  observaciones: string;
  created_at: string;
}

export interface MetricaEficiencia {
  id: number;
  operario: number;
  maquina: number;
  turno: number;
  eficiencia: number;
  produccion_real: number;
  produccion_objetivo: number;
  fecha: string;
}

export interface ObjetivoProduccion {
  id: number;
  maquina: number;
  operario: number | null;
  cantidad_objetivo: number;
  unidad: string;
  periodo: string;
  activo: boolean;
}

// ─── Alertas ─────────────────────────────────────────────────────
export interface ReglaAlerta {
  id: number;
  nombre: string;
  condicion: string;
  umbral: number;
  tiempo_minutos: number;
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  activo: boolean;
}

export interface Alerta {
  id: number;
  regla: number;
  regla_detalle?: ReglaAlerta;
  mensaje: string;
  prioridad: 'BAJA' | 'MEDIA' | 'ALTA' | 'CRITICA';
  estado: 'ACTIVA' | 'RESUELTA' | 'IGNORADA';
  created_at: string;
  resuelta_at: string | null;
}

export interface Notificacion {
  id: number;
  usuario: number;
  titulo: string;
  mensaje: string;
  leida: boolean;
  created_at: string;
}

// ─── Reasignaciones ──────────────────────────────────────────────
export interface SugerenciaReasignacion {
  id: number;
  operario_origen: number;
  maquina_destino: number;
  razon: string;
  estado: 'PENDIENTE' | 'ACEPTADA' | 'RECHAZADA';
  impacto_estimado: number;
  created_at: string;
}

// ─── Órdenes ─────────────────────────────────────────────────────
export interface OrdenProduccion {
  id: number;
  producto: number;
  producto_detalle?: Producto;
  cantidad_objetivo: number;
  cantidad_producida: number;
  estado: 'PENDIENTE' | 'EN_PROCESO' | 'LISTA' | 'DESPACHADA';
  prioridad: number;
  fecha_limite: string;
  created_at: string;
}

export interface ColaDespacho {
  id: number;
  orden: number;
  orden_detalle?: OrdenProduccion;
  posicion: number;
  created_at: string;
}

// ─── Reportes / Dashboard ────────────────────────────────────────
export interface DashboardOperario {
  asignacion_activa: Asignacion | null;
  produccion_hoy: number;
  objetivo_hoy: number;
  eficiencia_hoy: number;
  incidencias_abiertas: number;
}

export interface DashboardSupervisor {
  maquinas_estado: { estado: string; count: number }[];
  alertas_activas: number;
  sugerencias_pendientes: number;
  eficiencia_turno: number;
  operarios_activos: number;
}

export interface DashboardGerente {
  eficiencia_general: number;
  oee: number;
  cumplimiento: number;
  produccion_semana: { fecha: string; cantidad: number }[];
  top_operarios: { operario: string; eficiencia: number }[];
  incidencias_semana: { tipo: string; count: number }[];
}
