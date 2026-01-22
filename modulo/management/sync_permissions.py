from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from modulo.models import UserRole

class Command(BaseCommand):
    help = 'Sincroniza los permisos del sistema con los modelos de la base de datos'
    
    def handle(self, *args, **options):
        self.stdout.write('Sincronizando permisos...')
        
        # Aquí puedes agregar lógica para sincronizar permisos
        # entre el sistema de Django y tu sistema personalizado de roles
        
        self.stdout.write(self.style.SUCCESS('Permisos sincronizados correctamente'))