'use client';

import { reportesApi } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table';
import { PageLoader } from '@/components/shared/LoadingSpinner';
import { EmptyState } from '@/components/shared/EmptyState';
import { FileText, Download } from 'lucide-react';
import { toast } from 'sonner';

export default function GerenteReportesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['reportes-generados'],
    queryFn: () => reportesApi.reportesGenerados().then((r) => r.data),
  });

  const handleExportCSV = async () => {
    try {
      const response = await reportesApi.exportarCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `flexop_reporte_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success('Reporte CSV descargado');
    } catch {
      toast.error('Error al exportar reporte');
    }
  };

  if (isLoading) return <PageLoader />;

  const reportes = Array.isArray(data?.results) ? data.results : [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <FileText className="h-6 w-6" /> Reportes
        </h1>
        <Button size="sm" onClick={handleExportCSV}>
          <Download className="h-4 w-4 mr-2" /> Exportar CSV
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm text-muted-foreground">Historial de reportes generados</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {reportes.length === 0 ? (
            <EmptyState
              title="Sin reportes"
              description="No hay reportes generados todavía. Usa el botón de exportar para crear uno."
              icon={FileText}
              className="py-16"
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nombre</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Generado</TableHead>
                  <TableHead className="text-right">Descargar</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {reportes.map((r: { id: number; nombre?: string; tipo?: string; created_at?: string; archivo?: string }) => (
                  <TableRow key={r.id}>
                    <TableCell className="font-medium">{r.nombre ?? `Reporte #${r.id}`}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">{r.tipo ?? '—'}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      {r.created_at ? new Date(r.created_at).toLocaleString('es') : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      {r.archivo && (
                        <Button size="sm" variant="ghost" asChild>
                          <a href={r.archivo} download>
                            <Download className="h-4 w-4" />
                          </a>
                        </Button>
                      )}
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
