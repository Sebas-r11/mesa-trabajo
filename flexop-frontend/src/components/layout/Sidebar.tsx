'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Cpu,
  Users,
  Activity,
  BarChart3,
  Bell,
  Shuffle,
  FileText,
  ClipboardList,
  Building2,
  PackagePlus,
  AlertCircle,
} from 'lucide-react';

const navByRole: Record<string, { href: string; label: string; icon: React.ElementType }[]> = {
  OPERARIO: [
    { href: '/operario', label: 'Mi Dashboard', icon: LayoutDashboard },
    { href: '/operario/produccion', label: 'Producción', icon: PackagePlus },
    { href: '/operario/incidencias', label: 'Incidencias', icon: AlertCircle },
  ],
  SUPERVISOR: [
    { href: '/supervisor', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/supervisor/alertas', label: 'Alertas', icon: Bell },
    { href: '/supervisor/sugerencias', label: 'Reasignaciones', icon: Shuffle },
    { href: '/supervisor/asignaciones', label: 'Asignaciones', icon: Activity },
    { href: '/supervisor/incidencias', label: 'Incidencias', icon: AlertCircle },
  ],
  GERENTE: [
    { href: '/gerente', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/gerente/reportes', label: 'Reportes', icon: FileText },
    { href: '/gerente/metricas', label: 'Métricas', icon: BarChart3 },
    { href: '/gerente/ordenes', label: 'Órdenes', icon: ClipboardList },
  ],
  ADMIN: [
    { href: '/admin/usuarios', label: 'Usuarios', icon: Users },
    { href: '/admin/maquinas', label: 'Máquinas', icon: Cpu },
    { href: '/admin/operarios', label: 'Operarios', icon: Users },
  ],
};

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuthStore();
  const navItems = user ? (navByRole[user.rol] ?? []) : [];

  return (
    <aside className="w-64 flex-shrink-0 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex flex-col">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-slate-200 dark:border-slate-800">
        <span className="text-xl font-bold text-primary">FLEX-OP</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
              pathname === href
                ? 'bg-primary text-primary-foreground'
                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'
            )}
          >
            <Icon className="h-4 w-4 flex-shrink-0" />
            {label}
          </Link>
        ))}
      </nav>

      {/* Rol badge */}
      {user && (
        <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800">
          <p className="text-xs text-slate-500 truncate">{user.first_name} {user.last_name}</p>
          <p className="text-xs font-medium text-slate-700 dark:text-slate-300">{user.rol}</p>
        </div>
      )}
    </aside>
  );
}
