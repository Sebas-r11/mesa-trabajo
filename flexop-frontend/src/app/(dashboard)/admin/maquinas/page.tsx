'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useMaquinas, useTiposMaquina } from '@/hooks/useApi';
import { maquinasApi } from '@/lib/api/maquinas';
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
import { Cpu, Plus } from 'lucide-react';
import { toast } from 'sonner';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  nombre: z.string().min(2, 'Mínimo 2 caracteres'),
  codigo: z.string().min(1, 'Requerido'),
  tipo: z.string().transform(Number),
  eficiencia_objetivo: z.string().transform(Number),
  descripcion: z.string().optional(),
});
type FormInput = { nombre: string; codigo: string; tipo: string; eficiencia_objetivo: string; descripcion?: string };
type FormData = z.infer<typeof schema>;

export default function AdminMaquinasPage() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const { data, isLoading } = useMaquinas();
  const { data: tipos } = useTiposMaquina();

  const { register, handleSubmit, setValue, reset, formState: { errors } } = useForm<FormInput>({
    resolver: zodResolver(schema) as never,
    defaultValues: { eficiencia_objetivo: '80' },
  });

  const crear = useMutation({
    mutationFn: (values: FormData) => maquinasApi.create(values as unknown as import('@/types').Maquina),
    onSuccess: () => {
      toast.success('Máquina creada');
      qc.invalidateQueries({ queryKey: ['maquinas'] });
      reset();
      setOpen(false);
    },
    onError: () => toast.error('Error al crear máquina'),
  });

  const toggleActivo = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) =>
      maquinasApi.update(id, { activo: !activo }),
    onSuccess: () => { toast.success('Máquina actualizada'); qc.invalidateQueries({ queryKey: ['maquinas'] }); },
  });

  if (isLoading) return <PageLoader />;

  const maquinas = data?.results ?? [];
  const tiposList = tipos?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Cpu className="h-6 w-6" /> Máquinas
        </h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button size="sm"><Plus className="h-4 w-4 mr-2" /> Nueva máquina</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Nueva máquina</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit((d) => crear.mutate(d as unknown as FormData))} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Nombre</Label>
                  <Input {...register('nombre')} placeholder="Inyectora A1" />
                  {errors.nombre && <p className="text-xs text-destructive">{errors.nombre.message}</p>}
                </div>
                <div className="space-y-2">
                  <Label>Código</Label>
                  <Input {...register('codigo')} placeholder="INY-001" />
                  {errors.codigo && <p className="text-xs text-destructive">{errors.codigo.message}</p>}
                </div>
              </div>
              <div className="space-y-2">
                <Label>Tipo de máquina</Label>
                <Select onValueChange={(v) => setValue('tipo', v)}>
                  <SelectTrigger><SelectValue placeholder="Seleccionar..." /></SelectTrigger>
                  <SelectContent>
                    {tiposList.map((t) => (
                      <SelectItem key={t.id} value={String(t.id)}>{t.nombre}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.tipo && <p className="text-xs text-destructive">{errors.tipo.message}</p>}
              </div>
              <div className="space-y-2">
                <Label>Eficiencia objetivo (%)</Label>
                <Input type="number" min={1} max={100} {...register('eficiencia_objetivo')} />
              </div>
              <div className="space-y-2">
                <Label>Descripción</Label>
                <Input {...register('descripcion')} placeholder="Opcional..." />
              </div>
              <div className="flex gap-2 justify-end">
                <Button type="button" variant="outline" onClick={() => setOpen(false)}>Cancelar</Button>
                <Button type="submit" disabled={crear.isPending}>
                  {crear.isPending ? 'Creando...' : 'Crear'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">{data?.count ?? 0} máquinas</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {maquinas.length === 0 ? (
            <EmptyState title="Sin máquinas" description="Crea la primera máquina de tu planta" icon={Cpu} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Código</TableHead>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Eficiencia obj.</TableHead>
                  <TableHead>Activa</TableHead>
                  <TableHead className="text-right">Acción</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {maquinas.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-mono text-sm">{m.codigo}</TableCell>
                    <TableCell className="font-medium">{m.nombre}</TableCell>
                    <TableCell><StatusBadge value={m.estado} /></TableCell>
                    <TableCell>{m.eficiencia_objetivo}%</TableCell>
                    <TableCell>
                      <StatusBadge value={m.activo ? 'ACTIVO' : 'INACTIVO'} />
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => toggleActivo.mutate({ id: m.id, activo: m.activo })}
                        disabled={toggleActivo.isPending}
                      >
                        {m.activo ? 'Desactivar' : 'Activar'}
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
