from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from modulo.models import UserRole

User = get_user_model()

class Command(BaseCommand):
    help = 'Test permission system'

    def handle(self, *args, **options):
        self.stdout.write('=== Testing Permission System ===')
        
        # Obtener todos los usuarios
        users = User.objects.all()
        
        for user in users:
            self.stdout.write(f'\nUsuario: {user.email}')
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Is Superuser: {user.is_superuser}')
            self.stdout.write(f'Is Staff: {user.is_staff}')
            
            if hasattr(user, 'role') and user.role:
                self.stdout.write(f'Rol: {user.role.name}')
                
                # Test some permissions
                permissions_to_test = [
                    'can_manage_users',
                    'can_manage_roles',
                    'can_manage_clientes',
                    'can_manage_consultores',
                    'can_view_informe_clientes'
                ]
                
                for permission in permissions_to_test:
                    if hasattr(user.role, permission):
                        has_perm = getattr(user.role, permission)
                        self.stdout.write(f'  {permission}: {has_perm}')
                    else:
                        self.stdout.write(f'  {permission}: NO EXISTE')
            else:
                self.stdout.write('Sin rol asignado')
        
        # Test roles
        self.stdout.write('\n=== Roles Disponibles ===')
        roles = UserRole.objects.all()
        for role in roles:
            self.stdout.write(f'\nRol: {role.name}')
            users_with_role = User.objects.filter(role=role)
            self.stdout.write(f'Usuarios con este rol: {users_with_role.count()}')
            
            # Test some permissions for this role
            permissions_to_test = [
                'can_manage_users',
                'can_manage_roles',
                'can_manage_clientes',
                'can_manage_consultores'
            ]
            
            for permission in permissions_to_test:
                if hasattr(role, permission):
                    has_perm = getattr(role, permission)
                    self.stdout.write(f'  {permission}: {has_perm}')
        
        self.stdout.write('\n=== Test Completed ===')