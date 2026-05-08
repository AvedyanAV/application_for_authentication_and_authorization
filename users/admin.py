from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import User
from django.contrib import admin
from .models import User, Role, Permission, RolePermission, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Кастомная админка для модели User."""

    ordering = ('email',)

    list_display = (
        'email',
        'is_active',
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


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_system', 'created_at')
    list_filter = ('is_system',)
    search_fields = ('name',)
    inlines = [RolePermissionInline]
    readonly_fields = ('is_system', 'created_at')


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name', 'resource', 'action', 'created_at')
    list_filter = ('resource', 'action')
    search_fields = ('codename', 'name', 'description')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_at', 'assigned_by')
    list_filter = ('role', 'assigned_at')
    search_fields = ('user__email', 'role__name')
