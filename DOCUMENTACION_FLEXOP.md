# FLEX-OP - Documentación General

**Fecha de actualización:** 9 de abril de 2026

---

## 1. Plan de Desarrollo (Resumen)

**FLEX-OP** es una plataforma modular para la gestión de operaciones industriales. El desarrollo se organizó en fases:

- **Fase 1:** Configuración inicial, modelos base, autenticación JWT, admin y migraciones.
- **Fase 2:** Módulo de configuración (máquinas, operarios, habilidades, unidades de medida, validaciones).
- **Fase 3:** Operaciones y asignaciones (asignar operarios a máquinas, registrar eventos, incidencias).
- **Fase 4:** Métricas y producción (registros de producción, cálculo de eficiencia, objetivos).
- **Fase 5:** Alertas y notificaciones (reglas automáticas, alertas, notificaciones a usuarios).
- **Fase 6:** Sugerencias inteligentes de reasignación (propuestas automáticas para mejorar eficiencia).
- **Fase 7:** Reportes y dashboards (por rol, exportación CSV, historial de reportes).
- **Fase 8:** Gestión de órdenes de producción y cola de despacho.
- **Fase 9+:** Mejoras, integración IoT, optimización y soporte multitenancy.

---

## 2. Endpoints Principales por Módulo

### Usuarios y Autenticación
- `POST /api/auth/login/` - Login JWT
- `POST /api/auth/refresh/` - Refrescar token
- `GET /api/usuarios/` - Listar usuarios
- `GET /api/empresas/` - Listar empresas

### Máquinas y Productos
- `GET /api/maquinas/` - Listar máquinas
- `POST /api/maquinas/` - Crear máquina
- `GET /api/productos/` - Listar productos

### Operaciones
- `GET /api/turnos/` - Listar turnos
- `GET /api/operarios/` - Listar operarios
- `GET /api/asignaciones/` - Listar asignaciones
- `POST /api/asignaciones/{id}/iniciar/` - Iniciar asignación
- `POST /api/asignaciones/{id}/finalizar/` - Finalizar asignación
- `GET /api/incidencias/` - Listar incidencias
- `POST /api/incidencias/{id}/resolver/` - Resolver incidencia

### Métricas y Producción
- `GET /api/produccion/` - Listar registros de producción
- `POST /api/produccion/` - Registrar producción
- `GET /api/metricas/` - Listar métricas de eficiencia
- `GET /api/objetivos/` - Listar objetivos de producción

### Alertas y Notificaciones
- `GET /api/reglas-alerta/` - Listar reglas de alerta
- `POST /api/reglas-alerta/` - Crear regla de alerta
- `GET /api/alertas/` - Listar alertas
- `POST /api/alertas/{id}/resolver/` - Resolver alerta
- `GET /api/notificaciones/` - Listar notificaciones

### Reasignaciones
- `GET /api/sugerencias/` - Listar sugerencias de reasignación
- `POST /api/sugerencias/{id}/aceptar/` - Aceptar sugerencia
- `POST /api/sugerencias/{id}/rechazar/` - Rechazar sugerencia

### Reportes y Dashboards
- `GET /api/dashboard/operario/` - Dashboard de operario
- `GET /api/dashboard/supervisor/` - Dashboard de supervisor
- `GET /api/dashboard/gerente/` - Dashboard de gerente
- `GET /api/reportes/exportar-csv/` - Exportar datos a CSV
- `GET /api/reportes-generados/` - Historial de reportes

### Órdenes de Producción
- `GET /api/ordenes/` - Listar órdenes
- `POST /api/ordenes/` - Crear orden
- `POST /api/ordenes/{id}/iniciar/` - Iniciar orden
- `POST /api/ordenes/{id}/registrar_produccion/` - Registrar producción en orden
- `POST /api/ordenes/{id}/completar/` - Completar orden
- `GET /api/cola-despacho/` - Cola de despacho

---

## 3. Ejemplo de Uso de Endpoints

**Login y uso de token:**
```http
POST /api/auth/login/
{
  "username": "usuario@empresa.com",
  "password": "contraseña123"
}
// Respuesta: { "access": "...", "refresh": "..." }
```
Luego, en cada petición:
```
Authorization: Bearer <access_token>
```

**Registrar producción:**
```http
POST /api/produccion/
{
  "asignacion": 1,
  "cantidad": 150,
  "observaciones": "Producción normal"
}
```

**Obtener dashboard de supervisor:**
```http
GET /api/dashboard/supervisor/
// Respuesta: { "maquinas_estado": [...], "alertas_activas": 3, ... }
```

---

## 4. Historias de Usuario Principales

## Historias de Usuario Principales con Rut Map y Requisitos

### 1. Como **operario**, quiero ver mi asignación actual y registrar mi producción diaria, para llevar un control de mi trabajo y cumplir mis objetivos.
**Requisitos:**
- Estar logueado como operario
- Tener una asignación activa

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Consultar asignación actual (`GET /api/dashboard/operario/`)
3. Registrar producción (`POST /api/produccion/`)

---

### 2. Como **supervisor**, quiero ver el estado de todas las máquinas y operarios en mi turno, recibir alertas y reasignar recursos rápidamente, para mantener la eficiencia y evitar paradas.
**Requisitos:**
- Estar logueado como supervisor

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Consultar dashboard de supervisor (`GET /api/dashboard/supervisor/`)
3. Ver alertas (`GET /api/alertas/`)
4. Reasignar recursos (aceptar/rechazar sugerencias: `POST /api/sugerencias/{id}/aceptar/` o `/rechazar/`)

---

### 3. Como **gerente**, quiero acceder a dashboards con KPIs, tendencias y reportes históricos, para tomar decisiones estratégicas y mejorar la productividad de la planta.
**Requisitos:**
- Estar logueado como gerente

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Consultar dashboard de gerente (`GET /api/dashboard/gerente/`)
3. Descargar reportes (`GET /api/reportes/exportar-csv/`)

---

### 4. Como **usuario**, quiero recibir notificaciones automáticas cuando haya incidencias, alertas críticas o cambios en mis asignaciones, para estar siempre informado y reaccionar a tiempo.
**Requisitos:**
- Estar logueado

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Consultar notificaciones (`GET /api/notificaciones/`)
3. Marcar como leídas (`POST /api/notificaciones/{id}/marcar_leida/`)

---

### 5. Como **supervisor**, quiero aceptar o rechazar sugerencias inteligentes de reasignación de operarios, para optimizar la producción según el análisis del sistema.
**Requisitos:**
- Estar logueado como supervisor

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Ver sugerencias (`GET /api/sugerencias/`)
3. Aceptar (`POST /api/sugerencias/{id}/aceptar/`) o rechazar (`POST /api/sugerencias/{id}/rechazar/`)

---

### 6. Como **administrador**, quiero gestionar empresas, usuarios y permisos desde un panel centralizado, para mantener la seguridad y la organización del sistema.
**Requisitos:**
- Estar logueado como administrador

**Rut Map:**
1. Login (`POST /api/auth/login/`)
2. Gestionar empresas (`GET/POST/PUT/DELETE /api/empresas/`)
3. Gestionar usuarios (`GET/POST/PUT/DELETE /api/usuarios/`)
4. Asignar roles y permisos (en la creación/edición de usuarios)

---

## 5. Referencias y Navegación

- Documentación completa de endpoints en cada módulo: `usuarios/ENDPOINTS.md`, `maquinas/ENDPOINTS.md`, etc.
- Diagrama de fases y modelos: ver `PLAN_DESARROLLO.md` y `MODELOS_DJANGO.md`
- Para pruebas y exploración de la API: `/swagger/` y `/redoc/` en el servidor local.

---
