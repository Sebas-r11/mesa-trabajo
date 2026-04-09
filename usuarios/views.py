"""
ViewSets para autenticación en FLEX-OP
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import update_session_auth_hash

from .models import User, Empresa
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    EmpresaSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de usuarios y acciones como ver perfil, cambiar contraseña, listar operarios y supervisores
    """ViewSet para gestionar usuarios"""
    
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_permissions(self):
        """Permisos personalizados por acción"""
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener información del usuario actual"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Cambiar contraseña de usuario"""
        user = self.get_object()
        
        # Solo el usuario puede cambiar su propia contraseña o un admin
        if user != request.user and not request.user.es_admin:
            return Response(
                {'error': 'No tienes permiso para cambiar la contraseña de este usuario.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Verificar contraseña actual
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {'old_password': 'Contraseña actual incorrecta.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Establecer nueva contraseña
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            # Mantener la sesión activa después del cambio
            update_session_auth_hash(request, user)
            
            return Response({'message': 'Contraseña actualizada exitosamente.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def operarios(self, request):
        """Listar solo usuarios con rol operario"""
        operarios = self.queryset.filter(rol=User.RolChoices.OPERARIO)
        serializer = self.get_serializer(operarios, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def supervisores(self, request):
        """Listar solo usuarios con rol supervisor"""
        supervisores = self.queryset.filter(rol=User.RolChoices.SUPERVISOR)
        serializer = self.get_serializer(supervisores, many=True)
        return Response(serializer.data)


class EmpresaViewSet(viewsets.ModelViewSet):
    # Gestiona el CRUD de empresas (alta, baja, modificación, listado)
    """ViewSet para gestionar empresas"""
    
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    
    filterset_fields = ['activa']
    search_fields = ['nombre', 'ruc', 'razon_social']
    ordering_fields = ['nombre', 'fecha_creacion']
