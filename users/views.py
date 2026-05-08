from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView, FormView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .mock_data import filter_by_access_level, DOCUMENTS, PROJECTS, REPORTS
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

        from .models import Role, UserRole
        try:
            default_role = Role.objects.get(name='User')
            UserRole.objects.create(user=user, role=default_role)
        except Role.DoesNotExist:
            pass

        login(self.request, user)
        return super().form_valid(form)


class LoginView(FormView):
    """Вход в систему."""
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_url = reverse_lazy('users:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
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
    """Просмотр профиля текущего пользователя."""

    def get(self, request):
        user = request.user

        roles = list(user.get_roles().values_list('name', flat=True))

        can_view_all_users = user.has_permission('users.view_all')
        can_manage_roles = user.has_permission('roles.manage')

        return render(request, 'users/profile.html', {
            'user': user,
            'roles': roles,
            'can_view_all_users': can_view_all_users,
            'can_manage_roles': can_manage_roles,
        })


class UpdateProfileView(LoginRequiredMixin, View):
    """Редактирование профиля."""

    def get(self, request):
        return render(request, 'users/update_profile.html', {'user': request.user})

    def post(self, request):
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
        return render(request, 'users/delete_account.html')

    def post(self, request):
        password = request.POST.get('password', '')
        user = request.user

        if not user.check_password(password):
            return render(request, 'users/delete_account.html', {
                'error': 'Неверный пароль.'
            })

        user.soft_delete()
        logout(request)

        return redirect('users:login')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Просмотр всех пользователей."""
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'

    def test_func(self):
        return self.request.user.has_permission('users.view_all')

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return JsonResponse({'error': 'Требуется аутентификация'}, status=401)
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    def get_context_data(self, **kwargs):
        """Добавляет статистику в контекст шаблона."""
        context = super().get_context_data(**kwargs)
        context['active_count'] = User.objects.filter(is_active=True).count()
        context['inactive_count'] = User.objects.filter(is_active=False).count()
        return context


class BusinessBaseView(LoginRequiredMixin, View):
    """ Базовый класс для бизнес-представлений."""
    required_permission = None

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'error': 'Требуется аутентификация',
                    'error_type': 'authentication_required'
                }, status=401)
            return redirect(f"{reverse_lazy('users:login')}?next={request.path}")

        if self.required_permission and not request.user.has_permission(self.required_permission):
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'error': 'Доступ запрещён',
                    'detail': f'Требуется право: {self.required_permission}',
                    'error_type': 'permission_denied'
                }, status=403)
            return render(request, 'users/error_403.html', status=403)

        return super().dispatch(request, *args, **kwargs)

    def get_user_roles(self):
        """Получает список ролей пользователя."""
        return list(self.request.user.get_roles().values_list('name', flat=True))


class DocumentListView(BusinessBaseView):
    """Список документов."""
    required_permission = 'users.view_self'

    def get(self, request):
        roles = self.get_user_roles()
        documents = filter_by_access_level(DOCUMENTS, request.user.email, roles)

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'documents': documents}, status=200)

        return render(request, 'users/documents.html', {
            'documents': documents,
            'user': request.user,
            'roles': roles
        })


class ProjectListView(BusinessBaseView):
    """Список проектов."""
    required_permission = 'users.view_self'

    def get(self, request):
        roles = self.get_user_roles()
        user_email = request.user.email

        if 'Admin' in roles:
            projects = PROJECTS
        elif 'Moderator' in roles:
            projects = [p for p in PROJECTS
                        if p['manager'] == user_email or user_email in p.get('team', [])]
        else:
            projects = [p for p in PROJECTS
                        if p['manager'] == user_email or user_email in p.get('team', [])]

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'projects': projects}, status=200)

        return render(request, 'users/projects.html', {
            'projects': projects,
            'user': request.user,
            'roles': roles
        })


class ReportListView(BusinessBaseView):
    """Список отчётов."""
    required_permission = 'users.view_all'

    def get(self, request):
        roles = self.get_user_roles()

        if 'Admin' in roles or 'Moderator' in roles:
            reports = REPORTS
        else:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'error': 'Доступ запрещён',
                    'detail': 'Отчёты доступны только администраторам и модераторам',
                    'error_type': 'permission_denied'
                }, status=403)
            return render(request, 'users/error_403.html', {
                'message': 'Отчёты доступны только администраторам и модераторам'
            }, status=403)

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({'reports': reports}, status=200)

        return render(request, 'users/reports.html', {
            'reports': reports,
            'user': request.user,
            'roles': roles
        })
