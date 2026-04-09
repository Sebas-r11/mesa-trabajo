"""
Modelos del modulo de Reportes para FLEX-OP

Este modulo no tiene modelos propios, utiliza los datos de otros modulos
para generar reportes y dashboards. Aqui definimos solo el modelo de
historial de reportes generados.
"""
from django.db import models
from django.utils import timezone


class ReporteGenerado(models.Model):
    # Registro de reportes generados por el sistema
    """
    Historial de reportes generados
    
    Guarda un registro de todos los reportes generados:
    - Permite descargar reportes anteriores
    - Mantiene historial para auditoria
    - Evita regenerar reportes frecuentemente consultados
    
    Tipos de reportes:
    - EFICIENCIA_DIARIA: Eficiencia de todos los operarios en un dia
    - EFICIENCIA_SEMANAL: Resumen de eficiencia de la semana
    - PRODUCCION_DIARIA: Produccion de todas las maquinas en un dia
    - INCIDENCIAS: Resumen de incidencias en un periodo
    - OPERARIOS: Ranking y estadisticas de operarios
    - MAQUINAS: Estado y rendimiento de maquinas
    """
    
    class TipoReporteChoices(models.TextChoices):
        """Tipos de reportes disponibles"""
        EFICIENCIA_DIARIA = 'EFICIENCIA_DIARIA', 'Eficiencia Diaria'
        EFICIENCIA_SEMANAL = 'EFICIENCIA_SEMANAL', 'Eficiencia Semanal'
        PRODUCCION_DIARIA = 'PRODUCCION_DIARIA', 'Produccion Diaria'
        INCIDENCIAS = 'INCIDENCIAS', 'Reporte de Incidencias'
        OPERARIOS = 'OPERARIOS', 'Reporte de Operarios'
        MAQUINAS = 'MAQUINAS', 'Reporte de Maquinas'
        KPI_GERENCIAL = 'KPI_GERENCIAL', 'KPIs Gerenciales'
    
    class FormatoChoices(models.TextChoices):
        """Formatos de exportacion"""
        PDF = 'PDF', 'PDF'
        EXCEL = 'EXCEL', 'Excel'
        CSV = 'CSV', 'CSV'
    
    # Tipo de reporte
    tipo = models.CharField(
        max_length=30,
        choices=TipoReporteChoices.choices
    )
    
    # Formato del archivo
    formato = models.CharField(
        max_length=10,
        choices=FormatoChoices.choices,
        default=FormatoChoices.PDF
    )
    
    # Periodo del reporte
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    
    # Archivo generado
    archivo = models.FileField(
        upload_to='reportes/',
        null=True,
        blank=True
    )
    
    # Empresa
    empresa = models.ForeignKey(
        'usuarios.Empresa',
        on_delete=models.CASCADE,
        related_name='reportes_generados'
    )
    
    # Usuario que genero el reporte
    generado_por = models.ForeignKey(
        'usuarios.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reportes_generados'
    )
    
    # Auditoria
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    
    # Parametros usados para generar el reporte (en JSON)
    parametros = models.JSONField(
        null=True,
        blank=True,
        help_text='Parametros usados para generar el reporte'
    )
    
    class Meta:
        """Configuracion del modelo en la base de datos"""
        db_table = 'reportes_generados'
        verbose_name = 'Reporte Generado'
        verbose_name_plural = 'Reportes Generados'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        """Representacion en texto: tipo (fecha_inicio a fecha_fin)"""
        return f"{self.get_tipo_display()} ({self.fecha_inicio} a {self.fecha_fin})"

