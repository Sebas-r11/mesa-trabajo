'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useIncidencias, useMaquinas, useOperarios } from '@/hooks/useApi';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { AlertCircle, CheckCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

export default function SupervisorIncidenciasPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useIncidencias();
  const { data: maquinas } = useMaquinas();
  const { data: operarios } = useOperarios();

  const resolver = useMutation({
    mutationFn: (id: number) => operacionesApi.incidenciaResolver(id),
    onSuccess: () => {
      toast.success('Incidencia resuelta');
      qc.invalidateQueries({ queryKey: ['incidencias'] });
    },
    onError: () => toast.error('Error al resolver incidencia'),
  });

  if (isLoading) return <PageLoader />;

  const incidencias = data?.results ?? [];
  const abiertas = incidencias.filter((i) => i.estado === 'ABIERTA');

  const maquinaMap = Object.fromEntries((maquinas?.results ?? []).map((m) => [m.id, m.nombre]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertCircle className="h-6 w-6" /> Incidencias
          {abiertas.length > 0 && (
            <Badge variant="destructive" className="ml-1">{abiertas.length}</Badge>
          )}
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} incidencias totales · {abiertas.length} abiertas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {incidencias.length === 0 ? (
            <EmptyState
              title="Sin incidencias"
              description="No hay incidencias registradas en el sistema"
              icon={AlertCircle}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Reportada</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidencias.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="text-sm font-medium">
                      {inc.tipo.replace(/_/g, ' ')}
                    </TableCell>
                    <TableCell className="max-w-[250px]">
                      <p className="text-sm text-muted-foreground truncate">{inc.descripcion}</p>
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={inc.prioridad} />
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={inc.estado} />
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(inc.created_at).toLocaleString('es')}
                    </TableCell>
                    <TableCell className="text-right">
                      {inc.estado === 'ABIERTA' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => resolver.mutate(inc.id)}
                          disabled={resolver.isPending}
                        >
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Resolver
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
