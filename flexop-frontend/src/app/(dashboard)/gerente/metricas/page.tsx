'use client';

import { useMetricas, useMaquinas, useOperarios } from '@/hooks/useApi';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { BarChart3 } from 'lucide-react';

function eficienciaColor(v: number) {
  if (v >= 90) return 'text-green-600';
  if (v >= 70) return 'text-yellow-600';
  return 'text-red-600';
}

export default function GerenteMetricasPage() {
  const { data, isLoading } = useMetricas();
  const { data: maquinas } = useMaquinas();

  if (isLoading) return <PageLoader />;

  const metricas = data?.results ?? [];
  const maquinaMap = Object.fromEntries((maquinas?.results ?? []).map((m) => [m.id, m.nombre]));

  const chartData = metricas.map((m) => ({
    nombre: maquinaMap[m.maquina] ?? `M${m.maquina}`,
    eficiencia: parseFloat(m.eficiencia.toFixed(1)),
  }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <BarChart3 className="h-6 w-6" /> Métricas de Eficiencia
      </h1>

      {chartData.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Eficiencia por máquina</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200" />
                <XAxis dataKey="nombre" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} unit="%" />
                <Tooltip formatter={(v) => [`${v}%`, 'Eficiencia']} />
                <ReferenceLine y={80} stroke="#f59e0b" strokeDasharray="4 4" label={{ value: 'Obj 80%', fontSize: 10 }} />
                <Bar dataKey="eficiencia" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">
            {data?.count ?? 0} registros de métricas
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {metricas.length === 0 ? (
            <EmptyState title="Sin métricas" description="Aún no hay datos de eficiencia calculados" icon={BarChart3} className="py-16" />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Máquina</TableHead>
                  <TableHead>Eficiencia</TableHead>
                  <TableHead>Real</TableHead>
                  <TableHead>Objetivo</TableHead>
                  <TableHead>Fecha</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metricas.map((m) => (
                  <TableRow key={m.id}>
                    <TableCell className="font-medium">{maquinaMap[m.maquina] ?? `#${m.maquina}`}</TableCell>
                    <TableCell>
                      <span className={`font-bold ${eficienciaColor(m.eficiencia)}`}>
                        {m.eficiencia.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>{m.produccion_real}</TableCell>
                    <TableCell>{m.produccion_objetivo}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{m.fecha}</TableCell>
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
