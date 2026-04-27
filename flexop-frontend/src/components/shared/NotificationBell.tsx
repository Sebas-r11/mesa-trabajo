'use client';

import { useQuery } from '@tanstack/react-query';
import { alertasApi } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Bell } from 'lucide-react';

export function NotificationBell() {
  const { data } = useQuery({
    queryKey: ['notificaciones'],
    queryFn: () => alertasApi.notificacionesList().then((r) => r.data),
    refetchInterval: 30_000,
  });

  const unread = data?.results.filter((n) => !n.leida) ?? [];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-5 w-5" />
          {unread.length > 0 && (
            <Badge
              variant="destructive"
              className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
            >
              {unread.length > 9 ? '9+' : unread.length}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel>Notificaciones</DropdownMenuLabel>
        <DropdownMenuSeparator />
        {unread.length === 0 ? (
          <DropdownMenuItem className="text-muted-foreground text-sm">
            Sin notificaciones nuevas
          </DropdownMenuItem>
        ) : (
          unread.slice(0, 5).map((n) => (
            <DropdownMenuItem key={n.id} className="flex flex-col items-start gap-1">
              <span className="text-sm font-medium">{n.titulo}</span>
              <span className="text-xs text-muted-foreground line-clamp-2">{n.mensaje}</span>
            </DropdownMenuItem>
          ))
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
