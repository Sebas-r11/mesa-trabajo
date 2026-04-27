'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { usuariosApi } from '@/lib/api/usuarios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Users, UserPlus } from 'lucide-react';
import { toast } from 'sonner';

const rolVariant = (rol: string) => {
  if (rol === 'ADMIN') return 'destructive';
  if (rol === 'GERENTE') return 'default';
  if (rol === 'SUPERVISOR') return 'secondary';
  return 'outline';
};

export default function AdminUsuariosPage() {
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['usuarios'],
    queryFn: () => usuariosApi.list().then((r) => r.data),
  });

  const toggleActivo = useMutation({
    mutationFn: ({ id, activo }: { id: number; activo: boolean }) =>
      usuariosApi.update(id, { activo: !activo }),
    onSuccess: () => {
      toast.success('Usuario actualizado');
      qc.invalidateQueries({ queryKey: ['usuarios'] });
    },
    onError: () => toast.error('Error al actualizar usuario'),
  });

  if (isLoading) {
    return <div className="animate-pulse h-64 bg-slate-200 rounded-lg" />;
  }

  const usuarios = data?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Users className="h-6 w-6" /> Usuarios
        </h1>
        <Button size="sm">
          <UserPlus className="h-4 w-4 mr-2" /> Nuevo usuario
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} usuarios registrados
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Usuario</TableHead>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Rol</TableHead>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Acciones</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {usuarios.map((u) => (
                <TableRow key={u.id}>
                  <TableCell className="font-mono text-sm">{u.username}</TableCell>
                  <TableCell>{u.first_name} {u.last_name}</TableCell>
                  <TableCell className="text-muted-foreground">{u.email}</TableCell>
                  <TableCell>
                    <Badge variant={rolVariant(u.rol)}>{u.rol}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={u.activo ? 'default' : 'secondary'}>
                      {u.activo ? 'Activo' : 'Inactivo'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toggleActivo.mutate({ id: u.id, activo: u.activo })}
                      disabled={toggleActivo.isPending}
                    >
                      {u.activo ? 'Desactivar' : 'Activar'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
