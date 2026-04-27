'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAsignaciones, useMaquinas, useOperarios } from '@/hooks/useApi';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Activity, Play, Square } from 'lucide-react';
import { toast } from 'sonner';

export default function SupervisorAsignacionesPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useAsignaciones();
  const { data: maquinas } = useMaquinas();
  const { data: operarios } = useOperarios();

  const iniciar = useMutation({
    mutationFn: (id: number) => operacionesApi.asignacionIniciar(id),
    onSuccess: () => { toast.success('Asignación iniciada'); qc.invalidateQueries({ queryKey: ['asignaciones'] }); },
    onError: () => toast.error('Error al iniciar'),
  });

  const finalizar = useMutation({
    mutationFn: (id: number) => operacionesApi.asignacionFinalizar(id),
    onSuccess: () => { toast.success('Asignación finalizada'); qc.invalidateQueries({ queryKey: ['asignaciones'] }); },
    onError: () => toast.error('Error al finalizar'),
  });

  const maquinaMap = Object.fromEntries((maquinas?.results ?? []).map((m) => [m.id, m.nombre]));

  if (isLoading) return <PageLoader />;
  const asignaciones = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Activity className="h-6 w-6" /> Asignaciones
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} asignaciones · {asignaciones.filter((a) => a.estado === 'ACTIVA').length} activas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {asignaciones.length === 0 ? (
            <EmptyState title="Sin asignaciones" description="No hay asignaciones registradas" icon={Activity} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Operario</TableHead>
                  <TableHead>Máquina</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Inicio</TableHead>
                  <TableHead>Fin</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {asignaciones.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="text-sm">#{a.operario}</TableCell>
                    <TableCell className="text-sm font-medium">
                      {maquinaMap[a.maquina] ?? `#${a.maquina}`}
                    </TableCell>
                    <TableCell><StatusBadge value={a.estado} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {a.fecha_inicio ? new Date(a.fecha_inicio).toLocaleString('es') : '—'}
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {a.fecha_fin ? new Date(a.fecha_fin).toLocaleString('es') : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      {a.estado === 'PENDIENTE' && (
                        <Button size="sm" onClick={() => iniciar.mutate(a.id)} disabled={iniciar.isPending}>
                          <Play className="h-3 w-3 mr-1" /> Iniciar
                        </Button>
                      )}
                      {a.estado === 'ACTIVA' && (
                        <Button size="sm" variant="outline" onClick={() => finalizar.mutate(a.id)} disabled={finalizar.isPending}>
                          <Square className="h-3 w-3 mr-1" /> Finalizar
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
