from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def verificar_permiso(permiso_requerido):
    """
    Decorador para verificar si un usuario tiene un permiso específico a través de su rol.
    
    Uso:
    @verificar_permiso('can_manage_modulo')
    def vista(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Superusuarios y staff siempre tienen acceso
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Verificar si el usuario tiene un rol asignado
            if not request.user.role:
                messages.error(request, 'No tiene un rol asignado.')
                return redirect('inicio')
            
            # Verificar si el rol tiene el permiso requerido
            if not hasattr(request.user.role, permiso_requerido) or \
               not getattr(request.user.role, permiso_requerido):
                messages.error(request, 'No tiene permiso para acceder a esta sección.')
                return redirect('inicio')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator