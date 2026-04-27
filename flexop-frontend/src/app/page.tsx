'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/authStore';

export default function HomePage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }
    if (user) {
      const routes: Record<string, string> = {
        OPERARIO: '/operario',
        SUPERVISOR: '/supervisor',
        GERENTE: '/gerente',
        ADMIN: '/admin/usuarios',
      };
      router.replace(routes[user.rol] ?? '/login');
    }
  }, [isAuthenticated, user, router]);

  return null;
}
