# Modulo de Reasignaciones - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de reasignaciones.
El modulo gestiona sugerencias inteligentes para reasignar operarios a maquinas.


## Sugerencias de Reasignacion

Las sugerencias de reasignacion son propuestas generadas por el sistema
para mejorar la eficiencia asignando operarios a maquinas donde pueden
ser mas productivos.


### Listar Sugerencias

```
GET /api/sugerencias/
```

Retorna todas las sugerencias de reasignacion de la empresa.

**Parametros de consulta opcionales:**
- `estado`: Filtrar por estado (PENDIENTE, ACEPTADA, RECHAZADA, EXPIRADA)
- `operario`: Filtrar por operario (ID)
- `prioridad`: Filtrar por prioridad (BAJA, MEDIA, ALTA, URGENTE)
- `fecha`: Filtrar por fecha

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "empresa": 1,
        "operario_origen": 1,
        "operario_origen_nombre": "Carlos Ramirez",
        "maquina_origen": 2,
        "maquina_origen_codigo": "INY-002",
        "maquina_destino": 1,
        "maquina_destino_codigo": "INY-001",
        "motivo": "Operario con mayor eficiencia historica en maquina INY-001",
        "mejora_estimada": 15.5,
        "prioridad": "ALTA",
        "prioridad_display": "Alta",
        "estado": "PENDIENTE",
        "estado_display": "Pendiente",
        "fecha_sugerencia": "2026-03-09T10:00:00Z",
        "fecha_expiracion": "2026-03-09T14:00:00Z",
        "aceptada_por": null,
        "fecha_respuesta": null,
        "notas": null
    }
]
```


### Obtener Detalle de Sugerencia

```
GET /api/sugerencias/{id}/
```

Retorna el detalle completo de una sugerencia incluyendo analisis.

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "empresa": 1,
    "operario_origen": 1,
    "operario_origen_nombre": "Carlos Ramirez",
    "operario_origen_eficiencia": 88.5,
    "maquina_origen": 2,
    "maquina_origen_codigo": "INY-002",
    "maquina_destino": 1,
    "maquina_destino_codigo": "INY-001",
    "motivo": "Operario con mayor eficiencia historica en maquina INY-001",
    "analisis": {
        "eficiencia_actual": 88.5,
        "eficiencia_estimada": 104.0,
        "mejora_porcentual": 15.5,
        "historial_en_destino": {
            "asignaciones_previas": 5,
            "eficiencia_promedio": 96.5
        }
    },
    "mejora_estimada": 15.5,
    "prioridad": "ALTA",
    "estado": "PENDIENTE",
    "fecha_sugerencia": "2026-03-09T10:00:00Z",
    "fecha_expiracion": "2026-03-09T14:00:00Z"
}
```


### Aceptar Sugerencia

```
POST /api/sugerencias/{id}/aceptar/
```

Acepta una sugerencia de reasignacion y ejecuta el cambio.

**Body de la peticion (opcional):**
```json
{
    "notas": "Reasignacion aprobada por necesidad de produccion"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Sugerencia aceptada y reasignacion ejecutada",
    "sugerencia": {
        "id": 1,
        "estado": "ACEPTADA",
        "aceptada_por": 3,
        "fecha_respuesta": "2026-03-09T10:15:00Z"
    },
    "asignacion_creada": {
        "id": 15,
        "operario": 1,
        "maquina": 1,
        "estado": "PROGRAMADA"
    }
}
```

**Errores posibles:**
- 400: La sugerencia ya fue procesada
- 400: La sugerencia ha expirado
- 400: El operario ya tiene asignacion activa
- 400: La maquina ya tiene operario asignado


### Rechazar Sugerencia

```
POST /api/sugerencias/{id}/rechazar/
```

Rechaza una sugerencia de reasignacion.

**Body de la peticion (opcional):**
```json
{
    "motivo_rechazo": "El operario tiene restriccion medica"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Sugerencia rechazada",
    "sugerencia": {
        "id": 1,
        "estado": "RECHAZADA",
        "fecha_respuesta": "2026-03-09T10:15:00Z",
        "notas": "El operario tiene restriccion medica"
    }
}
```


### Obtener Sugerencias Pendientes

```
GET /api/sugerencias/pendientes/
```

Retorna todas las sugerencias con estado PENDIENTE que no han expirado.

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "operario_origen_nombre": "Carlos Ramirez",
        "maquina_destino_codigo": "INY-001",
        "mejora_estimada": 15.5,
        "prioridad": "ALTA",
        "tiempo_restante_minutos": 210
    }
]
```


### Generar Sugerencias

```
POST /api/sugerencias/generar/
```

Genera nuevas sugerencias de reasignacion basadas en el analisis
de eficiencia actual.

**Body de la peticion (opcional):**
```json
{
    "turno": 1,
    "solo_criticas": false
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Sugerencias generadas",
    "sugerencias_creadas": 3,
    "sugerencias": [
        {
            "id": 2,
            "operario": "Carlos Ramirez",
            "maquina_destino": "INY-001",
            "mejora_estimada": 15.5
        },
        {
            "id": 3,
            "operario": "Ana Martinez",
            "maquina_destino": "EXT-002",
            "mejora_estimada": 8.2
        }
    ]
}
```


### Obtener Estadisticas de Sugerencias

```
GET /api/sugerencias/estadisticas/
```

Retorna estadisticas sobre las sugerencias de reasignacion.

**Parametros de consulta opcionales:**
- `fecha_inicio`: Fecha de inicio del periodo
- `fecha_fin`: Fecha de fin del periodo

**Respuesta exitosa (200):**
```json
{
    "periodo": {
        "inicio": "2026-03-01",
        "fin": "2026-03-09"
    },
    "total_sugerencias": 25,
    "por_estado": {
        "aceptadas": 15,
        "rechazadas": 5,
        "pendientes": 3,
        "expiradas": 2
    },
    "tasa_aceptacion": 60.0,
    "mejora_promedio_estimada": 12.5,
    "mejora_real_promedio": 10.8,
    "tiempo_respuesta_promedio_minutos": 45
}
```


## Criterios de Generacion de Sugerencias

El sistema analiza varios factores para generar sugerencias:

1. **Eficiencia historica**: Compara la eficiencia del operario en diferentes maquinas
2. **Habilidades**: Verifica que el operario tenga las habilidades necesarias
3. **Disponibilidad**: La maquina destino debe estar disponible
4. **Carga de trabajo**: Balancea la carga entre operarios
5. **Urgencia**: Prioriza maquinas con produccion critica


## Estados de Sugerencia

| Estado | Descripcion |
|--------|-------------|
| PENDIENTE | Esperando respuesta del supervisor |
| ACEPTADA | Sugerencia aceptada y ejecutada |
| RECHAZADA | Sugerencia rechazada por el supervisor |
| EXPIRADA | Sugerencia vencida sin respuesta |


## Prioridades de Sugerencia

| Prioridad | Descripcion | Tiempo de expiracion |
|-----------|-------------|---------------------|
| URGENTE | Requiere accion inmediata | 1 hora |
| ALTA | Importante para eficiencia | 4 horas |
| MEDIA | Mejora recomendada | 8 horas |
| BAJA | Mejora opcional | 24 horas |


## Notas de Implementacion

1. Las sugerencias se generan automaticamente cada hora
2. Las sugerencias urgentes generan notificaciones inmediatas
3. Al aceptar una sugerencia, se crea automaticamente la nueva asignacion
4. Las sugerencias expiradas se archivan para analisis
5. La mejora estimada se calcula usando el historial del operario
6. Solo supervisores y gerentes pueden aceptar/rechazar sugerencias
