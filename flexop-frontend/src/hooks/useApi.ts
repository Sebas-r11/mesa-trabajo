import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertasApi, reasignacionesApi, reportesApi, metricasApi, ordenesApi } from '@/lib/api';
import { operacionesApi } from '@/lib/api/operaciones';
import { maquinasApi } from '@/lib/api/maquinas';
import { usuariosApi } from '@/lib/api/usuarios';

// ─── Usuarios ─────────────────────────────────────────────────────
export function useUsuarios(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['usuarios', params],
    queryFn: () => usuariosApi.list(params).then((r) => r.data),
  });
}

// ─── Máquinas ─────────────────────────────────────────────────────
export function useMaquinas(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['maquinas', params],
    queryFn: () => maquinasApi.list(params).then((r) => r.data),
  });
}

export function useTiposMaquina() {
  return useQuery({
    queryKey: ['tipos-maquina'],
    queryFn: () => maquinasApi.tiposList().then((r) => r.data),
  });
}

// ─── Operaciones ──────────────────────────────────────────────────
export function useTurnos() {
  return useQuery({
    queryKey: ['turnos'],
    queryFn: () => operacionesApi.turnosList().then((r) => r.data),
  });
}

export function useOperarios(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['operarios', params],
    queryFn: () => operacionesApi.operariosList(params).then((r) => r.data),
  });
}

export function useAsignaciones(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['asignaciones', params],
    queryFn: () => operacionesApi.asignacionesList(params).then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useIncidencias(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['incidencias', params],
    queryFn: () => operacionesApi.incidenciasList(params).then((r) => r.data),
  });
}

// ─── Métricas ─────────────────────────────────────────────────────
export function useProduccion(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['produccion', params],
    queryFn: () => metricasApi.produccionList(params).then((r) => r.data),
  });
}

export function useMetricas(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['metricas', params],
    queryFn: () => metricasApi.metricasList(params).then((r) => r.data),
  });
}

// ─── Alertas ──────────────────────────────────────────────────────
export function useAlertas(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['alertas', params],
    queryFn: () => alertasApi.alertasList(params).then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useNotificaciones() {
  return useQuery({
    queryKey: ['notificaciones'],
    queryFn: () => alertasApi.notificacionesList().then((r) => r.data),
    refetchInterval: 30_000,
  });
}

// ─── Sugerencias ──────────────────────────────────────────────────
export function useSugerencias(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['sugerencias', params],
    queryFn: () => reasignacionesApi.sugerenciasList(params).then((r) => r.data),
    refetchInterval: 30_000,
  });
}

// ─── Órdenes ──────────────────────────────────────────────────────
export function useOrdenes(params?: Record<string, unknown>) {
  return useQuery({
    queryKey: ['ordenes', params],
    queryFn: () => ordenesApi.list(params).then((r) => r.data),
  });
}

export function useColaDespacho() {
  return useQuery({
    queryKey: ['cola-despacho'],
    queryFn: () => ordenesApi.colaDespacho().then((r) => r.data),
    refetchInterval: 60_000,
  });
}

// ─── Dashboards ───────────────────────────────────────────────────
export function useDashboardOperario() {
  return useQuery({
    queryKey: ['dashboard', 'operario'],
    queryFn: () => reportesApi.dashboardOperario().then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useDashboardSupervisor() {
  return useQuery({
    queryKey: ['dashboard', 'supervisor'],
    queryFn: () => reportesApi.dashboardSupervisor().then((r) => r.data),
    refetchInterval: 30_000,
  });
}

export function useDashboardGerente() {
  return useQuery({
    queryKey: ['dashboard', 'gerente'],
    queryFn: () => reportesApi.dashboardGerente().then((r) => r.data),
    refetchInterval: 60_000,
  });
}

// ─── Mutations reutilizables ───────────────────────────────────────
export function useResolverAlerta() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => alertasApi.alertaResolver(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['alertas'] });
      qc.invalidateQueries({ queryKey: ['dashboard'] });
    },
  });
}

export function useAceptarSugerencia() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => reasignacionesApi.sugerenciaAceptar(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sugerencias'] }),
  });
}

export function useRechazarSugerencia() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => reasignacionesApi.sugerenciaRechazar(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sugerencias'] }),
  });
}
