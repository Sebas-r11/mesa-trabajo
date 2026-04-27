'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useOperarios, useTurnos } from '@/hooks/useApi';
import { operacionesApi } from '@/lib/api/operaciones';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Users } from 'lucide-react';
import { toast } from 'sonner';

export default function AdminOperariosPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useOperarios();
  const { data: turnos } = useTurnos();

  const toggleActivo = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) =>
      operacionesApi.operarioUpdate(id, { activo: !activo }),
    onSuccess: () => { toast.success('Operario actualizado'); qc.invalidateQueries({ queryKey: ['operarios'] }); },
    onError: () => toast.error('Error al actualizar'),
  });

  if (isLoading) return <PageLoader />;

  const operarios = data?.results ?? [];
  const turnoMap = Object.fromEntries((turnos?.results ?? []).map((t) => [t.id, t.nombre]));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" /> Operarios
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} operarios registrados
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {operarios.length === 0 ? (
            <EmptyState title="Sin operarios" description="No hay operarios configurados en el sistema" icon={Users} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuario</TableHead>
                  <TableHead>Turno</TableHead>
                  <TableHead>Habilidades</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {operarios.map((op) => (
                  <TableRow key={op.id}>
                    <TableCell className="font-medium">#{op.usuario}</TableCell>
                    <TableCell className="text-sm">
                      {op.turno ? turnoMap[op.turno] ?? `#${op.turno}` : '—'}
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        {(op.habilidades ?? []).slice(0, 3).map((h) => (
                          <Badge key={h} variant="secondary" className="text-xs">#{h}</Badge>
                        ))}
                        {(op.habilidades?.length ?? 0) > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{(op.habilidades?.length ?? 0) - 3}
                          </Badge>
                        )}
                        {(op.habilidades?.length ?? 0) === 0 && (
                          <span className="text-xs text-muted-foreground">Sin habilidades</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge value={op.activo ? 'ACTIVO' : 'INACTIVO'} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleActivo.mutate({ id: op.id, activo: op.activo })}
                        disabled={toggleActivo.isPending}
                      >
                        {op.activo ? 'Desactivar' : 'Activar'}
                      </Button>
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
