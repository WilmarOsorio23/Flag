from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from datetime import timedelta
from ..forms import UserRoleForm, CustomUserForm, CustomUserEditForm
from ..models import UserRole, CustomUser, LoginAttempt
from django.db import connection, transaction

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def check_login_attempts(email, ip_address):
    """
    Verifica los intentos de inicio de sesión fallidos en los últimos 15 minutos.
    Retorna True si el usuario debe ser bloqueado.
    """
    tiempo_bloqueo = timezone.now() - timedelta(minutes=15)
    intentos_fallidos = LoginAttempt.objects.filter(
        email=email,
        ip_address=ip_address,
        timestamp__gte=tiempo_bloqueo,
        successful=False
    ).count()
    return intentos_fallidos >= 5

def is_admin(user):
    return user.is_superuser or user.is_staff

# auth_views.py
def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
        
    if request.method == 'POST':
        username_or_email = request.POST.get('username')
        password = request.POST.get('password')
        ip_address = get_client_ip(request)
        
        # Verificar si el usuario está bloqueado
        if check_login_attempts(username_or_email, ip_address):
            messages.error(request, 'Su cuenta ha sido bloqueada temporalmente por múltiples intentos fallidos. Por favor, intente nuevamente en 15 minutos.')
            return render(request, 'Login/login.html')
        
        user = authenticate(request, username=username_or_email, password=password)
        
        # Registrar el intento de inicio de sesión
        LoginAttempt.objects.create(
            email=username_or_email,
            ip_address=ip_address,
            successful=user is not None
        )
        
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirigir según el rol o página por defecto
                next_url = request.GET.get('next', 'inicio')
                return redirect(next_url)
            else:
                messages.error(request, 'Su cuenta está desactivada.')
        else:
            messages.error(request, 'Usuario/Email o contraseña incorrectos.')
    
    return render(request, 'Login/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
@user_passes_test(is_admin)
def role_list(request):
    roles = UserRole.objects.all()
    return render(request, 'roles/role_list.html', {'roles': roles})

@login_required
@user_passes_test(is_admin)
def role_create(request):
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol creado exitosamente.')
            return redirect('role_list')
    else:
        form = UserRoleForm()
    
    return render(request, 'roles/role_form.html', {'form': form, 'title': 'Crear Rol'})

@login_required
@user_passes_test(is_admin)
def role_edit(request, role_id):
    role = get_object_or_404(UserRole, id=role_id)
    
    if request.method == 'POST':
        form = UserRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, 'Rol actualizado exitosamente.')
            return redirect('role_list')
    else:
        form = UserRoleForm(instance=role)
    
    return render(request, 'roles/role_form.html', {'form': form, 'title': 'Editar Rol', 'role': role})

@login_required
@user_passes_test(is_admin)
def role_delete(request, role_id):
    role = get_object_or_404(UserRole, id=role_id)
    if request.method == 'POST':
        # Verificar si hay usuarios con este rol
        users_with_role = CustomUser.objects.filter(role=role)
        if users_with_role.exists():
            messages.error(request, f'No se puede eliminar el rol "{role.name}" porque hay {users_with_role.count()} usuario(s) asignado(s) a este rol.')
            return redirect('role_list')
        
        role.delete()
        messages.success(request, 'Rol eliminado exitosamente.')
        return redirect('role_list')
    
    # Verificar si hay usuarios con este rol para mostrar advertencia
    users_with_role = CustomUser.objects.filter(role=role)
    context = {
        'role': role,
        'users_with_role': users_with_role,
        'can_delete': not users_with_role.exists()
    }
    return render(request, 'roles/role_confirm_delete.html', context)

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'users/user_list.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = CustomUserForm()
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Crear Usuario'})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = CustomUserEditForm(instance=user)
    
    return render(request, 'users/user_form.html', {'form': form, 'title': 'Editar Usuario', 'user': user})

@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == 'POST':
        # Eliminar usando SQL crudo para evitar limpiar M2M (custom_users_groups, etc.)
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM custom_users WHERE id = %s", [user.id])
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('user_list')
    return redirect('user_list')  # Redirige si no es POST

@login_required
def check_permission(request):
    feature = request.GET.get('feature')
    if not feature:
        return JsonResponse({'error': 'Este campo es requerido'}, status=400)
    
    # Superusuarios y staff siempre tienen permisos
    if request.user.is_superuser or request.user.is_staff:
        return JsonResponse({'has_permission': True})
        
    has_permission = False
    if hasattr(request.user, 'role') and request.user.role:
        if hasattr(request.user.role, feature):
            has_permission = getattr(request.user.role, feature)
        
    return JsonResponse({'has_permission': has_permission})

@login_required
def test_permissions(request):
    return render(request, 'test_permissions.html')

@login_required
def cambiar_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not request.user.check_password(old_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return render(request, 'users/change_password.html')

        if new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return render(request, 'users/change_password.html')

        if len(new_password1) < 8:
            messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            return render(request, 'users/change_password.html')

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Contraseña actualizada exitosamente.')
        
        # Actualizar la sesión para mantener al usuario conectado
        update_session_auth_hash(request, request.user)
        
        return redirect('inicio')

    return render(request, 'users/change_password.html')