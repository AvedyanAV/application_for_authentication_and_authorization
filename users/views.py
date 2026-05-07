from django.http import JsonResponse
from django.views import View
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from .models import User
from .forms import UserRegistrationForm


class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        """Сохраняет пользователя и выполняет автоматический вход."""
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        """Возвращает ошибки валидации."""
        return JsonResponse({'errors': form.errors}, status=400)


class LoginView(View):
    """Вход в систему."""

    def post(self, request):
        return JsonResponse({"message": "Login endpoint работает"}, status=501)


class LogoutView(View):
    """Выход из системы."""

    def post(self, request):
        return JsonResponse({"message": "Logout endpoint работает"}, status=501)


class ProfileView(View):
    """Просмотр профиля текущего пользователя."""

    def get(self, request):
        return JsonResponse({"message": "Profile endpoint работает"}, status=501)


class UpdateProfileView(View):
    """Обновление данных профиля."""

    def put(self, request):
        return JsonResponse({"message": "Update profile endpoint работает"}, status=501)

    def patch(self, request):
        return JsonResponse({"message": "Update profile endpoint работает"}, status=501)


class DeleteAccountView(View):
    """Мягкое удаление аккаунта."""

    def delete(self, request):
        return JsonResponse({"message": "Delete account endpoint работает"}, status=501)
