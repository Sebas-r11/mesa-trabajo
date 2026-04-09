# Modulo de Ordenes de Produccion - FLEX-OP

Este documento describe todos los endpoints disponibles en el modulo de ordenes.
El modulo gestiona las ordenes de produccion y la cola de despacho.


## Ordenes de Produccion

Las ordenes de produccion representan el trabajo que debe realizarse
en la planta. Contienen informacion sobre producto, cantidad y fechas.


### Listar Ordenes

```
GET /api/ordenes/
```

Retorna todas las ordenes de produccion de la empresa.

**Parametros de consulta opcionales:**
- `estado`: Filtrar por estado (PENDIENTE, EN_PROGRESO, COMPLETADA, CANCELADA)
- `prioridad`: Filtrar por prioridad (1-5, donde 5 es maxima)
- `maquina_asignada`: Filtrar por maquina (ID)
- `search`: Buscar por numero de orden o producto

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "numero_orden": "ORD-2026-0001",
        "producto": 1,
        "cantidad_solicitada": 1000,
        "cantidad_producida": 750,
        "porcentaje": 75.0,
        "fecha_entrega_estimada": "2026-03-15",
        "prioridad": 3,
        "estado": "EN_PROGRESO",
        "estado_display": "En Progreso"
    }
]
```


### Obtener Detalle de Orden

```
GET /api/ordenes/{id}/
```

Retorna el detalle completo de una orden incluyendo progreso y asignaciones.

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "numero_orden": "ORD-2026-0001",
    "empresa": 1,
    "producto": 1,
    "producto_nombre": "Botella PET 500ml",
    "cantidad_solicitada": 1000,
    "cantidad_producida": 750,
    "cantidad_pendiente": 250,
    "porcentaje_completado": 75.0,
    "fecha_creacion": "2026-03-01T10:00:00Z",
    "fecha_entrega_estimada": "2026-03-15",
    "dias_restantes": 6,
    "prioridad": 3,
    "estado": "EN_PROGRESO",
    "estado_display": "En Progreso",
    "maquina_asignada": 1,
    "maquina_nombre": "Inyectora Principal",
    "notas": "Pedido urgente para cliente VIP",
    "created_at": "2026-03-01T10:00:00Z",
    "updated_at": "2026-03-09T14:00:00Z"
}
```


### Crear Orden

```
POST /api/ordenes/
```

Crea una nueva orden de produccion.

**Body de la peticion:**
```json
{
    "empresa": 1,
    "producto": 1,
    "cantidad_solicitada": 1000,
    "fecha_entrega_estimada": "2026-03-15",
    "prioridad": 3,
    "maquina_asignada": 1,
    "notas": "Pedido urgente para cliente VIP"
}
```

**Validaciones:**
- La cantidad debe ser mayor a cero
- La fecha de entrega debe ser futura
- El producto debe existir y estar activo
- La maquina debe ser compatible con el producto

**Respuesta exitosa (201):**
```json
{
    "id": 2,
    "numero_orden": "ORD-2026-0002",
    "producto": 1,
    "cantidad_solicitada": 1000,
    "estado": "PENDIENTE"
}
```


### Actualizar Orden

```
PUT /api/ordenes/{id}/
PATCH /api/ordenes/{id}/
```

Actualiza los datos de una orden. Solo se pueden modificar ordenes
que no estan completadas o canceladas.


### Eliminar Orden

```
DELETE /api/ordenes/{id}/
```

Elimina una orden. Solo se pueden eliminar ordenes pendientes.


### Iniciar Orden

```
POST /api/ordenes/{id}/iniciar/
```

Cambia el estado de la orden de PENDIENTE a EN_PROGRESO.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Orden ORD-2026-0001 iniciada",
    "orden": {
        "id": 1,
        "numero_orden": "ORD-2026-0001",
        "estado": "EN_PROGRESO"
    }
}
```

**Error (400):**
```json
{
    "error": "Solo se pueden iniciar ordenes pendientes"
}
```


### Registrar Produccion en Orden

```
POST /api/ordenes/{id}/registrar_produccion/
```

Registra unidades producidas para una orden.

**Body de la peticion:**
```json
{
    "cantidad": 100
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Produccion registrada: 100 unidades",
    "cantidad_total_producida": 850,
    "cantidad_solicitada": 1000,
    "orden_completada": false,
    "orden": {
        "id": 1,
        "numero_orden": "ORD-2026-0001",
        "cantidad_producida": 850
    }
}
```

**Nota:** Si la orden estaba en estado PENDIENTE, automaticamente
cambiara a EN_PROGRESO.


### Completar Orden

```
POST /api/ordenes/{id}/completar/
```

Marca la orden como completada y la agrega a la cola de despacho.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Orden ORD-2026-0001 completada y agregada a cola de despacho",
    "posicion_cola": 3,
    "orden": {
        "id": 1,
        "numero_orden": "ORD-2026-0001",
        "estado": "COMPLETADA"
    }
}
```

**Errores posibles:**
- 400: La orden ya esta completada
- 400: No se puede completar una orden cancelada
- 400: La orden no tiene produccion registrada


### Cancelar Orden

```
POST /api/ordenes/{id}/cancelar/
```

Cancela una orden de produccion.

**Body de la peticion (opcional):**
```json
{
    "motivo": "Cliente cancelo el pedido"
}
```

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Orden ORD-2026-0001 cancelada",
    "orden": {
        "id": 1,
        "numero_orden": "ORD-2026-0001",
        "estado": "CANCELADA"
    }
}
```


### Listar Ordenes Pendientes

```
GET /api/ordenes/pendientes/
```

Retorna todas las ordenes con estado PENDIENTE ordenadas por
prioridad y fecha de entrega.

**Respuesta exitosa (200):**
```json
[
    {
        "id": 3,
        "numero_orden": "ORD-2026-0003",
        "producto": 2,
        "cantidad_solicitada": 500,
        "prioridad": 5,
        "fecha_entrega_estimada": "2026-03-10",
        "estado": "PENDIENTE"
    }
]
```


### Listar Ordenes en Progreso

```
GET /api/ordenes/en_progreso/
```

Retorna todas las ordenes que estan actualmente en produccion.


## Cola de Despacho

La cola de despacho organiza las ordenes completadas que estan
listas para ser entregadas al cliente.


### Listar Cola de Despacho

```
GET /api/cola-despacho/
```

Retorna todos los items en la cola de despacho ordenados por posicion.

**Parametros de consulta opcionales:**
- `despachado`: Filtrar por estado de despacho (true/false)

**Respuesta exitosa (200):**
```json
[
    {
        "id": 1,
        "orden": 1,
        "orden_numero": "ORD-2026-0001",
        "producto_nombre": "Botella PET 500ml",
        "cantidad": 1000,
        "posicion_cola": 1,
        "fecha_ingreso_cola": "2026-03-09T14:00:00Z",
        "despachado": false,
        "fecha_despacho": null
    },
    {
        "id": 2,
        "orden": 2,
        "orden_numero": "ORD-2026-0002",
        "producto_nombre": "Tapa Rosca 28mm",
        "cantidad": 5000,
        "posicion_cola": 2,
        "fecha_ingreso_cola": "2026-03-09T15:00:00Z",
        "despachado": false,
        "fecha_despacho": null
    }
]
```


### Obtener Detalle de Item

```
GET /api/cola-despacho/{id}/
```


### Despachar Item

```
POST /api/cola-despacho/{id}/despachar/
```

Marca un item como despachado y registra la fecha de despacho.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Orden ORD-2026-0001 despachada",
    "fecha_despacho": "2026-03-09T16:30:00Z",
    "item": {
        "id": 1,
        "orden_numero": "ORD-2026-0001",
        "despachado": true
    }
}
```

**Error (400):**
```json
{
    "error": "Este item ya fue despachado"
}
```


### Reordenar Cola

```
POST /api/cola-despacho/reordenar/
```

Reordena los items pendientes de despacho en la cola.

**Body de la peticion:**
```json
{
    "orden": [3, 1, 2]
}
```

Los IDs en el array representan el nuevo orden de la cola.

**Respuesta exitosa (200):**
```json
{
    "mensaje": "Cola reordenada exitosamente",
    "nuevo_orden": [3, 1, 2]
}
```

**Errores posibles:**
- 400: Se requiere una lista de IDs
- 400: Algunos IDs no son validos o ya fueron despachados


### Listar Pendientes de Despacho

```
GET /api/cola-despacho/pendientes/
```

Retorna los items que aun no han sido despachados.


## Estados de Orden

| Estado | Descripcion |
|--------|-------------|
| PENDIENTE | Orden creada, esperando inicio de produccion |
| EN_PROGRESO | Orden en produccion activa |
| COMPLETADA | Produccion finalizada, en cola de despacho |
| CANCELADA | Orden cancelada |


## Prioridades de Orden

| Nivel | Descripcion |
|-------|-------------|
| 1 | Baja - Puede esperar |
| 2 | Normal - Tiempo estandar |
| 3 | Media - Prioridad moderada |
| 4 | Alta - Requiere atencion |
| 5 | Urgente - Maxima prioridad |


## Flujo de Trabajo de Ordenes

```
1. CREAR ORDEN (estado: PENDIENTE)
   |
2. INICIAR ORDEN (estado: EN_PROGRESO)
   |
3. REGISTRAR PRODUCCION (actualiza cantidad_producida)
   |
4. COMPLETAR ORDEN (estado: COMPLETADA, agrega a cola)
   |
5. DESPACHAR (marca como despachado en cola)
```


## Calculo de Dias Restantes

El campo `dias_restantes` se calcula automaticamente:
- Valores positivos: dias que faltan para la fecha de entrega
- Cero: hoy es la fecha de entrega
- Valores negativos: dias de retraso


## Notas de Implementacion

1. Las ordenes generan numero automatico secuencial
2. Al completar una orden se crea automaticamente el item en cola
3. Los items despachados se mantienen en historico
4. La posicion en cola se asigna automaticamente al agregar
5. Solo supervisores y gerentes pueden cancelar ordenes
6. La prioridad afecta el orden sugerido de produccion
