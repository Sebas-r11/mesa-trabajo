# Modulo de Metricas - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de metricas.
El modulo gestiona registros de produccion, metricas de eficiencia y objetivos.


## Registros de Produccion

Los registros de produccion capturan la cantidad de unidades producidas
durante una asignacion.


### Listar Registros de Produccion

```
GET /api/produccion/
```

Retorna todos los registros de produccion de la empresa.

**Parametros de consulta opcionales:**
- `asignacion`: Filtrar por asignacion (ID)
- `fecha`: Filtrar por fecha especifica (YYYY-MM-DD)
- `maquina`: Filtrar por maquina a traves de la asignacion

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "asignacion": 1,
        "cantidad": 150,
        "fecha_hora": "2026-03-09T08:00:00Z",
        "observaciones": "Produccion normal",
        "registrado_por": 5,
        "registrado_por_nombre": "Carlos Ramirez",
        "asignacion_detalle": {
            "operario_nombre": "Carlos Ramirez",
            "maquina_codigo": "INY-001"
        },
        "created_at": "2026-03-09T08:00:00Z"
    }
]
```


### Obtener Detalle de Registro

```
GET /api/produccion/{id}/
```


### Crear Registro de Produccion

```
POST /api/produccion/
```

Registra unidades producidas.

**Body de la peticion:**
```json
{
    "asignacion": 1,
    "cantidad": 150,
    "observaciones": "Produccion normal"
}
```

**Validaciones:**
- La asignacion debe estar activa
- La cantidad debe ser mayor a cero
- El usuario debe tener permisos para registrar produccion

**Respuesta exitosa (201):**
```json
{
    "id": 1,
    "asignacion": 1,
    "cantidad": 150,
    "fecha_hora": "2026-03-09T08:00:00Z",
    "observaciones": "Produccion normal",
    "registrado_por": 5
}
```


### Actualizar Registro

```
PUT /api/produccion/{id}/
PATCH /api/produccion/{id}/
```

Permite corregir un registro de produccion.


### Eliminar Registro

```
DELETE /api/produccion/{id}/
```


### Obtener Resumen de Produccion

```
GET /api/produccion/resumen/
```

Retorna un resumen de produccion por periodo.

**Parametros de consulta:**
- `fecha_inicio`: Fecha de inicio del periodo (YYYY-MM-DD)
- `fecha_fin`: Fecha de fin del periodo (YYYY-MM-DD)

**Respuesta exitosa (200):**
```json
{
    "fecha_inicio": "2026-03-01",
    "fecha_fin": "2026-03-09",
    "total_produccion": 15000,
    "cantidad_registros": 85,
    "promedio_por_registro": 176.47,
    "produccion_por_maquina": [
        {
            "maquina": "INY-001",
            "total": 8000
        },
        {
            "maquina": "INY-002",
            "total": 7000
        }
    ],
    "produccion_por_turno": [
        {
            "turno": "Turno Mañana",
            "total": 9000
        },
        {
            "turno": "Turno Tarde",
            "total": 6000
        }
    ]
}
```


## Metricas de Eficiencia

Las metricas de eficiencia calculan el rendimiento de operarios y maquinas.


### Listar Metricas de Eficiencia

```
GET /api/metricas/
```

Retorna todas las metricas de eficiencia calculadas.

**Parametros de consulta opcionales:**
- `operario`: Filtrar por operario (ID)
- `maquina`: Filtrar por maquina (ID)
- `fecha`: Filtrar por fecha especifica
- `fecha_inicio`: Filtrar desde fecha
- `fecha_fin`: Filtrar hasta fecha

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "operario": 1,
        "operario_nombre": "Carlos Ramirez",
        "maquina": 1,
        "maquina_codigo": "INY-001",
        "asignacion": 1,
        "fecha": "2026-03-09",
        "produccion_real": 750,
        "produccion_teorica": 800,
        "eficiencia_calculada": 93.75,
        "tiempo_operativo_minutos": 450,
        "tiempo_parada_minutos": 30,
        "disponibilidad": 93.75,
        "created_at": "2026-03-09T14:05:00Z"
    }
]
```


### Obtener Detalle de Metrica

```
GET /api/metricas/{id}/
```


### Crear Metrica de Eficiencia

```
POST /api/metricas/
```

Crea un registro de metrica manualmente. Normalmente las metricas se
calculan automaticamente al finalizar asignaciones.

**Body de la peticion:**
```json
{
    "operario": 1,
    "maquina": 1,
    "asignacion": 1,
    "fecha": "2026-03-09",
    "produccion_real": 750,
    "produccion_teorica": 800,
    "tiempo_operativo_minutos": 450,
    "tiempo_parada_minutos": 30
}
```


### Calcular Metrica para Asignacion

```
POST /api/metricas/calcular_para_asignacion/
```

Calcula y guarda la metrica de eficiencia para una asignacion especifica.

**Body de la peticion:**
```json
{
    "asignacion_id": 1
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Metrica calculada correctamente",
    "metrica": {
        "id": 1,
        "eficiencia_calculada": 93.75,
        "disponibilidad": 93.75
    }
}
```


### Obtener Resumen de Metricas

```
GET /api/metricas/resumen/
```

Retorna un resumen de metricas por periodo.

**Parametros de consulta:**
- `fecha_inicio`: Fecha de inicio (YYYY-MM-DD)
- `fecha_fin`: Fecha de fin (YYYY-MM-DD)

**Respuesta exitosa (200):**
```json
{
    "fecha_inicio": "2026-03-01",
    "fecha_fin": "2026-03-09",
    "eficiencia_promedio": 91.5,
    "disponibilidad_promedio": 92.3,
    "total_registros": 45,
    "metricas_por_operario": [
        {
            "operario": "Carlos Ramirez",
            "eficiencia_promedio": 93.75
        }
    ],
    "metricas_por_maquina": [
        {
            "maquina": "INY-001",
            "eficiencia_promedio": 92.0
        }
    ]
}
```


### Obtener Tendencia de Eficiencia

```
GET /api/metricas/tendencia/
```

Retorna la tendencia de eficiencia por dia.

**Parametros de consulta:**
- `dias`: Numero de dias hacia atras (por defecto 7)
- `operario`: Filtrar por operario especifico (ID)
- `maquina`: Filtrar por maquina especifica (ID)

**Respuesta exitosa (200):**
```json
{
    "dias": 7,
    "tendencia": [
        {"fecha": "2026-03-03", "eficiencia": 90.5},
        {"fecha": "2026-03-04", "eficiencia": 91.2},
        {"fecha": "2026-03-05", "eficiencia": 89.8},
        {"fecha": "2026-03-06", "eficiencia": 92.0},
        {"fecha": "2026-03-07", "eficiencia": 93.5},
        {"fecha": "2026-03-08", "eficiencia": 91.8},
        {"fecha": "2026-03-09", "eficiencia": 93.75}
    ],
    "promedio_periodo": 91.79
}
```


## Objetivos de Produccion

Los objetivos de produccion definen las metas a alcanzar por operarios,
maquinas o turnos.


### Listar Objetivos

```
GET /api/objetivos/
```

Retorna todos los objetivos de produccion.

**Parametros de consulta opcionales:**
- `activo`: Filtrar por estado activo
- `tipo`: Filtrar por tipo de objetivo
- `operario`: Filtrar por operario
- `maquina`: Filtrar por maquina
- `turno`: Filtrar por turno

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Objetivo Diario INY-001",
        "descripcion": "Meta diaria de produccion para Inyectora Principal",
        "empresa": 1,
        "tipo_objetivo": "DIARIO",
        "maquina": 1,
        "maquina_nombre": "Inyectora Principal",
        "operario": null,
        "turno": null,
        "valor_objetivo": 1000,
        "unidad_medida": "unidades",
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2026-03-31",
        "activo": true,
        "porcentaje_cumplimiento": 85.5
    }
]
```


### Obtener Detalle de Objetivo

```
GET /api/objetivos/{id}/
```


### Crear Objetivo

```
POST /api/objetivos/
```

Crea un nuevo objetivo de produccion.

**Body de la peticion:**
```json
{
    "nombre": "Objetivo Semanal Turno Mañana",
    "descripcion": "Meta semanal para el turno de la mañana",
    "empresa": 1,
    "tipo_objetivo": "SEMANAL",
    "turno": 1,
    "valor_objetivo": 5000,
    "unidad_medida": "unidades",
    "fecha_inicio": "2026-03-01",
    "fecha_fin": "2026-03-31"
}
```

**Tipos de objetivo disponibles:**
- DIARIO: Objetivo por dia
- SEMANAL: Objetivo por semana
- MENSUAL: Objetivo por mes


### Actualizar Objetivo

```
PUT /api/objetivos/{id}/
PATCH /api/objetivos/{id}/
```


### Eliminar Objetivo

```
DELETE /api/objetivos/{id}/
```


### Evaluar Cumplimiento de Objetivos

```
GET /api/objetivos/evaluar/
```

Evalua el cumplimiento de todos los objetivos activos.

**Parametros de consulta opcionales:**
- `fecha`: Fecha para evaluar (por defecto hoy)

**Respuesta exitosa (200):**
```json
{
    "fecha": "2026-03-09",
    "objetivos_evaluados": [
        {
            "objetivo": "Objetivo Diario INY-001",
            "valor_objetivo": 1000,
            "valor_actual": 855,
            "porcentaje_cumplimiento": 85.5,
            "estado": "EN_PROGRESO"
        }
    ],
    "resumen": {
        "total_objetivos": 5,
        "cumplidos": 3,
        "en_progreso": 2,
        "no_cumplidos": 0
    }
}
```


## Formulas de Calculo

### Eficiencia
```
Eficiencia = (Produccion Real / Produccion Teorica) * 100
```

### Disponibilidad
```
Disponibilidad = (Tiempo Operativo / (Tiempo Operativo + Tiempo Parada)) * 100
```

### OEE (Overall Equipment Effectiveness)
```
OEE = Disponibilidad * Rendimiento * Calidad / 10000
```


## Notas de Implementacion

1. Las metricas se calculan automaticamente al finalizar asignaciones
2. Los registros de produccion generan eventos en el modulo de operaciones
3. Los objetivos pueden asignarse a operarios, maquinas o turnos
4. La eficiencia promedio del operario se actualiza con cada metrica
5. Las alertas se generan cuando la eficiencia cae por debajo del umbral
