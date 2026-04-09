# Modulo de Operaciones - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de operaciones.
El modulo gestiona turnos, habilidades, operarios, asignaciones, eventos e incidencias.


## Turnos

Los turnos definen los horarios de trabajo en la planta.


### Listar Turnos

```
GET /api/turnos/
```

Retorna todos los turnos de la empresa.

**Parametros de consulta opcionales:**
- `activo`: Filtrar por estado activo (true/false)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Turno Mañana",
        "hora_inicio": "06:00:00",
        "hora_fin": "14:00:00",
        "empresa": 1,
        "activo": true,
        "duracion_horas": 8.0,
        "created_at": "2026-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "nombre": "Turno Tarde",
        "hora_inicio": "14:00:00",
        "hora_fin": "22:00:00",
        "empresa": 1,
        "activo": true,
        "duracion_horas": 8.0,
        "created_at": "2026-01-15T10:00:00Z"
    }
]
```


### Crear Turno

```
POST /api/turnos/
```

Crea un nuevo turno de trabajo.

**Body de la peticion:**
```json
{
    "nombre": "Turno Noche",
    "hora_inicio": "22:00:00",
    "hora_fin": "06:00:00",
    "empresa": 1
}
```


### Actualizar Turno

```
PUT /api/turnos/{id}/
PATCH /api/turnos/{id}/
```


### Eliminar Turno

```
DELETE /api/turnos/{id}/
```


### Obtener Turno Actual

```
GET /api/turnos/actual/
```

Retorna el turno que esta activo en este momento segun la hora actual.

**Respuesta exitosa (200):**
```json
{
    "turno": {
        "id": 1,
        "nombre": "Turno Mañana",
        "hora_inicio": "06:00:00",
        "hora_fin": "14:00:00"
    },
    "mensaje": "Turno activo actualmente"
}
```

**Sin turno activo (200):**
```json
{
    "turno": null,
    "mensaje": "No hay turno activo en este momento"
}
```


## Habilidades

Las habilidades representan las capacidades de los operarios para
manejar tipos especificos de maquinas.


### Listar Habilidades

```
GET /api/habilidades/
```

Retorna todas las habilidades registradas en la empresa.

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Operacion Inyectora",
        "descripcion": "Capacidad para operar maquinas inyectoras",
        "tipo_maquina": 1,
        "tipo_maquina_nombre": "Inyectora",
        "empresa": 1,
        "nivel_requerido": 2,
        "activa": true
    }
]
```


### Crear Habilidad

```
POST /api/habilidades/
```

Crea una nueva habilidad.

**Body de la peticion:**
```json
{
    "nombre": "Operacion Extrusora",
    "descripcion": "Capacidad para operar extrusoras",
    "tipo_maquina": 2,
    "empresa": 1,
    "nivel_requerido": 3
}
```


## Operarios

Los operarios son los trabajadores que realizan las tareas de produccion.


### Listar Operarios

```
GET /api/operarios/
```

Retorna todos los operarios de la empresa.

**Parametros de consulta opcionales:**
- `activo`: Filtrar por estado activo (true/false)
- `turno_actual`: Filtrar por turno (ID)
- `search`: Buscar por codigo o nombre

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "codigo_empleado": "OP-001",
        "usuario": 5,
        "usuario_nombre": "Carlos Ramirez",
        "usuario_email": "carlos@empresa.com",
        "turno_actual": 1,
        "turno_nombre": "Turno Mañana",
        "eficiencia_promedio": 92.5,
        "activo": true,
        "habilidades": [
            {
                "habilidad": 1,
                "habilidad_nombre": "Operacion Inyectora",
                "nivel": 3
            }
        ],
        "created_at": "2026-02-01T08:00:00Z"
    }
]
```


### Obtener Detalle de Operario

```
GET /api/operarios/{id}/
```

Retorna el detalle completo de un operario incluyendo historial de asignaciones.


### Crear Operario

```
POST /api/operarios/
```

Registra un nuevo operario. El usuario debe existir previamente con rol OPERARIO.

**Body de la peticion:**
```json
{
    "usuario": 5,
    "codigo_empleado": "OP-002",
    "turno_actual": 1
}
```


### Actualizar Operario

```
PUT /api/operarios/{id}/
PATCH /api/operarios/{id}/
```


### Eliminar Operario

```
DELETE /api/operarios/{id}/
```


### Asignar Habilidades

```
POST /api/operarios/{id}/asignar_habilidades/
```

Asigna o actualiza las habilidades de un operario.

**Body de la peticion:**
```json
{
    "habilidades": [
        {"habilidad_id": 1, "nivel": 3},
        {"habilidad_id": 2, "nivel": 2}
    ]
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Habilidades asignadas correctamente",
    "operario": {
        "id": 1,
        "codigo_empleado": "OP-001",
        "habilidades": [...]
    }
}
```


### Obtener Operarios Disponibles

```
GET /api/operarios/disponibles/
```

Retorna los operarios que estan activos y no tienen asignacion en este momento.

**Parametros de consulta opcionales:**
- `turno`: Filtrar por turno especifico (ID)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 2,
        "codigo_empleado": "OP-002",
        "usuario_nombre": "Ana Martinez",
        "eficiencia_promedio": 88.0,
        "habilidades": ["Operacion Inyectora"]
    }
]
```


## Asignaciones

Las asignaciones representan la asignacion de un operario a una maquina
durante un turno especifico.


### Listar Asignaciones

```
GET /api/asignaciones/
```

Retorna todas las asignaciones de la empresa.

**Parametros de consulta opcionales:**
- `fecha`: Filtrar por fecha especifica (YYYY-MM-DD)
- `estado`: Filtrar por estado (PROGRAMADA, ACTIVA, COMPLETADA, CANCELADA)
- `operario`: Filtrar por operario (ID)
- `maquina`: Filtrar por maquina (ID)
- `turno`: Filtrar por turno (ID)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "operario": 1,
        "operario_nombre": "Carlos Ramirez",
        "maquina": 1,
        "maquina_codigo": "INY-001",
        "maquina_nombre": "Inyectora Principal",
        "turno": 1,
        "turno_nombre": "Turno Mañana",
        "fecha": "2026-03-09",
        "estado": "ACTIVA",
        "estado_display": "Activa",
        "hora_inicio_real": "06:05:30",
        "hora_fin_real": null,
        "notas": "Produccion de botellas",
        "created_at": "2026-03-08T18:00:00Z"
    }
]
```


### Obtener Detalle de Asignacion

```
GET /api/asignaciones/{id}/
```

Retorna el detalle de una asignacion incluyendo eventos y produccion.


### Crear Asignacion

```
POST /api/asignaciones/
```

Crea una nueva asignacion programada.

**Body de la peticion:**
```json
{
    "operario": 1,
    "maquina": 1,
    "turno": 1,
    "fecha": "2026-03-10",
    "notas": "Produccion programada de botellas"
}
```

**Validaciones:**
- El operario debe estar activo
- La maquina debe estar activa y operando
- El operario no debe tener otra asignacion en la misma fecha y turno
- La maquina no debe tener otro operario asignado en la misma fecha y turno


### Actualizar Asignacion

```
PUT /api/asignaciones/{id}/
PATCH /api/asignaciones/{id}/
```

Solo se pueden modificar asignaciones en estado PROGRAMADA.


### Eliminar Asignacion

```
DELETE /api/asignaciones/{id}/
```

Solo se pueden eliminar asignaciones programadas.


### Iniciar Asignacion

```
POST /api/asignaciones/{id}/iniciar/
```

Inicia una asignacion programada. Registra la hora real de inicio.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Asignacion iniciada correctamente",
    "asignacion": {
        "id": 1,
        "estado": "ACTIVA",
        "hora_inicio_real": "06:05:30"
    }
}
```

**Error (400):**
```json
{
    "error": "Solo se pueden iniciar asignaciones programadas"
}
```


### Finalizar Asignacion

```
POST /api/asignaciones/{id}/finalizar/
```

Finaliza una asignacion activa. Registra la hora de fin y calcula metricas.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Asignacion finalizada correctamente",
    "asignacion": {
        "id": 1,
        "estado": "COMPLETADA",
        "hora_inicio_real": "06:05:30",
        "hora_fin_real": "14:02:15"
    },
    "duracion_horas": 7.94
}
```


### Cancelar Asignacion

```
POST /api/asignaciones/{id}/cancelar/
```

Cancela una asignacion programada o activa.

**Body de la peticion (opcional):**
```json
{
    "motivo": "Operario reporto enfermedad"
}
```


### Obtener Asignaciones de Hoy

```
GET /api/asignaciones/hoy/
```

Retorna todas las asignaciones del dia actual.


### Obtener Asignaciones Activas

```
GET /api/asignaciones/activas/
```

Retorna las asignaciones que estan actualmente en curso.


## Eventos

Los eventos registran lo que sucede durante una asignacion.


### Listar Eventos

```
GET /api/eventos/
```

Retorna todos los eventos registrados.

**Parametros de consulta opcionales:**
- `asignacion`: Filtrar por asignacion (ID)
- `tipo`: Filtrar por tipo (INICIO, FIN, PAUSA, REINICIO, PRODUCCION, etc.)
- `fecha`: Filtrar por fecha

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "asignacion": 1,
        "tipo": "INICIO",
        "tipo_display": "Inicio de turno",
        "fecha_hora": "2026-03-09T06:05:30Z",
        "descripcion": "Inicio de jornada laboral",
        "datos_adicionales": {}
    },
    {
        "id": 2,
        "asignacion": 1,
        "tipo": "PRODUCCION",
        "tipo_display": "Registro de produccion",
        "fecha_hora": "2026-03-09T08:00:00Z",
        "descripcion": "Registro de produccion: 150 unidades",
        "datos_adicionales": {"cantidad": 150, "producto": "Botella PET 500ml"}
    }
]
```


### Crear Evento

```
POST /api/eventos/
```

Registra un nuevo evento.

**Body de la peticion:**
```json
{
    "asignacion": 1,
    "tipo": "PAUSA",
    "descripcion": "Pausa por almuerzo",
    "datos_adicionales": {"duracion_minutos": 30}
}
```

**Tipos de evento disponibles:**
- INICIO: Inicio de la asignacion
- FIN: Fin de la asignacion
- PAUSA: Pausa temporal
- REINICIO: Reinicio despues de pausa
- PRODUCCION: Registro de produccion
- INCIDENCIA: Reporte de incidencia
- CAMBIO_PRODUCTO: Cambio de producto
- OTRO: Otros eventos


### Obtener Eventos por Asignacion

```
GET /api/eventos/por_asignacion/?asignacion={id}
```

Retorna todos los eventos de una asignacion especifica ordenados cronologicamente.


## Incidencias

Las incidencias registran problemas o situaciones especiales con las maquinas.


### Listar Incidencias

```
GET /api/incidencias/
```

Retorna todas las incidencias de la empresa.

**Parametros de consulta opcionales:**
- `estado`: Filtrar por estado (ABIERTA, EN_PROCESO, RESUELTA, CERRADA)
- `prioridad`: Filtrar por prioridad (BAJA, MEDIA, ALTA, CRITICA)
- `maquina`: Filtrar por maquina (ID)
- `tipo`: Filtrar por tipo (MECANICO, ELECTRICO, CALIDAD, SEGURIDAD, OTRO)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "maquina": 1,
        "maquina_codigo": "INY-001",
        "maquina_nombre": "Inyectora Principal",
        "tipo": "MECANICO",
        "tipo_display": "Problema mecanico",
        "prioridad": "ALTA",
        "prioridad_display": "Alta",
        "estado": "ABIERTA",
        "estado_display": "Abierta",
        "titulo": "Falla en sistema hidraulico",
        "descripcion": "Se detecta fuga de aceite hidraulico en el cilindro principal",
        "fecha_reporte": "2026-03-09T10:30:00Z",
        "reportado_por": 5,
        "reportado_por_nombre": "Carlos Ramirez",
        "asignacion_relacionada": 1,
        "fecha_resolucion": null,
        "tiempo_abierta_minutos": 45
    }
]
```


### Obtener Detalle de Incidencia

```
GET /api/incidencias/{id}/
```


### Crear Incidencia

```
POST /api/incidencias/
```

Reporta una nueva incidencia.

**Body de la peticion:**
```json
{
    "maquina": 1,
    "tipo": "MECANICO",
    "prioridad": "ALTA",
    "titulo": "Falla en sistema hidraulico",
    "descripcion": "Se detecta fuga de aceite hidraulico",
    "asignacion_relacionada": 1
}
```


### Actualizar Incidencia

```
PUT /api/incidencias/{id}/
PATCH /api/incidencias/{id}/
```


### Resolver Incidencia

```
POST /api/incidencias/{id}/resolver/
```

Marca una incidencia como resuelta.

**Body de la peticion:**
```json
{
    "solucion": "Se reemplazo el sello del cilindro hidraulico"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Incidencia resuelta correctamente",
    "incidencia": {
        "id": 1,
        "estado": "RESUELTA",
        "fecha_resolucion": "2026-03-09T11:15:00Z",
        "solucion_aplicada": "Se reemplazo el sello del cilindro hidraulico"
    },
    "tiempo_resolucion_minutos": 45
}
```


### Obtener Incidencias Abiertas

```
GET /api/incidencias/abiertas/
```

Retorna todas las incidencias con estado ABIERTA o EN_PROCESO.


### Obtener Incidencias por Maquina

```
GET /api/incidencias/por_maquina/?maquina={id}
```

Retorna todas las incidencias de una maquina especifica.


## Estados de Asignacion

| Estado | Descripcion |
|--------|-------------|
| PROGRAMADA | Asignacion creada pero no iniciada |
| ACTIVA | Asignacion en curso |
| COMPLETADA | Asignacion finalizada correctamente |
| CANCELADA | Asignacion cancelada |


## Estados de Incidencia

| Estado | Descripcion |
|--------|-------------|
| ABIERTA | Incidencia reportada, pendiente de atencion |
| EN_PROCESO | Incidencia siendo atendida |
| RESUELTA | Incidencia solucionada |
| CERRADA | Incidencia cerrada (puede o no estar resuelta) |


## Prioridades de Incidencia

| Prioridad | Descripcion | Tiempo respuesta esperado |
|-----------|-------------|--------------------------|
| BAJA | Problema menor | 24 horas |
| MEDIA | Problema moderado | 4 horas |
| ALTA | Problema serio | 1 hora |
| CRITICA | Problema urgente | 15 minutos |


## Notas de Implementacion

1. Las asignaciones generan eventos automaticos al iniciar y finalizar
2. Las incidencias criticas generan alertas automaticas
3. El tiempo de resolucion de incidencias afecta las metricas de disponibilidad
4. Los eventos de produccion se reflejan en el modulo de metricas
5. La eficiencia promedio del operario se actualiza automaticamente
