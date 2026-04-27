'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useOrdenes, useColaDespacho } from '@/hooks/useApi';
import { ordenesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { ClipboardList, Truck, Play, CheckSquare } from 'lucide-react';
import { toast } from 'sonner';

export default function GerenteOrdenesPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useOrdenes();
  const { data: cola } = useColaDespacho();

  const iniciarOrden = useMutation({
    mutationFn: (id: number) => ordenesApi.iniciar(id),
    onSuccess: () => { toast.success('Orden iniciada'); qc.invalidateQueries({ queryKey: ['ordenes'] }); },
    onError: () => toast.error('Error al iniciar orden'),
  });

  const completarOrden = useMutation({
    mutationFn: (id: number) => ordenesApi.completar(id),
    onSuccess: () => { toast.success('Orden completada'); qc.invalidateQueries({ queryKey: ['ordenes', 'cola-despacho'] }); },
    onError: () => toast.error('Error al completar orden'),
  });

  const despachar = useMutation({
    mutationFn: () => ordenesApi.despachar(),
    onSuccess: () => { toast.success('Orden despachada'); qc.invalidateQueries({ queryKey: ['cola-despacho'] }); },
    onError: () => toast.error('Error al despachar'),
  });

  if (isLoading) return <PageLoader />;

  const ordenes = data?.results ?? [];
  const proxima = cola?.[0];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <ClipboardList className="h-6 w-6" /> Órdenes de Producción
      </h1>

      {/* Cola de despacho */}
      <Card className={proxima ? 'border-primary/30 bg-primary/5' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Truck className="h-5 w-5" /> Cola de despacho
          </CardTitle>
        </CardHeader>
        <CardContent>
          {proxima ? (
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Orden #{proxima.orden} — posición {proxima.posicion}</p>
                <p className="text-sm text-muted-foreground">
                  En cola desde {new Date(proxima.created_at).toLocaleString('es')}
                </p>
              </div>
              <Button onClick={() => despachar.mutate()} disabled={despachar.isPending}>
                <Truck className="h-4 w-4 mr-2" />
                {despachar.isPending ? 'Despachando...' : 'Despachar'}
              </Button>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Cola de despacho vacía</p>
          )}
        </CardContent>
      </Card>

      {/* Listado */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} órdenes
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {ordenes.length === 0 ? (
            <EmptyState title="Sin órdenes" description="No hay órdenes de producción" icon={ClipboardList} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>#</TableHead>
                  <TableHead>Producto</TableHead>
                  <TableHead>Progreso</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Fecha límite</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ordenes.map((ord) => {
                  const pct = ord.cantidad_objetivo > 0
                    ? Math.min(100, (ord.cantidad_producida / ord.cantidad_objetivo) * 100)
                    : 0;
                  return (
                    <TableRow key={ord.id}>
                      <TableCell className="font-mono text-sm">#{ord.id}</TableCell>
                      <TableCell className="font-medium">#{ord.producto}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 min-w-[120px]">
                          <div className="flex-1 bg-slate-200 rounded-full h-1.5">
                            <div
                              className="bg-primary h-1.5 rounded-full transition-all"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground whitespace-nowrap">
                            {ord.cantidad_producida}/{ord.cantidad_objetivo}
                          </span>
                        </div>
                      </TableCell>
                      <TableCell><StatusBadge value={ord.estado} /></TableCell>
                      <TableCell>
                        <Badge variant="outline">{ord.prioridad}</Badge>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(ord.fecha_limite).toLocaleDateString('es')}
                      </TableCell>
                      <TableCell className="text-right">
                        {ord.estado === 'PENDIENTE' && (
                          <Button size="sm" onClick={() => iniciarOrden.mutate(ord.id)} disabled={iniciarOrden.isPending}>
                            <Play className="h-3 w-3 mr-1" /> Iniciar
                          </Button>
                        )}
                        {ord.estado === 'EN_PROCESO' && (
                          <Button size="sm" variant="outline" onClick={() => completarOrden.mutate(ord.id)} disabled={completarOrden.isPending}>
                            <CheckSquare className="h-3 w-3 mr-1" /> Completar
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
