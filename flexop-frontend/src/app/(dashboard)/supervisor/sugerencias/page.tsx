'use client';

import {
  useSugerencias,
  useAceptarSugerencia,
  useRechazarSugerencia,
} from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Shuffle, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

export default function SupervisorSugerenciasPage() {
  const { data, isLoading } = useSugerencias();
  const aceptar = useAceptarSugerencia();
  const rechazar = useRechazarSugerencia();

  if (isLoading) return <PageLoader />;

  const sugerencias = data?.results ?? [];
  const pendientes = sugerencias.filter((s) => s.estado === 'PENDIENTE');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Shuffle className="h-6 w-6" /> Sugerencias de Reasignación
          {pendientes.length > 0 && (
            <Badge variant="secondary">{pendientes.length} pendientes</Badge>
          )}
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} sugerencias totales
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {sugerencias.length === 0 ? (
            <EmptyState
              title="Sin sugerencias"
              description="El sistema no tiene sugerencias de reasignación pendientes"
              icon={Shuffle}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Razón</TableHead>
                  <TableHead>Operario origen</TableHead>
                  <TableHead>Máquina destino</TableHead>
                  <TableHead>Impacto estimado</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead className="text-right">Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sugerencias.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="max-w-[250px]">
                      <p className="text-sm">{s.razon}</p>
                    </TableCell>
                    <TableCell className="text-sm">#{s.operario_origen}</TableCell>
                    <TableCell className="text-sm">#{s.maquina_destino}</TableCell>
                    <TableCell>
                      <span className="flex items-center gap-1 text-sm font-medium text-green-600">
                        <TrendingUp className="h-3 w-3" />
                        +{s.impacto_estimado?.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell><StatusBadge value={s.estado} /></TableCell>
                    <TableCell className="text-right">
                      {s.estado === 'PENDIENTE' && (
                        <div className="flex gap-2 justify-end">
                          <Button
                            size="sm"
                            onClick={() => aceptar.mutate(s.id, {
                              onSuccess: () => toast.success('Reasignación aplicada'),
                              onError: () => toast.error('Error'),
                            })}
                            disabled={aceptar.isPending}
                          >
                            Aceptar
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => rechazar.mutate(s.id, {
                              onSuccess: () => toast.info('Sugerencia rechazada'),
                              onError: () => toast.error('Error'),
                            })}
                            disabled={rechazar.isPending}
                          >
                            Rechazar
                          </Button>
                        </div>
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
