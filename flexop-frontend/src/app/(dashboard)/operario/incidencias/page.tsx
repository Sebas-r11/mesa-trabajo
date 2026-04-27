'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useQueryClient, useMutation } from '@tanstack/react-query';
import { operacionesApi } from '@/lib/api/operaciones';
import { useIncidencias, useDashboardOperario } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger,
} from '@/components/ui/dialog';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { StatusBadge } from '@/components/shared/StatusBadge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { AlertCircle, Plus } from 'lucide-react';
import { toast } from 'sonner';

const schema = z.object({
  tipo: z.string().min(1, 'Selecciona un tipo'),
  descripcion: z.string().min(5, 'Describe la incidencia (mín. 5 caracteres)'),
  prioridad: z.enum(['BAJA', 'MEDIA', 'ALTA', 'CRITICA']),
});
type FormData = z.infer<typeof schema>;

const TIPOS = ['FALLA_MECANICA', 'FALTA_MATERIAL', 'ERROR_OPERARIO', 'PARADA_NO_PLANIFICADA', 'OTRO'];

export default function OperarioIncidenciasPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { data: dashboard } = useDashboardOperario();
  const { data, isLoading } = useIncidencias();

  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { prioridad: 'MEDIA' },
  });

  const reportar = useMutation({
    mutationFn: (values: FormData) =>
      operacionesApi.incidenciaCreate({
        asignacion: dashboard?.asignacion_activa?.id,
        ...values,
      }),
    onSuccess: () => {
      toast.success('Incidencia reportada');
      qc.invalidateQueries({ queryKey: ['incidencias'] });
      qc.invalidateQueries({ queryKey: ['dashboard', 'operario'] });
      reset();
      setOpen(false);
    },
    onError: () => toast.error('Error al reportar incidencia'),
  });

  if (isLoading) return <PageLoader />;

  const incidencias = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <AlertCircle className="h-6 w-6" /> Incidencias
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm" variant="destructive" disabled={!dashboard?.asignacion_activa}>
              <Plus className="h-4 w-4 mr-2" /> Reportar incidencia
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Reportar incidencia</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit((d) => reportar.mutate(d))} className="space-y-4">
              <div className="space-y-2">
                <Label>Tipo</Label>
                <Select onValueChange={(v) => setValue('tipo', v)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar tipo..." />
                  </SelectTrigger>
                  <SelectContent>
                    {TIPOS.map((t) => (
                      <SelectItem key={t} value={t}>{t.replace(/_/g, ' ')}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.tipo && <p className="text-sm text-destructive">{errors.tipo.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Prioridad</Label>
                <Select defaultValue="MEDIA" onValueChange={(v) => setValue('prioridad', v as FormData['prioridad'])}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {(['BAJA', 'MEDIA', 'ALTA', 'CRITICA'] as const).map((p) => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="desc">Descripción</Label>
                <Input id="desc" {...register('descripcion')} placeholder="Describe el problema..." />
                {errors.descripcion && (
                  <p className="text-sm text-destructive">{errors.descripcion.message}</p>
                )}
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" variant="destructive" disabled={reportar.isPending}>
                  {reportar.isPending ? 'Enviando...' : 'Reportar'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">{data?.count ?? 0} incidencias</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {incidencias.length === 0 ? (
            <EmptyState title="Sin incidencias" description="No hay incidencias registradas" icon={AlertCircle} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Descripción</TableHead>
                  <TableHead>Prioridad</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {incidencias.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="font-medium text-sm">{inc.tipo.replace(/_/g, ' ')}</TableCell>
                    <TableCell className="text-sm max-w-[200px] truncate">{inc.descripcion}</TableCell>
                    <TableCell><StatusBadge value={inc.prioridad} /></TableCell>
                    <TableCell><StatusBadge value={inc.estado} /></TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {new Date(inc.created_at).toLocaleString('es')}
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
