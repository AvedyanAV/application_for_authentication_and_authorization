from functools import wraps
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied


def require_permission(permission_codename):
    """Декоратор для проверки наличия разрешения у пользователя."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                response_data = {
                    'error': 'Требуется аутентификация',
                    'detail': 'Пожалуйста, войдите в систему.'
                }
                if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
                    return JsonResponse(response_data, status=401)
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(f"{reverse('users:login')}?next={request.path}")

            if not request.user.has_permission(permission_codename):
                response_data = {
                    'error': 'Доступ запрещён',
                    'detail': f'У вас нет права: {permission_codename}'
                }
                if request.headers.get('Accept') == 'application/json' or request.path.startswith('/api/'):
                    return JsonResponse(response_data, status=403)
                raise PermissionDenied("У вас нет прав для выполнения этого действия.")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
