'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { metricasApi } from '@/lib/api';
import { useDashboardOperario } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { Plus, PackagePlus } from 'lucide-react';
import { toast } from 'sonner';

const schema = z.object({
  cantidad: z.string().transform((v) => parseInt(v, 10)).pipe(z.number().min(1, 'Debe ser al menos 1')),
  observaciones: z.string().optional(),
});
type FormInput = { cantidad: string; observaciones?: string };
type FormData = z.infer<typeof schema>;

export default function OperarioProduccionPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { data: dashboard } = useDashboardOperario();

  const { data, isLoading } = useQuery({
    queryKey: ['produccion'],
    queryFn: () => metricasApi.produccionList().then((r) => r.data),
  });

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormInput>({
    resolver: zodResolver(schema) as never,
  });

  const registrar = useMutation({
    mutationFn: (values: { cantidad: number; observaciones?: string }) =>
      metricasApi.produccionCreate({
        asignacion: dashboard?.asignacion_activa?.id,
        cantidad: values.cantidad,
        observaciones: values.observaciones ?? '',
      }),
    onSuccess: () => {
      toast.success('Producción registrada');
      qc.invalidateQueries({ queryKey: ['produccion'] });
      qc.invalidateQueries({ queryKey: ['dashboard', 'operario'] });
      reset();
      setOpen(false);
    },
    onError: () => toast.error('Error al registrar producción'),
  });

  if (isLoading) return <PageLoader />;

  const registros = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <PackagePlus className="h-6 w-6" /> Registro de Producción
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" disabled={!dashboard?.asignacion_activa}>
              <Plus className="h-4 w-4 mr-2" /> Registrar
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Registrar producción</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit((d) => registrar.mutate(d as unknown as { cantidad: number; observaciones?: string }))} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cantidad">Cantidad producida</Label>
                <Input id="cantidad" type="number" min={1} {...register('cantidad')} />
                {errors.cantidad && (
                  <p className="text-sm text-destructive">{errors.cantidad.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="obs">Observaciones</Label>
                <Input id="obs" placeholder="Opcional..." {...register('observaciones')} />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>
                  Cancelar
                </Button>
                <Button type="submit" disabled={registrar.isPending}>
                  {registrar.isPending ? 'Guardando...' : 'Guardar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {!dashboard?.asignacion_activa && (
        <div className="text-sm text-amber-600 bg-amber-50 border border-amber-200 rounded-md px-4 py-2">
          Necesitas una asignación activa para registrar producción.
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} registros
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {registros.length === 0 ? (
            <EmptyState
              title="Sin registros"
              description="Registra tu primera producción del día"
              icon={PackagePlus}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Fecha</TableHead>
                  <TableHead>Cantidad</TableHead>
                  <TableHead>Observaciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {registros.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(r.created_at).toLocaleString('es')}
                    </TableCell>
                    <TableCell className="font-bold">{r.cantidad}</TableCell>
                    <TableCell className="text-sm">{r.observaciones || '—'}</TableCell>
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
