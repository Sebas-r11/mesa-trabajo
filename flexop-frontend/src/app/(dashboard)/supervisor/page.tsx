'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { reportesApi } from '@/lib/api';
import { alertasApi, reasignacionesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Bell, Shuffle, Cpu, Users, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export default function SupervisorDashboard() {
  const qc = useQueryClient();

  const { data: dashboard, isLoading: loadingDash } = useQuery({
    queryKey: ['dashboard', 'supervisor'],
    queryFn: () => reportesApi.dashboardSupervisor().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const { data: alertas } = useQuery({
    queryKey: ['alertas', { estado: 'ACTIVA' }],
    queryFn: () => alertasApi.alertasList({ estado: 'ACTIVA' }).then((r) => r.data),
    refetchInterval: 30_000,
  });

  const { data: sugerencias } = useQuery({
    queryKey: ['sugerencias', { estado: 'PENDIENTE' }],
    queryFn: () => reasignacionesApi.sugerenciasList({ estado: 'PENDIENTE' }).then((r) => r.data),
  });

  const resolverAlerta = useMutation({
    mutationFn: (id: number) => alertasApi.alertaResolver(id),
    onSuccess: () => {
      toast.success('Alerta resuelta');
      qc.invalidateQueries({ queryKey: ['alertas'] });
      qc.invalidateQueries({ queryKey: ['dashboard', 'supervisor'] });
    },
  });

  const aceptarSugerencia = useMutation({
    mutationFn: (id: number) => reasignacionesApi.sugerenciaAceptar(id),
    onSuccess: () => {
      toast.success('Reasignación aplicada');
      qc.invalidateQueries({ queryKey: ['sugerencias'] });
    },
  });

  const rechazarSugerencia = useMutation({
    mutationFn: (id: number) => reasignacionesApi.sugerenciaRechazar(id),
    onSuccess: () => {
      toast.info('Sugerencia rechazada');
      qc.invalidateQueries({ queryKey: ['sugerencias'] });
    },
  });

  const prioridadVariant = (p: string) => {
    if (p === 'CRITICA') return 'destructive';
    if (p === 'ALTA') return 'destructive';
    if (p === 'MEDIA') return 'secondary';
    return 'outline';
  };

  if (loadingDash) {
    return <div className="animate-pulse space-y-4"><div className="h-32 bg-slate-200 rounded-lg" /></div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard Supervisor</h1>

      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Cpu className="h-4 w-4" /> Máquinas operando
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-green-600">
              {dashboard?.maquinas_estado.find((m) => m.estado === 'OPERANDO')?.count ?? 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Bell className="h-4 w-4" /> Alertas activas
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-destructive">
              {dashboard?.alertas_activas ?? 0}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Users className="h-4 w-4" /> Operarios activos
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{dashboard?.operarios_activos ?? 0}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-4 w-4" /> Eficiencia turno
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {dashboard?.eficiencia_turno?.toFixed(1) ?? 0}%
            </p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Alertas */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" /> Alertas activas
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(alertas?.results ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">Sin alertas activas</p>
            ) : (
              (alertas?.results ?? []).slice(0, 5).map((alerta) => (
                <div key={alerta.id} className="flex items-start justify-between gap-2 p-3 border rounded-lg">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <Badge variant={prioridadVariant(alerta.prioridad)}>
                        {alerta.prioridad}
                      </Badge>
                    </div>
                    <p className="text-sm">{alerta.mensaje}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => resolverAlerta.mutate(alerta.id)}
                    disabled={resolverAlerta.isPending}
                  >
                    Resolver
                  </Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Sugerencias */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shuffle className="h-5 w-5" /> Sugerencias de reasignación
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {(sugerencias?.results ?? []).length === 0 ? (
              <p className="text-sm text-muted-foreground">Sin sugerencias pendientes</p>
            ) : (
              (sugerencias?.results ?? []).map((s) => (
                <div key={s.id} className="p-3 border rounded-lg space-y-2">
                  <p className="text-sm">{s.razon}</p>
                  <p className="text-xs text-muted-foreground">
                    Impacto estimado: +{s.impacto_estimado?.toFixed(1)}%
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      onClick={() => aceptarSugerencia.mutate(s.id)}
                      disabled={aceptarSugerencia.isPending}
                    >
                      Aceptar
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => rechazarSugerencia.mutate(s.id)}
                      disabled={rechazarSugerencia.isPending}
                    >
                      Rechazar
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
