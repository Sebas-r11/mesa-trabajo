"""
Script para poblar la base de datos de FLEX-OP con datos de prueba
"""
import os
import django
from datetime import date, time

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flexop.settings')
django.setup()

from usuarios.models import Empresa, User
from maquinas.models import TipoMaquina, UnidadEficiencia, Maquina
from operaciones.models import Turno, Habilidad, Operario


def main():
    print("Poblando base de datos de FLEX-OP...")
    
    # Crear Empresa
    print("\n1. Creando empresa...")
    empresa = Empresa.objects.create(
        nombre="ACME Industries",
        razon_social="ACME Industries S.A.C.",
        ruc="20123456789",
        direccion="Av. Industrial 123, Lima",
        telefono="+51 1 234 5678",
        email="contacto@acme.com",
        activa=True
    )
    print(f"   ✓ Empresa creada: {empresa.nombre}")
    
    # Crear Usuarios
    print("\n2. Creando usuarios...")
    admin = User.objects.create_superuser(
        username='admin',
        email='admin@flexop.com',
        password='admin123',
        first_name='Administrador',
        last_name='Sistema',
        rol='ADMIN',
        empresa=empresa
    )
    print(f"   ✓ Admin: {admin.username}")
    
    supervisor = User.objects.create_user(
        username='supervisor1',
        email='supervisor@acme.com',
        password='super123',
        first_name='Carlos',
        last_name='Mendoza',
        rol='SUPERVISOR',
        empresa=empresa
    )
    print(f"   ✓ Supervisor: {supervisor.get_full_name()}")
    
    gerente = User.objects.create_user(
        username='gerente1',
        email='gerente@acme.com',
        password='gerente123',
        first_name='María',
        last_name='García',
        rol='GERENTE',
        empresa=empresa
    )
    print(f"   ✓ Gerente: {gerente.get_full_name()}")
    
    operario1 = User.objects.create_user(
        username='operario1',
        email='operario1@acme.com',
        password='operario123',
        first_name='Juan',
        last_name='Pérez',
        rol='OPERARIO',
        empresa=empresa
    )
    print(f"   ✓ Operario: {operario1.get_full_name()}")
    
    operario2 = User.objects.create_user(
        username='operario2',
        email='operario2@acme.com',
        password='operario123',
        first_name='Ana',
        last_name='López',
        rol='OPERARIO',
        empresa=empresa
    )
    print(f"   ✓ Operario: {operario2.get_full_name()}")
    
    operario3 = User.objects.create_user(
        username='operario3',
        email='operario3@acme.com',
        password='operario123',
        first_name='Pedro',
        last_name='Ramírez',
        rol='OPERARIO',
        empresa=empresa
    )
    print(f"   ✓ Operario: {operario3.get_full_name()}")
    
    # Crear Turnos
    print("\n3. Creando turnos...")
    turno_manana = Turno.objects.create(
        nombre="Turno Mañana",
        hora_inicio=time(7, 0),
        hora_fin=time(15, 0),
        empresa=empresa,
        activo=True
    )
    print(f"   ✓ {turno_manana.nombre}")
    
    turno_tarde = Turno.objects.create(
        nombre="Turno Tarde",
        hora_inicio=time(15, 0),
        hora_fin=time(23, 0),
        empresa=empresa,
        activo=True
    )
    print(f"   ✓ {turno_tarde.nombre}")
    
    turno_noche = Turno.objects.create(
        nombre="Turno Noche",
        hora_inicio=time(23, 0),
        hora_fin=time(7, 0),
        empresa=empresa,
        activo=True
    )
    print(f"   ✓ {turno_noche.nombre}")
    
    # Crear Tipos de Máquina
    print("\n4. Creando tipos de máquina...")
    tipo_llenadora = TipoMaquina.objects.create(
        nombre="Llenadora",
        descripcion="Máquina para llenado de envases",
        empresa=empresa
    )
    print(f"   ✓ {tipo_llenadora.nombre}")
    
    tipo_etiquetadora = TipoMaquina.objects.create(
        nombre="Etiquetadora",
        descripcion="Máquina para aplicación de etiquetas",
        empresa=empresa
    )
    print(f"   ✓ {tipo_etiquetadora.nombre}")
    
    # Crear Unidades de Eficiencia
    print("\n5. Creando unidades de eficiencia...")
    unidad_uh = UnidadEficiencia.objects.create(
        nombre="Unidades por Hora",
        abreviatura="u/h",
        descripcion="Cantidad de unidades producidas por hora",
        empresa=empresa
    )
    print(f"   ✓ {unidad_uh.nombre}")
    
    # Crear Habilidades
    print("\n6. Creando habilidades...")
    hab_llenadora = Habilidad.objects.create(
        nombre="Operación de Llenadora",
        descripcion="Capacitado para operar máquinas llenadoras",
        empresa=empresa
    )
    hab_llenadora.tipos_maquina.add(tipo_llenadora)
    print(f"   ✓ {hab_llenadora.nombre}")
    
    hab_etiquetadora = Habilidad.objects.create(
        nombre="Operación de Etiquetadora",
        descripcion="Capacitado para operar máquinas etiquetadoras",
        empresa=empresa
    )
    hab_etiquetadora.tipos_maquina.add(tipo_etiquetadora)
    print(f"   ✓ {hab_etiquetadora.nombre}")
    
    hab_mantenimiento = Habilidad.objects.create(
        nombre="Mantenimiento Básico",
        descripcion="Conocimientos de mantenimiento preventivo",
        empresa=empresa
    )
    print(f"   ✓ {hab_mantenimiento.nombre}")
    
    # Crear Máquinas
    print("\n7. Creando máquinas...")
    maquina1 = Maquina.objects.create(
        codigo="LLE-001",
        nombre="Llenadora Principal",
        tipo=tipo_llenadora,
        empresa=empresa,
        marca="ACME",
        modelo="FL-3000",
        capacidad_teorica=300,
        unidad_capacidad=unidad_uh,
        estado_actual="DISPONIBLE"
    )
    print(f"   ✓ {maquina1.codigo} - {maquina1.nombre}")
    
    maquina2 = Maquina.objects.create(
        codigo="LLE-002",
        nombre="Llenadora Secundaria",
        tipo=tipo_llenadora,
        empresa=empresa,
        marca="ACME",
        modelo="FL-2500",
        capacidad_teorica=250,
        unidad_capacidad=unidad_uh,
        estado_actual="DISPONIBLE"
    )
    print(f"   ✓ {maquina2.codigo} - {maquina2.nombre}")
    
    maquina3 = Maquina.objects.create(
        codigo="ETQ-001",
        nombre="Etiquetadora Automática",
        tipo=tipo_etiquetadora,
        empresa=empresa,
        marca="LabelPro",
        modelo="LP-500",
        capacidad_teorica=500,
        unidad_capacidad=unidad_uh,
        estado_actual="DISPONIBLE"
    )
    print(f"   ✓ {maquina3.codigo} - {maquina3.nombre}")
    
    # Crear Operarios
    print("\n8. Creando operarios...")
    oper1 = Operario.objects.create(
        usuario=operario1,
        codigo_empleado="OP-001",
        fecha_contratacion=date(2023, 1, 15),
        turno_actual=turno_manana,
        disponible=True,
        activo=True
    )
    oper1.habilidades.add(hab_llenadora, hab_mantenimiento)
    print(f"   ✓ {oper1.codigo_empleado} - {oper1.usuario.get_full_name()}")
    
    oper2 = Operario.objects.create(
        usuario=operario2,
        codigo_empleado="OP-002",
        fecha_contratacion=date(2023, 3, 10),
        turno_actual=turno_tarde,
        disponible=True,
        activo=True
    )
    oper2.habilidades.add(hab_etiquetadora)
    print(f"   ✓ {oper2.codigo_empleado} - {oper2.usuario.get_full_name()}")
    
    oper3 = Operario.objects.create(
        usuario=operario3,
        codigo_empleado="OP-003",
        fecha_contratacion=date(2023, 5, 20),
        turno_actual=turno_manana,
        disponible=True,
        activo=True
    )
    oper3.habilidades.add(hab_llenadora, hab_etiquetadora, hab_mantenimiento)
    print(f"   ✓ {oper3.codigo_empleado} - {oper3.usuario.get_full_name()}")
    
    print("\n" + "="*50)
    print("✓ Base de datos poblada exitosamente!")
    print("="*50)
    print("\nCredenciales de acceso:")
    print("  Admin:      admin / admin123")
    print("  Supervisor: supervisor1 / super123")
    print("  Gerente:    gerente1 / gerente123")
    print("  Operario 1: operario1 / operario123")
    print("  Operario 2: operario2 / operario123")
    print("  Operario 3: operario3 / operario123")


if __name__ == '__main__':
    main()
