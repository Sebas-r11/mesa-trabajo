'use client';

import { useQuery } from '@tanstack/react-query';
import { reportesApi } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, Users, Cpu, CheckSquare } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

const COLORS = ['#3b82f6', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6'];

export default function GerenteDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard', 'gerente'],
    queryFn: () => reportesApi.dashboardGerente().then((r) => r.data),
    refetchInterval: 60_000,
  });

  if (isLoading) {
    return <div className="animate-pulse space-y-4"><div className="h-64 bg-slate-200 rounded-lg" /></div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard Gerente</h1>

      {/* KPIs globales */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-4 w-4" /> Eficiencia general
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{data?.eficiencia_general?.toFixed(1) ?? 0}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <Cpu className="h-4 w-4" /> OEE
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{data?.oee?.toFixed(1) ?? 0}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-1">
              <CheckSquare className="h-4 w-4" /> Cumplimiento
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{data?.cumplimiento?.toFixed(1) ?? 0}%</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Tendencia producción */}
        <Card>
          <CardHeader>
            <CardTitle>Producción últimos 7 días</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={data?.produccion_semana ?? []}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" />
                <XAxis dataKey="fecha" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="cantidad" stroke="#3b82f6" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Top operarios */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" /> Top operarios
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={data?.top_operarios ?? []} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                <YAxis dataKey="operario" type="category" tick={{ fontSize: 11 }} width={80} />
                <Tooltip formatter={(v) => [`${v}%`, 'Eficiencia']} />
                <Bar dataKey="eficiencia" fill="#3b82f6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Incidencias */}
        <Card>
          <CardHeader>
            <CardTitle>Incidencias por tipo</CardTitle>
          </CardHeader>
          <CardContent className="flex justify-center">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={data?.incidencias_semana ?? []}
                  dataKey="count"
                  nameKey="tipo"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                >
                  {(data?.incidencias_semana ?? []).map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Legend />
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
