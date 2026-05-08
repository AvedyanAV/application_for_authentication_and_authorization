from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Менеджер для модели User без username."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя."""

    objects = CustomUserManager()

    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name='Email'
    )

    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя'
    )

    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия'
    )

    patronymic = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name='Доступ в админку'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['email']
        indexes = [
            models.Index(fields=['email', 'is_active']),
        ]

    def __str__(self):
        if self.patronymic:
            return f"{self.last_name} {self.first_name} {self.patronymic} ({self.email})"
        return f"{self.last_name} {self.first_name} ({self.email})"

    def soft_delete(self):
        """Мягкое удаление"""
        self.is_active = False
        self.save(update_fields=['is_active', ])

    def restore(self):
        """Восстановление после мягкого удаления"""
        self.is_active = True
        self.save(update_fields=['is_active', ])

    def get_roles(self):
        """Возвращает QuerySet ролей пользователя."""
        return Role.objects.filter(user_roles__user=self)

    def get_permissions(self):
        """Возвращает QuerySet разрешений пользователя."""
        return Permission.objects.filter(
            rolepermission__role__user_roles__user=self
        ).distinct()

    def has_permission(self, permission_codename):
        """Проверяет, есть ли у пользователя конкретное разрешение."""
        if self.is_superuser:
            return True

        return self.get_permissions().filter(codename=permission_codename).exists()

    def has_role(self, role_name):
        """Проверяет, есть ли у пользователя конкретная роль."""
        return self.get_roles().filter(name=role_name).exists()


class Permission(models.Model):
    """Разрешение на выполнение действия над ресурсом."""
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Кодовое имя'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    resource = models.CharField(
        max_length=100,
        verbose_name='Ресурс'
    )
    action = models.CharField(
        max_length=100,
        verbose_name='Действие'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Разрешение'
        verbose_name_plural = 'Разрешения'
        ordering = ['resource', 'action']
        indexes = [
            models.Index(fields=['codename']),
            models.Index(fields=['resource', 'action']),
        ]

    def __str__(self):
        return f"{self.name} ({self.codename})"


class Role(models.Model):
    """Роль пользователя с набором разрешений."""
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Название'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        verbose_name='Разрешения',
        related_name='roles'
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name='Системная роль',
        help_text='Системные роли нельзя удалить'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['name']

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """Промежуточная таблица для связи Role-Permission."""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name='Разрешение'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Назначено'
    )

    class Meta:
        verbose_name = 'Разрешение роли'
        verbose_name_plural = 'Разрешения ролей'
        unique_together = [['role', 'permission']]

    def __str__(self):
        return f"{self.role.name} → {self.permission.codename}"


class UserRole(models.Model):
    """Связь пользователя с ролью."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name='Роль',
        related_name='user_roles'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Назначена'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Кем назначена',
        related_name='assigned_roles'
    )

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        unique_together = [['user', 'role']]

    def __str__(self):
        return f"{self.user.email} → {self.role.name}"
