# Modulo de Alertas - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de alertas.
El modulo gestiona reglas de alerta, alertas generadas y notificaciones.


## Reglas de Alerta

Las reglas de alerta definen las condiciones bajo las cuales se generan
alertas automaticas en el sistema.


### Listar Reglas de Alerta

```
GET /api/reglas-alerta/
```

Retorna todas las reglas de alerta de la empresa.

**Parametros de consulta opcionales:**
- `activa`: Filtrar por estado activo (true/false)
- `tipo`: Filtrar por tipo de regla

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "nombre": "Alerta de Baja Eficiencia",
        "descripcion": "Se activa cuando la eficiencia cae por debajo del 70%",
        "empresa": 1,
        "tipo_regla": "EFICIENCIA_BAJA",
        "tipo_display": "Eficiencia Baja",
        "valor_umbral": 70.0,
        "operador_comparacion": "MENOR",
        "prioridad_generada": "ALTA",
        "activa": true,
        "created_at": "2026-01-15T10:00:00Z"
    },
    {
        "id": 2,
        "nombre": "Alerta de Maquina Parada",
        "descripcion": "Se activa cuando una maquina lleva mas de 30 minutos parada",
        "empresa": 1,
        "tipo_regla": "MAQUINA_PARADA",
        "tipo_display": "Maquina Parada",
        "valor_umbral": 30.0,
        "operador_comparacion": "MAYOR",
        "prioridad_generada": "CRITICA",
        "activa": true,
        "created_at": "2026-01-15T10:00:00Z"
    }
]
```


### Obtener Detalle de Regla

```
GET /api/reglas-alerta/{id}/
```


### Crear Regla de Alerta

```
POST /api/reglas-alerta/
```

Crea una nueva regla de alerta.

**Body de la peticion:**
```json
{
    "nombre": "Alerta de Produccion Insuficiente",
    "descripcion": "Se activa cuando la produccion del turno es menor al 80% del objetivo",
    "empresa": 1,
    "tipo_regla": "PRODUCCION_BAJA",
    "valor_umbral": 80.0,
    "operador_comparacion": "MENOR",
    "prioridad_generada": "MEDIA"
}
```

**Tipos de regla disponibles:**
- EFICIENCIA_BAJA: La eficiencia cae por debajo del umbral
- MAQUINA_PARADA: La maquina esta parada mas tiempo del umbral
- PRODUCCION_BAJA: La produccion es menor al umbral (porcentaje del objetivo)
- INCIDENCIA_ABIERTA: Hay incidencias abiertas por mas tiempo del umbral
- OPERARIO_AUSENTE: Un operario no tiene asignacion en su turno
- MANTENIMIENTO_PENDIENTE: Hay mantenimiento pendiente cercano

**Operadores de comparacion:**
- MENOR: El valor actual es menor que el umbral
- MAYOR: El valor actual es mayor que el umbral
- IGUAL: El valor actual es igual al umbral


### Actualizar Regla

```
PUT /api/reglas-alerta/{id}/
PATCH /api/reglas-alerta/{id}/
```


### Eliminar Regla

```
DELETE /api/reglas-alerta/{id}/
```


### Activar Regla

```
POST /api/reglas-alerta/{id}/activar/
```

Activa una regla de alerta desactivada.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Regla activada correctamente",
    "regla": {
        "id": 1,
        "nombre": "Alerta de Baja Eficiencia",
        "activa": true
    }
}
```


### Desactivar Regla

```
POST /api/reglas-alerta/{id}/desactivar/
```

Desactiva una regla de alerta. Las alertas existentes no se ven afectadas.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Regla desactivada correctamente",
    "regla": {
        "id": 1,
        "nombre": "Alerta de Baja Eficiencia",
        "activa": false
    }
}
```


### Evaluar Regla

```
POST /api/reglas-alerta/{id}/evaluar/
```

Evalua manualmente una regla de alerta y genera alertas si corresponde.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Regla evaluada",
    "alertas_generadas": 2,
    "detalles": [
        {
            "maquina": "INY-001",
            "eficiencia": 65.5,
            "alerta_generada": true
        }
    ]
}
```


## Alertas

Las alertas son las instancias generadas cuando se cumple una condicion
definida en una regla de alerta.


### Listar Alertas

```
GET /api/alertas/
```

Retorna todas las alertas de la empresa.

**Parametros de consulta opcionales:**
- `estado`: Filtrar por estado (ACTIVA, RECONOCIDA, RESUELTA, DESCARTADA)
- `prioridad`: Filtrar por prioridad (BAJA, MEDIA, ALTA, CRITICA)
- `regla`: Filtrar por regla de alerta (ID)
- `fecha`: Filtrar por fecha

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "regla": 1,
        "regla_nombre": "Alerta de Baja Eficiencia",
        "empresa": 1,
        "titulo": "Eficiencia baja en INY-001",
        "mensaje": "La eficiencia de la maquina INY-001 ha caido a 65.5%, por debajo del umbral de 70%",
        "prioridad": "ALTA",
        "prioridad_display": "Alta",
        "estado": "ACTIVA",
        "estado_display": "Activa",
        "fecha_generacion": "2026-03-09T10:30:00Z",
        "maquina_relacionada": 1,
        "operario_relacionado": 1,
        "incidencia_relacionada": null,
        "fecha_resolucion": null,
        "resuelta_por": null,
        "notas_resolucion": null,
        "tiempo_activa_minutos": 45
    }
]
```


### Obtener Detalle de Alerta

```
GET /api/alertas/{id}/
```


### Reconocer Alerta

```
POST /api/alertas/{id}/reconocer/
```

Marca una alerta como reconocida (el supervisor la ha visto).

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Alerta reconocida",
    "alerta": {
        "id": 1,
        "estado": "RECONOCIDA"
    }
}
```


### Resolver Alerta

```
POST /api/alertas/{id}/resolver/
```

Marca una alerta como resuelta.

**Body de la peticion:**
```json
{
    "notas_resolucion": "Se ajustaron los parametros de la maquina"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Alerta resuelta",
    "alerta": {
        "id": 1,
        "estado": "RESUELTA",
        "fecha_resolucion": "2026-03-09T11:15:00Z",
        "notas_resolucion": "Se ajustaron los parametros de la maquina"
    },
    "tiempo_resolucion_minutos": 45
}
```


### Descartar Alerta

```
POST /api/alertas/{id}/descartar/
```

Descarta una alerta (falso positivo o no relevante).

**Body de la peticion (opcional):**
```json
{
    "motivo": "Falso positivo por reinicio de sistema"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Alerta descartada",
    "alerta": {
        "id": 1,
        "estado": "DESCARTADA"
    }
}
```


### Obtener Alertas Activas

```
GET /api/alertas/activas/
```

Retorna todas las alertas con estado ACTIVA ordenadas por prioridad.

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "titulo": "Eficiencia baja en INY-001",
        "prioridad": "ALTA",
        "tiempo_activa_minutos": 45
    }
]
```


### Obtener Conteo de Alertas

```
GET /api/alertas/conteo/
```

Retorna el conteo de alertas por estado y prioridad.

**Respuesta exitosa (200):**
```json
{
    "total": 15,
    "por_estado": {
        "activas": 3,
        "reconocidas": 5,
        "resueltas": 6,
        "descartadas": 1
    },
    "por_prioridad": {
        "critica": 1,
        "alta": 4,
        "media": 7,
        "baja": 3
    },
    "activas_criticas": 1,
    "activas_altas": 2
}
```


## Notificaciones

Las notificaciones informan a los usuarios sobre alertas y eventos
importantes.


### Listar Notificaciones

```
GET /api/notificaciones/
```

Retorna todas las notificaciones del usuario autenticado.

**Parametros de consulta opcionales:**
- `leida`: Filtrar por estado de lectura (true/false)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "usuario": 5,
        "alerta": 1,
        "titulo": "Nueva alerta de eficiencia",
        "mensaje": "Se ha generado una alerta de baja eficiencia en INY-001",
        "tipo": "ALERTA",
        "tipo_display": "Alerta",
        "leida": false,
        "fecha_envio": "2026-03-09T10:30:00Z",
        "fecha_lectura": null
    }
]
```


### Obtener Notificacion

```
GET /api/notificaciones/{id}/
```


### Marcar Notificacion como Leida

```
POST /api/notificaciones/{id}/marcar_leida/
```

Marca una notificacion como leida.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Notificacion marcada como leida",
    "notificacion": {
        "id": 1,
        "leida": true,
        "fecha_lectura": "2026-03-09T10:35:00Z"
    }
}
```


### Marcar Todas como Leidas

```
POST /api/notificaciones/marcar_todas_leidas/
```

Marca todas las notificaciones del usuario como leidas.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Todas las notificaciones marcadas como leidas",
    "cantidad_marcadas": 5
}
```


### Obtener Notificaciones No Leidas

```
GET /api/notificaciones/no_leidas/
```

Retorna las notificaciones no leidas del usuario.


### Obtener Conteo de No Leidas

```
GET /api/notificaciones/conteo_no_leidas/
```

Retorna el numero de notificaciones no leidas.

**Respuesta exitosa (200):**
```json
{
    "no_leidas": 3
}
```


## Estados de Alerta

| Estado | Descripcion |
|--------|-------------|
| ACTIVA | Alerta generada, pendiente de atencion |
| RECONOCIDA | Alerta vista por el supervisor |
| RESUELTA | Alerta atendida y solucionada |
| DESCARTADA | Alerta descartada (falso positivo) |


## Prioridades de Alerta

| Prioridad | Color | Descripcion |
|-----------|-------|-------------|
| CRITICA | Rojo | Requiere atencion inmediata |
| ALTA | Naranja | Requiere atencion pronto |
| MEDIA | Amarillo | Puede esperar un poco |
| BAJA | Azul | Informativa |


## Tipos de Notificacion

| Tipo | Descripcion |
|------|-------------|
| ALERTA | Notificacion de alerta generada |
| SISTEMA | Notificacion del sistema |
| INFORMATIVA | Informacion general |


## Notas de Implementacion

1. Las reglas se evaluan automaticamente cada cierto tiempo (configurable)
2. Las alertas criticas generan notificaciones inmediatas
3. Los supervisores reciben notificaciones de su area
4. Los gerentes reciben alertas criticas de toda la empresa
5. Las notificaciones no leidas se muestran en el dashboard
6. Las alertas resueltas se archivan para reportes historicos
