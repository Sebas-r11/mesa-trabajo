import { Badge } from '@/components/ui/badge';

type Variant = 'default' | 'secondary' | 'destructive' | 'outline';

function getVariant(value: string): Variant {
  const map: Record<string, Variant> = {
    // Estados generales
    ACTIVA: 'default',
    ACTIVO: 'default',
    OPERANDO: 'default',
    PENDIENTE: 'secondary',
    FINALIZADA: 'outline',
    FINALIZADO: 'outline',
    CANCELADA: 'outline',
    CANCELADO: 'outline',
    INACTIVA: 'outline',
    INACTIVO: 'outline',
    PARADA: 'destructive',
    MANTENIMIENTO: 'secondary',
    // Prioridades
    BAJA: 'outline',
    MEDIA: 'secondary',
    ALTA: 'destructive',
    CRITICA: 'destructive',
    // Alertas / incidencias
    ABIERTA: 'destructive',
    EN_PROCESO: 'secondary',
    RESUELTA: 'default',
    IGNORADA: 'outline',
    // Roles
    ADMIN: 'destructive',
    GERENTE: 'default',
    SUPERVISOR: 'secondary',
    OPERARIO: 'outline',
    // Sugerencias
    ACEPTADA: 'default',
    RECHAZADA: 'outline',
    // Órdenes
    EN_PROCESO_ORD: 'secondary',
    LISTA: 'default',
    DESPACHADA: 'outline',
  };
  return map[value] ?? 'secondary';
}

interface Props {
  value: string;
  label?: string;
}

export function StatusBadge({ value, label }: Props) {
  return <Badge variant={getVariant(value)}>{label ?? value}</Badge>;
}
