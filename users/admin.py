from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомная админка для модели User."""

    ordering = ('email',)

    list_display = (
        'email',
        'is_active',
        'is_soft_deleted',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'email',
        'first_name',
        'last_name',
        'patronymic',
    )

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Личная информация'), {
            'fields': ('first_name', 'last_name', 'patronymic')
        }),
        (_('Разрешения'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'patronymic',
                'password1',
                'password2',
            ),
        }),
    )

    readonly_fields = ('last_login', )

    actions = ['make_active', 'make_inactive', 'soft_delete_selected']

    @admin.action(description="Активировать")
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True, deleted_at=None)
        self.message_user(request, f"{updated} пользователей активировано.")

    @admin.action(description="Деактивировать")
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} пользователей деактивировано.")

    @admin.action(description="Мягко удалить")
    def soft_delete_selected(self, request, queryset):
        now = timezone.now()
        updated = queryset.update(is_active=False, deleted_at=now)
        self.message_user(request, f"{updated} пользователей мягко удалено.")
