"""
Script para poblar la base de datos con datos de prueba
Ejecutar: python manage.py shell < populate_db.py
"""

from django.utils import timezone
from datetime import date, time
from core.models import (
    Empresa, User, TipoMaquina, Maquina, Habilidad,
    UnidadEficiencia, Turno, Operario
)

print("🚀 Iniciando población de base de datos...")

# Crear empresa
empresa, created = Empresa.objects.get_or_create(
    nombre="ACME Industries",
    defaults={
        'razon_social': 'ACME Industries S.A.C.',
        'ruc': '20123456789',
        'direccion': 'Av. Principal 123, Lima',
        'telefono': '01-234-5678',
        'email': 'contacto@acme.com',
        'activa': True
    }
)
print(f"✓ Empresa creada: {empresa.nombre}")

# Crear usuarios
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@flexop.com',
        'first_name': 'Administrador',
        'last_name': 'Sistema',
        'rol': User.RolChoices.ADMIN,
        'empresa': empresa,
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
print(f"✓ Usuario admin creado (password: admin123)")

supervisor, created = User.objects.get_or_create(
    username='supervisor1',
    defaults={
        'email': 'supervisor@acme.com',
        'first_name': 'Carlos',
        'last_name': 'Mendoza',
        'rol': User.RolChoices.SUPERVISOR,
        'empresa': empresa,
    }
)
if created:
    supervisor.set_password('super123')
    supervisor.save()
print(f"✓ Supervisor creado: {supervisor.get_full_name()}")

gerente, created = User.objects.get_or_create(
    username='gerente1',
    defaults={
        'email': 'gerente@acme.com',
        'first_name': 'María',
        'last_name': 'García',
        'rol': User.RolChoices.GERENTE,
        'empresa': empresa,
    }
)
if created:
    gerente.set_password('gerente123')
    gerente.save()
print(f"✓ Gerente creado: {gerente.get_full_name()}")

# Crear operarios
operarios_data = [
    {'username': 'operario1', 'first_name': 'Juan', 'last_name': 'Pérez', 'codigo': 'OP-001'},
    {'username': 'operario2', 'first_name': 'Ana', 'last_name': 'López', 'codigo': 'OP-002'},
    {'username': 'operario3', 'first_name': 'Pedro', 'last_name': 'Ramírez', 'codigo': 'OP-003'},
]

usuarios_operarios = []
for op_data in operarios_data:
    user, created = User.objects.get_or_create(
        username=op_data['username'],
        defaults={
            'email': f"{op_data['username']}@acme.com",
            'first_name': op_data['first_name'],
            'last_name': op_data['last_name'],
            'rol': User.RolChoices.OPERARIO,
            'empresa': empresa,
        }
    )
    if created:
        user.set_password('operario123')
        user.save()
    usuarios_operarios.append((user, op_data['codigo']))
    print(f"✓ Operario creado: {user.get_full_name()}")

# Crear unidades de eficiencia
unidades_data = [
    {'nombre': 'Unidades por hora', 'abreviatura': 'u/h'},
    {'nombre': 'Hectáreas por hora', 'abreviatura': 'ha/h'},
    {'nombre': 'Kilogramos por hora', 'abreviatura': 'kg/h'},
]

unidades = []
for u_data in unidades_data:
    unidad, created = UnidadEficiencia.objects.get_or_create(
        nombre=u_data['nombre'],
        empresa=empresa,
        defaults={'abreviatura': u_data['abreviatura']}
    )
    unidades.append(unidad)
    if created:
        print(f"✓ Unidad creada: {unidad}")

# Crear turnos
turnos_data = [
    {'nombre': 'Mañana', 'hora_inicio': time(7, 0), 'hora_fin': time(15, 0)},
    {'nombre': 'Tarde', 'hora_inicio': time(15, 0), 'hora_fin': time(23, 0)},
    {'nombre': 'Noche', 'hora_inicio': time(23, 0), 'hora_fin': time(7, 0)},
]

turnos = []
for t_data in turnos_data:
    turno, created = Turno.objects.get_or_create(
        nombre=t_data['nombre'],
        empresa=empresa,
        defaults={
            'hora_inicio': t_data['hora_inicio'],
            'hora_fin': t_data['hora_fin']
        }
    )
    turnos.append(turno)
    if created:
        print(f"✓ Turno creado: {turno}")

# Crear tipos de máquina
tipos_maquina_data = [
    {'nombre': 'Llenadora', 'descripcion': 'Máquina llenadora de líquidos'},
    {'nombre': 'Etiquetadora', 'descripcion': 'Máquina etiquetadora automática'},
    {'nombre': 'Empacadora', 'descripcion': 'Máquina empacadora al vacío'},
]

tipos_maquina = []
for tm_data in tipos_maquina_data:
    tipo, created = TipoMaquina.objects.get_or_create(
        nombre=tm_data['nombre'],
        defaults={
            'descripcion': tm_data['descripcion'],
            'empresa': empresa
        }
    )
    tipos_maquina.append(tipo)
    if created:
        print(f"✓ Tipo de máquina creado: {tipo}")

# Crear habilidades
habilidades_data = [
    {'nombre': 'Operación de Llenadora', 'descripcion': 'Capacidad para operar máquinas llenadoras'},
    {'nombre': 'Operación de Etiquetadora', 'descripcion': 'Capacidad para operar etiquetadoras'},
    {'nombre': 'Mantenimiento Básico', 'descripcion': 'Mantenimiento preventivo básico'},
]

habilidades = []
for h_data in habilidades_data:
    habilidad, created = Habilidad.objects.get_or_create(
        nombre=h_data['nombre'],
        empresa=empresa,
        defaults={'descripcion': h_data['descripcion']}
    )
    habilidades.append(habilidad)
    if created:
        print(f"✓ Habilidad creada: {habilidad}")

# Asociar habilidades con tipos de máquina
if tipos_maquina and habilidades:
    habilidades[0].tipos_maquina.add(tipos_maquina[0])  # Llenadora
    habilidades[1].tipos_maquina.add(tipos_maquina[1])  # Etiquetadora

# Crear máquinas
maquinas_data = [
    {
        'codigo': 'LLE-001',
        'nombre': 'Llenadora Principal',
        'tipo': tipos_maquina[0],
        'marca': 'FillMaster',
        'modelo': 'FM-3000',
        'capacidad': 300,
        'unidad': unidades[0]
    },
    {
        'codigo': 'LLE-002',
        'nombre': 'Llenadora Secundaria',
        'tipo': tipos_maquina[0],
        'marca': 'FillMaster',
        'modelo': 'FM-2500',
        'capacidad': 250,
        'unidad': unidades[0]
    },
    {
        'codigo': 'ETQ-001',
        'nombre': 'Etiquetadora Automática',
        'tipo': tipos_maquina[1],
        'marca': 'LabelPro',
        'modelo': 'LP-500',
        'capacidad': 500,
        'unidad': unidades[0]
    },
]

maquinas = []
for m_data in maquinas_data:
    maquina, created = Maquina.objects.get_or_create(
        codigo=m_data['codigo'],
        defaults={
            'nombre': m_data['nombre'],
            'tipo': m_data['tipo'],
            'empresa': empresa,
            'marca': m_data['marca'],
            'modelo': m_data['modelo'],
            'capacidad_teorica': m_data['capacidad'],
            'unidad_capacidad': m_data['unidad'],
            'estado_actual': Maquina.EstadoChoices.DISPONIBLE
        }
    )
    maquinas.append(maquina)
    if created:
        print(f"✓ Máquina creada: {maquina}")

# Crear perfiles de operarios
for user, codigo in usuarios_operarios:
    operario, created = Operario.objects.get_or_create(
        codigo_empleado=codigo,
        defaults={
            'usuario': user,
            'fecha_contratacion': date(2024, 1, 15),
            'turno_actual': turnos[0],  # Turno mañana
            'disponible': True,
            'activo': True
        }
    )
    if created:
        # Asignar habilidades aleatorias
        if codigo == 'OP-001':
            operario.habilidades.add(habilidades[0], habilidades[2])  # Llenadora y mantenimiento
        elif codigo == 'OP-002':
            operario.habilidades.add(habilidades[1])  # Etiquetadora
        elif codigo == 'OP-003':
            operario.habilidades.add(habilidades[0], habilidades[1])  # Ambas máquinas
        
        print(f"✓ Perfil de operario creado: {operario}")

print("\n✅ Base de datos poblada exitosamente!")
print("\n📋 Credenciales de acceso:")
print("━" * 50)
print("👤 Admin:      username: admin       password: admin123")
print("👤 Supervisor: username: supervisor1 password: super123")
print("👤 Gerente:    username: gerente1    password: gerente123")
print("👤 Operarios:  username: operario1-3 password: operario123")
print("━" * 50)
