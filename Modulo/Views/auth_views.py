from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from ..forms import UserRoleForm, CustomUserForm
from ..models import UserRole, CustomUser

def is_admin(user):
    return user.is_superuser or user.is_staff

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Email o contraseña incorrectos.')
    
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
    
    return render(request, 'roles/role_form.html', {'form': form})

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
    
    return render(request, 'roles/role_form.html', {'form': form})

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
    
    return render(request, 'users/user_form.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = CustomUserForm(instance=user)
    
    return render(request, 'users/user_form.html', {'form': form})

@login_required
def check_permission(request):
    feature = request.GET.get('feature')
    if not feature:
        return JsonResponse({'error': 'Feature parameter is required'}, status=400)
        
    has_permission = False
    if hasattr(request.user.role, feature):
        has_permission = getattr(request.user.role, feature)
        
    return JsonResponse({'has_permission': has_permission})