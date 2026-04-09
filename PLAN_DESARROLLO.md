# FLEX-OP - Plan de Desarrollo por Fases
## Proyecto Educativo con Django + Python

---

## Enfoque del Proyecto
- **Backend**: Django + Django REST Framework
- **Autenticación**: JWT (Simple JWT)
- **Base de datos**: PostgreSQL (o SQLite para desarrollo)
- **Frontend**: HTML/CSS/JS simple con Bootstrap (sin React para simplificar)
- **Tiempo real**: Polling AJAX simple (sin WebSockets)
- **IoT**: Funcionalidad preparada pero no implementada (marcada como "próximamente")

---

## FASE 1: Configuración Inicial y Modelos Base (Semana 1-2)

### Objetivo
Crear la estructura base del proyecto con modelos fundamentales y sistema de autenticación.

### Tareas
1. **Configuración del Proyecto Django**
   - Crear proyecto Django `flexop`
   - Crear app principal `core`
   - Configurar Django REST Framework
   - Configurar Simple JWT para autenticación
   - Configurar PostgreSQL/SQLite
   - Configurar variables de entorno (.env)

2. **Modelos Base**
   - Modelo Usuario extendido con roles (Operario, Supervisor, Gerente, Admin)
   - Modelo Empresa (cliente único pero preparado para multitenancy futuro)
   - Modelo Máquina
   - Modelo Operario (perfil extendido de Usuario)
   - Modelo Habilidad
   - Modelo Turno

3. **Sistema de Autenticación**
   - Login/Logout con JWT
   - Permisos por rol
   - Endpoints básicos de autenticación

4. **Admin de Django**
   - Configurar admin para todos los modelos
   - Personalizar vistas de admin

### Entregables
- Proyecto Django funcionando
- Modelos creados y migrados
- Sistema de autenticación JWT funcional
- Admin de Django configurado

---

## FASE 2: Módulo de Configuración (Semana 3-4)

### Objetivo
Permitir configurar máquinas, operarios, habilidades y unidades de medida.

### Tareas
1. **Modelos de Configuración**
   - Modelo UnidadEficiencia (ej: hectáreas/hora, unidades/hora)
   - Modelo TipoMaquina (categorías de máquinas)
   - Modelo ConfiguracionEficiencia (fórmulas personalizables)
   - Relaciones Máquina-Operario-Habilidad

2. **Serializers y Endpoints**
   - CRUD de Máquinas
   - CRUD de Operarios
   - CRUD de Habilidades
   - CRUD de Unidades de Eficiencia
   - Asignación de habilidades a operarios

3. **Interfaz Web Básica**
   - Dashboard de administración simple
   - Formularios para gestión de máquinas
   - Formularios para gestión de operarios
   - Vista de habilidades por operario

4. **Validaciones**
   - Validar que operario tenga habilidad para máquina
   - Validar disponibilidad de máquinas
   - Validar turnos

### Entregables
- API REST completa de configuración
- Interfaz web básica funcional
- Validaciones implementadas
- Documentación de API (Swagger/OpenAPI)

---

## FASE 3: Módulo de Operaciones y Asignaciones (Semana 5-6)

### Objetivo
Registrar asignaciones de operarios a máquinas y capturar eventos operativos.

### Tareas
1. **Modelos Operacionales**
   - Modelo Asignación (operario → máquina → turno)
   - Modelo Evento (inicio/fin de tarea, pausa, incidencia)
   - Modelo Incidencia (fallas, falta de material, etc.)
   - Modelo EstadoMaquina (operando, parada, mantenimiento)

2. **Lógica de Negocio**
   - Sistema de inicio/fin de tareas
   - Cambio de estado de máquinas
   - Registro de incidencias
   - Validación de asignaciones (no duplicar operarios)

3. **Endpoints API**
   - POST /asignaciones/ (asignar operario a máquina)
   - POST /eventos/ (iniciar/finalizar tarea)
   - POST /incidencias/ (reportar problemas)
   - GET /asignaciones/activas/ (ver asignaciones actuales)

4. **Interfaz para Operarios**
   - Vista simple para iniciar/finalizar tarea
   - Botón para reportar incidencias
   - Ver máquina asignada y tarea actual

### Entregables
- Sistema de asignaciones funcional
- Registro de eventos operativos
- Interfaz simple para operarios
- Validaciones de negocio

   - Login/Logout con JWT
   - Permisos por rol
   - Endpoints básicos de autenticación

4. **Admin de Django**
   - Configurar admin para todos los modelos
   - Personalizar vistas de admin

---

## FASE 4: Cálculo de Eficiencia (Semana 7-8)

### Objetivo
Calcular métricas de eficiencia en tiempo real basadas en eventos registrados.

### Tareas
1. **Modelos de Métricas**
   - Modelo RegistroProduccion (contador de unidades/hectáreas producidas)
   - Modelo MetricaEficiencia (almacena cálculos de eficiencia)
   - Modelo ObjetivoProduccion (metas por máquina/operario)

2. **Motor de Cálculo**
   - Servicio Python para calcular eficiencia
   - Fórmulas configurables: `Eficiencia = (Real / Teórico) × 100`
   - Cálculo por operario, por máquina, por turno
   - Almacenar históricos

3. **Endpoints de Métricas**
   - GET /metricas/operario/{id}/ (eficiencia personal)
   - GET /metricas/maquina/{id}/ (eficiencia por máquina)
   - GET /metricas/turno/{id}/ (eficiencia por turno)
   - POST /produccion/ (registrar producción manual)

4. **Automatización**
   - Tarea periódica (Celery o Cron) para calcular métricas
   - Trigger al finalizar tarea para calcular eficiencia

### Entregables
- Motor de cálculo de eficiencia funcional
- API de métricas
- Históricos de eficiencia almacenados
- Cálculos automatizados

---

## FASE 5: Sistema de Alertas y Reglas (Semana 9-10)

### Objetivo
Implementar motor de reglas simple para generar alertas automáticas.

### Tareas
1. **Modelos de Alertas**
   - Modelo ReglaAlerta (condiciones y acciones)
   - Modelo Alerta (alertas generadas)
   - Modelo Notificacion (log de notificaciones enviadas)

2. **Motor de Reglas Simple**
   - Evaluar reglas cada X minutos (tarea periódica)
   - Reglas básicas:
     - `Si eficiencia < umbral por X minutos → Alerta`
     - `Si máquina parada > X minutos → Alerta`
     - `Si incidencia no resuelta > X minutos → Escalar`
   - Sistema de prioridades (baja, media, alta, crítica)

3. **Sistema de Notificaciones**
   - Notificaciones en la plataforma (campana de alertas)
   - Email simple (opcional: usar Django mail)
   - Log de notificaciones enviadas

4. **Endpoints de Alertas**
   - GET /alertas/ (listar alertas activas)
   - POST /alertas/{id}/resolver/ (marcar como resuelta)
   - GET /alertas/estadisticas/ (alertas por tipo)

5. **Interfaz de Supervisor**
   - Panel de alertas en tiempo real
   - Botón para resolver alertas
   - Filtros por prioridad

### Entregables
- Motor de reglas funcional
- Sistema de alertas automáticas
- Notificaciones básicas
- Panel de alertas para supervisores

---

## FASE 6: Sugerencias de Reasignación (Semana 11-12)

### Objetivo
Sistema inteligente que sugiere reasignar operarios cuando hay problemas.

### Tareas
1. **Modelo de Sugerencias**
   - Modelo SugerenciaReasignacion (operario origen, máquina destino, razón)
   - Estado: pendiente, aceptada, rechazada

2. **Lógica de Reasignación**
   - Detectar: máquina parada + operario ocioso con habilidad
   - Detectar: máquina bajo rendimiento + operario disponible más eficiente
   - Generar sugerencias automáticas
   - Priorizar por impacto en producción

3. **Endpoints**
   - GET /sugerencias/ (listar sugerencias pendientes)
   - POST /sugerencias/{id}/aceptar/ (aplicar reasignación)
   - POST /sugerencias/{id}/rechazar/ (descartar sugerencia)

4. **Interfaz para Supervisor**
   - Panel de sugerencias
   - Botón "Aceptar" que reasigna automáticamente
   - Historial de sugerencias aceptadas/rechazadas

### Entregables
- Sistema de sugerencias automáticas
- Lógica de reasignación inteligente
- Interfaz para gestionar sugerencias
- Historial de decisiones

---

## FASE 7: Dashboards y Reportes (Semana 13-14)

### Objetivo
Crear visualizaciones claras para cada rol con métricas clave.

### Tareas
1. **Dashboard Operario**
   - Máquina actual asignada
   - Eficiencia personal del día
   - Objetivo vs. real
   - Tareas completadas

2. **Dashboard Supervisor**
   - Mapa de ocupación de máquinas (colores: verde=ok, amarillo=bajo, rojo=parada)
   - Lista de alertas activas
   - Sugerencias de reasignación pendientes
   - Eficiencia promedio del turno
   - Ranking de operarios del turno

3. **Dashboard Gerente**
   - KPIs globales (eficiencia general, OEE aproximado, cumplimiento)
   - Gráficas de tendencias (últimos 7 días)
   - Comparativa por turnos
   - Ranking de operarios (top 10 y bottom 5)
   - Ranking de máquinas
   - Estadísticas de incidencias

4. **Reportes Descargables**
   - Reporte diario en PDF (usando ReportLab o WeasyPrint)
   - Reporte semanal por operario
   - Reporte de incidencias
   - Exportar a Excel (CSV)

5. **Gráficas con Chart.js**
   - Gráfica de barras: eficiencia por operario
   - Gráfica de línea: tendencia de eficiencia
   - Gráfica de pastel: distribución de incidencias

### Entregables
- Dashboard operario funcional
- Dashboard supervisor con alertas y sugerencias
- Dashboard gerente con KPIs y gráficas
- Reportes descargables (PDF/Excel)

---

## FASE 8: Módulo de Cola de Despacho (Semana 15-16)

### Objetivo
Gestionar órdenes de producción y priorizar despachos.

### Tareas
1. **Modelos de Órdenes**
   - Modelo OrdenProduccion (producto, cantidad, fecha límite)
   - Modelo EstadoOrden (pendiente, en proceso, lista, despachada)
   - Modelo ColaDespacho (ordena órdenes listas)

2. **Lógica de Cola**
   - Al marcar orden como "lista", entra en cola
   - Priorización automática (fecha límite, prioridad)
   - Alertas si orden lleva mucho tiempo en cola

3. **Endpoints**
   - GET /ordenes/ (listar órdenes)
   - POST /ordenes/ (crear orden)
   - PUT /ordenes/{id}/estado/ (cambiar estado)
   - GET /cola-despacho/ (próxima orden a despachar)
   - POST /cola-despacho/despachar/ (marcar como despachada)

4. **Interfaz de Logística**
   - Vista simple: próxima orden a despachar
   - Botón "Despachar" que saca de la cola
   - Historial de despachos

### Entregables
- Sistema de órdenes de producción
- Cola de despacho priorizada
- Alertas de órdenes retrasadas
- Interfaz de logística

---

## FASE 9: Pruebas y Optimización (Semana 17-18)

### Objetivo
Validar funcionalidades, optimizar rendimiento y corregir bugs.

### Tareas
1. **Pruebas Unitarias**
   - Tests de modelos (validaciones)
   - Tests de serializers
   - Tests de endpoints (Django TestCase)
   - Cobertura mínima del 70%

2. **Pruebas de Integración**
   - Flujo completo: asignar → iniciar tarea → registrar producción → calcular eficiencia
   - Flujo de alertas: condición → alerta → notificación
   - Flujo de reasignación: sugerencia → aceptar → aplicar

3. **Pruebas de Usuario (UAT)**
   - Pruebas con roles reales (operario, supervisor, gerente)
   - Validar usabilidad de interfaces
   - Recoger feedback

4. **Optimización**
   - Indexar campos clave en DB (foreign keys, fechas)
   - Optimizar queries (select_related, prefetch_related)
   - Cachear métricas frecuentes (Redis opcional)
   - Paginación en listados grandes

5. **Documentación**
   - README con instrucciones de instalación
   - Documentación de API (Swagger automático)
   - Manual de usuario básico
   - Guía de despliegue

### Entregables
- Suite de pruebas funcional
- Cobertura de tests >70%
- Performance optimizada
- Documentación completa

---

## FASE 10: Despliegue y Preparación IoT (Semana 19-20)

### Objetivo
Desplegar el sistema en producción y preparar arquitectura para IoT futuro.

### Tareas
1. **Preparación para Despliegue**
   - Configurar settings.py para producción
   - Configurar variables de entorno
   - Configurar archivos estáticos (collectstatic)
   - Configurar Gunicorn + Nginx
   - Configurar PostgreSQL en producción

2. **Despliegue**
   - Desplegar en servidor (DigitalOcean, AWS, Heroku)
   - Configurar dominio y SSL (Let's Encrypt)
   - Configurar backups automáticos de DB

3. **Preparar Infraestructura IoT (sin implementar)**
   - Modelo SensorIoT (preparado para futuro)
   - Endpoint placeholder para recibir datos MQTT
   - Documentación de cómo se integrará IoT
   - Vista de "Próximamente" en dashboard

4. **Monitoreo Básico**
   - Logs configurados (Django logging)
   - Monitoreo de errores (Sentry opcional)
   - Script de backup de DB

### Entregables
- Sistema desplegado en producción
- SSL y dominio configurado
- Infraestructura IoT preparada (sin implementar)
- Sistema de monitoreo básico

---

## Funcionalidades Finales del MVP

Al completar estas 10 fases, tendremos:

### Funcionalidades Core
1. **Autenticación JWT** con roles (Operario, Supervisor, Gerente, Admin)
2. **Gestión de Máquinas y Operarios** con habilidades
3. **Asignación operario-máquina** con validaciones
4. **Registro de tareas** (inicio/fin) y eventos
5. **Cálculo de eficiencia** en tiempo real
6. **Sistema de alertas automáticas** con reglas configurables
7. **Sugerencias inteligentes de reasignación**
8. **Dashboards por rol** con métricas clave
9. **Reportes descargables** (PDF/Excel)
10. **Cola de despacho** para órdenes de producción

### Preparado para el Futuro
- Arquitectura lista para multitenancy
- Modelos preparados para integración IoT/MQTT
- API REST documentada para integraciones
- Base escalable para ML futuro

---

## Cronograma Visual

```
Semanas 1-2:   [████████] Configuración + Modelos Base + Auth
Semanas 3-4:   [████████] Módulo Configuración
Semanas 5-6:   [████████] Operaciones y Asignaciones
Semanas 7-8:   [████████] Cálculo de Eficiencia
Semanas 9-10:  [████████] Alertas y Reglas
Semanas 11-12: [████████] Reasignación Inteligente
Semanas 13-14: [████████] Dashboards y Reportes
Semanas 15-16: [████████] Cola de Despacho
Semanas 17-18: [████████] Pruebas y Optimización
Semanas 19-20: [████████] Despliegue y Prep IoT
```

**Duración Total: 20 semanas (5 meses)**

---

## Stack Tecnológico Final

### Backend
- **Python 3.10+**
- **Django 4.2+**
- **Django REST Framework**
- **Simple JWT** (autenticación)
- **Celery** (tareas periódicas - opcional, puede usar Cron)
- **PostgreSQL** (producción) / SQLite (desarrollo)

### Frontend
- **HTML5 + CSS3 + JavaScript**
- **Bootstrap 5** (diseño responsivo)
- **Chart.js** (gráficas)
- **Fetch API** (llamadas AJAX)

### Herramientas
- **Git** (control de versiones)
- **Docker** (opcional para despliegue)
- **Postman** (testing de API)
- **Swagger/OpenAPI** (documentación)

### Futuro (no en MVP)
- **Redis** (caché)
- **Mosquitto MQTT** (IoT)
- **React** (migración de frontend)
- **TensorFlow** (ML predictivo)

---

## Notas Importantes

### Simplificaciones Educativas
1. **Sin WebSockets**: Usaremos polling AJAX simple cada 10-30 segundos
2. **Sin IoT real**: Modelos preparados pero no implementados
3. **Un solo cliente**: No multitenancy activo (pero preparado en modelos)
4. **Reglas simples**: Evaluación básica con Python, no motor complejo
5. **Frontend simple**: HTML/Bootstrap, sin SPA complejo

### Buenas Prácticas Incluidas
- Separación de concerns (models, views, serializers, services)
- Validaciones en múltiples capas
- Logging apropiado
- Manejo de errores robusto
- Documentación de código
- Tests unitarios y de integración
- API RESTful bien diseñada
- Seguridad básica (JWT, permisos, validación de input)

---

## Próximos Pasos

1. Revisar este plan y ajustar si es necesario
2. Crear los modelos de Django (siguiente documento)
3. Configurar proyecto Django inicial
4. Implementar Fase 1

---

**Fecha de creación**: 5 de marzo de 2026  
**Proyecto**: FLEX-OP (Flexible Operations Platform)  
**Versión**: 1.0 - Plan Educativo
