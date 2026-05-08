from django.http import JsonResponse
from django.views import View
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import User
from .forms import UserRegistrationForm, UserLoginForm


class RegisterView(CreateView):
    """Регистрация нового пользователя."""
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:profile')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    """Вход в систему."""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('users:profile')

    def get_form_kwargs(self):
        """Передаём request в форму для аутентификации."""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """При успешной валидации выполняем вход."""
        user = form.get_user()
        login(self.request, user)
        return super().form_valid(form)


class LogoutView(View):
    """Выход из системы."""

    def get(self, request):
        logout(request)
        return redirect('users:login')

    def post(self, request):
        logout(request)
        return redirect('users:login')


class ProfileView(LoginRequiredMixin, View):
    """Просмотр профиля."""

    def get(self, request):
        from django.shortcuts import render
        return render(request, 'users/profile.html', {'user': request.user})


class UpdateProfileView(LoginRequiredMixin, View):
    """Редактирование профиля."""

    def get(self, request):
        """Показывает форму редактирования."""
        return render(request, 'users/update_profile.html', {'user': request.user})

    def post(self, request):
        """Обрабатывает обновление данных."""
        user = request.user

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        patronymic = request.POST.get('patronymic', '').strip()
        email = request.POST.get('email', '').strip()

        errors = []

        if not first_name:
            errors.append('Имя обязательно.')
        if not last_name:
            errors.append('Фамилия обязательна.')
        if not email:
            errors.append('Email обязателен.')
        elif email != user.email and User.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует.')

        if errors:
            return render(request, 'users/update_profile.html', {
                'user': user,
                'errors': errors
            })

        user.first_name = first_name
        user.last_name = last_name
        user.patronymic = patronymic if patronymic else None
        user.email = email
        user.save()

        return redirect('users:profile')


class DeleteAccountView(LoginRequiredMixin, View):
    """Мягкое удаление аккаунта."""

    def get(self, request):
        """Показывает страницу подтверждения удаления."""
        return render(request, 'users/delete_account.html')

    def post(self, request):
        """Выполняет мягкое удаление аккаунта."""
        password = request.POST.get('password', '')
        user = request.user

        if not user.check_password(password):
            return render(request, 'users/delete_account.html', {
                'error': 'Неверный пароль.'
            })

        user.soft_delete()

        logout(request)

        return redirect('users:login')
