# Modulo de Reportes - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de reportes.
El modulo proporciona dashboards personalizados por rol y exportacion de datos.


## Dashboards

Los dashboards proporcionan informacion en tiempo real adaptada a cada rol
de usuario en el sistema.


### Dashboard de Operario

```
GET /api/dashboard/operario/
```

Retorna la informacion relevante para un operario sobre su trabajo actual.

**Requiere autenticacion**: Si, el usuario debe tener perfil de operario.

**Respuesta exitosa (200):**
```json
{
    "asignacion_activa": {
        "id": 5,
        "maquina": "Inyectora Principal",
        "maquina_codigo": "INY-001",
        "turno": "Turno Mañana",
        "hora_inicio": "06:05:30"
    },
    "eficiencia_hoy": 92.5,
    "produccion_hoy": 750,
    "objetivo_dia": 1000,
    "porcentaje_objetivo": 75.0,
    "tareas_completadas_hoy": 2,
    "eficiencia_promedio": 88.5
}
```

**Sin asignacion activa:**
```json
{
    "asignacion_activa": null,
    "eficiencia_hoy": 0,
    "produccion_hoy": 0,
    "objetivo_dia": 1000,
    "porcentaje_objetivo": 0,
    "tareas_completadas_hoy": 0,
    "eficiencia_promedio": 88.5
}
```

**Error (403):**
```json
{
    "error": "Usuario no tiene perfil de operario"
}
```


### Dashboard de Supervisor

```
GET /api/dashboard/supervisor/
```

Retorna la informacion que necesita un supervisor para gestionar su turno.

**Respuesta exitosa (200):**
```json
{
    "maquinas_estado": [
        {
            "id": 1,
            "codigo": "INY-001",
            "nombre": "Inyectora Principal",
            "estado": "OPERANDO",
            "color": "verde"
        },
        {
            "id": 2,
            "codigo": "INY-002",
            "nombre": "Inyectora Secundaria",
            "estado": "PARADA",
            "color": "rojo"
        },
        {
            "id": 3,
            "codigo": "EXT-001",
            "nombre": "Extrusora 1",
            "estado": "MANTENIMIENTO",
            "color": "amarillo"
        }
    ],
    "alertas_activas": 3,
    "alertas_criticas": 1,
    "sugerencias_pendientes": 2,
    "eficiencia_turno": 87.5,
    "ranking_operarios": [
        {
            "codigo": "OP-001",
            "nombre": "Carlos Ramirez",
            "eficiencia": 92.5
        },
        {
            "codigo": "OP-003",
            "nombre": "Maria Lopez",
            "eficiencia": 90.2
        }
    ],
    "incidencias_abiertas": 2
}
```


### Dashboard de Gerente

```
GET /api/dashboard/gerente/
```

Retorna KPIs y metricas gerenciales de toda la empresa.

**Respuesta exitosa (200):**
```json
{
    "eficiencia_general": 88.5,
    "oee_aproximado": 78.2,
    "cumplimiento_objetivos": 85.5,
    "produccion_total_dia": 5000,
    "produccion_total_semana": 32500,
    "tendencia_eficiencia": [
        {"fecha": "2026-03-03", "eficiencia": 85.0},
        {"fecha": "2026-03-04", "eficiencia": 86.5},
        {"fecha": "2026-03-05", "eficiencia": 87.0},
        {"fecha": "2026-03-06", "eficiencia": 88.0},
        {"fecha": "2026-03-07", "eficiencia": 89.5},
        {"fecha": "2026-03-08", "eficiencia": 87.5},
        {"fecha": "2026-03-09", "eficiencia": 88.5}
    ],
    "comparativa_turnos": [
        {"turno": "Turno Mañana", "eficiencia": 89.5},
        {"turno": "Turno Tarde", "eficiencia": 87.5},
        {"turno": "Turno Noche", "eficiencia": 85.0}
    ],
    "top_operarios": [
        {"codigo": "OP-001", "nombre": "Carlos Ramirez", "eficiencia": 92.5},
        {"codigo": "OP-003", "nombre": "Maria Lopez", "eficiencia": 90.2},
        {"codigo": "OP-005", "nombre": "Pedro Garcia", "eficiencia": 89.8}
    ],
    "bottom_operarios": [
        {"codigo": "OP-008", "nombre": "Luis Torres", "eficiencia": 78.5},
        {"codigo": "OP-010", "nombre": "Ana Diaz", "eficiencia": 80.2}
    ],
    "ranking_maquinas": [
        {"codigo": "INY-001", "nombre": "Inyectora Principal", "eficiencia": 91.5},
        {"codigo": "EXT-001", "nombre": "Extrusora 1", "eficiencia": 88.0}
    ],
    "estadisticas_incidencias": {
        "total": 15,
        "abiertas": 3,
        "resueltas": 12,
        "por_tipo": [
            {"tipo": "MECANICO", "total": 8},
            {"tipo": "ELECTRICO", "total": 4},
            {"tipo": "CALIDAD", "total": 3}
        ]
    }
}
```


## Exportacion de Datos

El sistema permite exportar datos en formato CSV para analisis externo.


### Exportar a CSV

```
GET /api/reportes/exportar-csv/
```

Genera un archivo CSV con los datos solicitados.

**Parametros de consulta requeridos:**
- `tipo`: Tipo de reporte (eficiencia, produccion, incidencias)
- `fecha_inicio`: Fecha de inicio (YYYY-MM-DD)

**Parametros de consulta opcionales:**
- `fecha_fin`: Fecha de fin (por defecto hoy)

**Tipos de reporte disponibles:**

#### Reporte de Eficiencia
```
GET /api/reportes/exportar-csv/?tipo=eficiencia&fecha_inicio=2026-03-01&fecha_fin=2026-03-09
```

**Columnas del CSV:**
- Fecha
- Operario
- Maquina
- Produccion Real
- Produccion Teorica
- Eficiencia

#### Reporte de Produccion
```
GET /api/reportes/exportar-csv/?tipo=produccion&fecha_inicio=2026-03-01
```

**Columnas del CSV:**
- Fecha
- Maquina
- Operario
- Cantidad
- Observaciones

#### Reporte de Incidencias
```
GET /api/reportes/exportar-csv/?tipo=incidencias&fecha_inicio=2026-03-01
```

**Columnas del CSV:**
- Fecha
- Maquina
- Tipo
- Prioridad
- Estado
- Titulo
- Tiempo Abierta (min)

**Respuesta:**
Archivo CSV descargable con nombre `{tipo}_{fecha_inicio}_{fecha_fin}.csv`

**Errores posibles:**
- 400: Parametro tipo no especificado
- 400: Parametro fecha_inicio no especificado
- 400: Tipo de reporte no soportado


## Reportes Generados

El sistema mantiene un historial de reportes generados para poder
descargarlos nuevamente.


### Listar Reportes Generados

```
GET /api/reportes-generados/
```

Retorna el historial de reportes generados.

**Parametros de consulta opcionales:**
- `tipo`: Filtrar por tipo de reporte
- `formato`: Filtrar por formato (CSV, PDF, EXCEL)
- `empresa`: Filtrar por empresa

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Reporte Eficiencia Marzo 2026",
        "tipo": "EFICIENCIA",
        "formato": "CSV",
        "empresa": 1,
        "fecha_generacion": "2026-03-09T15:00:00Z",
        "generado_por": 3,
        "generado_por_nombre": "Gerente General",
        "parametros": {
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2026-03-09"
        },
        "archivo_url": "/media/reportes/eficiencia_2026-03-01_2026-03-09.csv"
    }
]
```


### Obtener Reporte Generado

```
GET /api/reportes-generados/{id}/
```


### Eliminar Reporte Generado

```
DELETE /api/reportes-generados/{id}/
```

Elimina un reporte del historial.


## Tipos de Reporte

| Tipo | Descripcion | Formatos |
|------|-------------|----------|
| EFICIENCIA | Metricas de eficiencia | CSV, PDF |
| PRODUCCION | Registros de produccion | CSV, PDF |
| INCIDENCIAS | Historial de incidencias | CSV, PDF |
| ASIGNACIONES | Historial de asignaciones | CSV, PDF |
| ALERTAS | Historial de alertas | CSV, PDF |


## Informacion de los Dashboards

### Dashboard Operario
Muestra informacion personal del operario:
- Asignacion activa actual
- Eficiencia del dia
- Produccion registrada
- Progreso hacia el objetivo diario

### Dashboard Supervisor
Muestra informacion de gestion del turno:
- Estado de todas las maquinas (semaforo)
- Alertas activas y criticas
- Sugerencias de reasignacion pendientes
- Ranking de operarios del turno
- Incidencias abiertas

### Dashboard Gerente
Muestra KPIs gerenciales:
- Eficiencia general de la planta
- OEE aproximado
- Tendencia de eficiencia (7 dias)
- Comparativa entre turnos
- Rankings de operarios y maquinas
- Estadisticas de incidencias


## Notas de Implementacion

1. Los dashboards se actualizan en tiempo real
2. Los reportes CSV son compatibles con Excel
3. Los reportes generados se guardan por 30 dias
4. Solo gerentes pueden acceder al dashboard gerencial
5. Los supervisores ven datos de su turno actual
6. Los operarios solo ven su informacion personal
