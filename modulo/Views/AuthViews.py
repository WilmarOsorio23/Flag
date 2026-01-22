# Modulo/Views/auth_views.py

import re
from datetime import timedelta
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db import connection, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from ..forms import CustomUserEditForm, CustomUserForm, UserRoleForm
from ..models import CustomUser, LoginAttempt, UserRole


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def check_login_attempts(email, ip_address):
    """
    Verifica intentos fallidos en los últimos 15 minutos.
    Bloquea si >= 5.
    """
    tiempo_bloqueo = timezone.now() - timedelta(minutes=15)
    intentos_fallidos = LoginAttempt.objects.filter(
        email=email,
        ip_address=ip_address,
        timestamp__gte=tiempo_bloqueo,
        successful=False,
    ).count()
    return intentos_fallidos >= 5


def is_admin(user):
    return user.is_superuser or user.is_staff


# -------------------------
# Auth
# -------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("inicio")

    if request.method == "POST":
        username_or_email = request.POST.get("username")
        password = request.POST.get("password")
        ip_address = get_client_ip(request)

        if check_login_attempts(username_or_email, ip_address):
            messages.error(
                request,
                "Su cuenta ha sido bloqueada temporalmente por múltiples intentos fallidos. "
                "Por favor, intente nuevamente en 15 minutos.",
            )
            return render(request, 'Login/Login.html')

        user = authenticate(request, username=username_or_email, password=password)

        # Registrar intento
        LoginAttempt.objects.create(
            email=username_or_email,
            ip_address=ip_address,
            successful=user is not None,
        )

        if user is not None:
            if user.is_active:
                login(request, user)
                next_url = request.GET.get("next", "inicio")
                return redirect(next_url)
            messages.error(request, "Su cuenta está desactivada.")
        else:
            messages.error(request, "Usuario/Email o contraseña incorrectos.")

    return render(request, 'Login/Login.html')


def logout_view(request):
    logout(request)
    return redirect("login")


# -------------------------
# Roles
# -------------------------
@login_required
@user_passes_test(is_admin)
def role_list(request):
    roles = UserRole.objects.all().order_by("name")
    return render(request, 'Roles/RoleList.html', {"roles": roles})


@login_required
@user_passes_test(is_admin)
def role_create(request):
    if request.method == "POST":
        form = UserRoleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol creado exitosamente.")
            return redirect("role_list")
    else:
        form = UserRoleForm()

    return render(request, 'Roles/RoleForm.html', {"form": form, "title": "Crear Rol"})


@login_required
@user_passes_test(is_admin)
def role_edit(request, role_id):
    role = get_object_or_404(UserRole, id=role_id)

    if request.method == "POST":
        form = UserRoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, "Rol actualizado exitosamente.")
            return redirect("role_list")
    else:
        form = UserRoleForm(instance=role)

    return render(
        request,
        'Roles/RoleForm.html',
        {"form": form, "title": "Editar Rol", "role": role},
    )


@login_required
@user_passes_test(is_admin)
def role_delete(request, role_id):
    role = get_object_or_404(UserRole, id=role_id)

    if request.method == "POST":
        users_with_role = CustomUser.objects.filter(role=role)
        if users_with_role.exists():
            messages.error(
                request,
                f'No se puede eliminar el rol "{role.name}" porque hay {users_with_role.count()} usuario(s) asignado(s) a este rol.',
            )
            return redirect("role_list")

        role.delete()
        messages.success(request, "Rol eliminado exitosamente.")
        return redirect("role_list")

    users_with_role = CustomUser.objects.filter(role=role)
    context = {
        "role": role,
        "users_with_role": users_with_role,
        "can_delete": not users_with_role.exists(),
    }
    return render(request, 'Roles/RolecConfirmDelete.html', context)


# -------------------------
# Users (OPTIMIZADO)
# -------------------------
@login_required
@user_passes_test(is_admin)
def user_list(request):
    q = (request.GET.get("q") or "").strip()

    per_page_options = [25, 50, 100, 200]
    try:
        per_page = int(request.GET.get("per_page") or 50)
    except ValueError:
        per_page = 50

    if per_page not in per_page_options:
        per_page = 50

    users_qs = (
        CustomUser.objects.select_related("role")
        .only(
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "role__id",
            "role__name",
        )
        .order_by("email")
    )

    if q:
        users_qs = users_qs.filter(
            Q(email__icontains=q)
            | Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
            | Q(role__name__icontains=q)
        )

    paginator = Paginator(users_qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Para construir links de paginación sin perder filtros
    base_params = {"per_page": per_page}
    if q:
        base_params["q"] = q
    base_qs = urlencode(base_params)

    return render(
        request,
        'Users/Userlist.html',
        {
            "page_obj": page_obj,
            "q": q,
            "per_page": per_page,
            "per_page_options": per_page_options,
            "base_qs": base_qs,  # <- para ?q=...&per_page=...&page=...
        },
    )


@login_required
@user_passes_test(is_admin)
def user_create(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario creado exitosamente.")
            return redirect("user_list")
    else:
        form = CustomUserForm()

    return render(request, 'Users/UserForm.html', {"form": form, "title": "Crear Usuario"})


@login_required
@user_passes_test(is_admin)
def user_edit(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado exitosamente.")
            return redirect("user_list")
    else:
        form = CustomUserEditForm(instance=user)

    return render(
        request,
        'Users/UserForm.html',
        {"form": form, "title": "Editar Usuario", "user": user},
    )


@login_required
@user_passes_test(is_admin)
def user_delete(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        # ⚠️ Mantengo tu estrategia de SQL crudo (según tu proyecto)
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM custom_users WHERE id = %s", [user.id])

        messages.success(request, "Usuario eliminado exitosamente.")
        return redirect("user_list")

    return redirect("user_list")


# -------------------------
# Permisos (robusto + batch)
# -------------------------
@require_GET
def check_permission(request):
    """
    Soporta:
    - /check-permission/?feature=can_manage_users
    - /check-permission/?feature=a,b,c
    - /check-permission/?feature=a&feature=b&feature=c

    Respuestas:
    - 200 JSON
    - 401 JSON si no autenticado
    - 400 JSON si falta feature
    - 500 JSON si hay excepción (para que el JS lo registre)
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({"has_permission": False, "error": "No autenticado"}, status=401)

        features = request.GET.getlist("feature")
        if len(features) == 1 and features[0] and "," in features[0]:
            features = [f.strip() for f in features[0].split(",") if f.strip()]

        if not features:
            return JsonResponse({"has_permission": False, "error": "feature es requerido"}, status=400)

        # Superuser/staff: todo true
        if request.user.is_superuser or request.user.is_staff:
            if len(features) == 1:
                return JsonResponse({"has_permission": True})
            return JsonResponse({"permissions": {f: True for f in features}})

        role = getattr(request.user, "role", None)
        if not role:
            if len(features) == 1:
                return JsonResponse({"has_permission": False})
            return JsonResponse({"permissions": {f: False for f in features}})

        safe_name = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

        def resolve_one(feature: str) -> bool:
            if not feature or not safe_name.match(feature):
                return False
            return bool(getattr(role, feature, False))

        if len(features) == 1:
            return JsonResponse({"has_permission": resolve_one(features[0])})

        return JsonResponse({"permissions": {f: resolve_one(f) for f in features}})

    except Exception as e:
        return JsonResponse({"has_permission": False, "error": str(e)}, status=500)


@login_required
def test_permissions(request):
    return render(request, "TestPermissions.html")


@login_required
def cambiar_password(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if not request.user.check_password(old_password):
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, 'Users/Changepassword.html')

        if new_password1 != new_password2:
            messages.error(request, "Las nuevas contraseñas no coinciden.")
            return render(request, 'Users/Changepassword.html')

        if len(new_password1 or "") < 8:
            messages.error(request, "La nueva contraseña debe tener al menos 8 caracteres.")
            return render(request, 'Users/Changepassword.html')

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, "Contraseña actualizada exitosamente.")

        update_session_auth_hash(request, request.user)
        return redirect("inicio")

    return render(request, 'Users/ChangePassword.html')
