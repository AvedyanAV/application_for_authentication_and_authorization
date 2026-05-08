from django.core.management.base import BaseCommand
from users.models import User, Role, Permission, RolePermission, UserRole


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными для RBAC'

    def handle(self, *args, **options):
        self.stdout.write('Создание разрешений...')

        permissions_data = [
            ('users.view_self', 'Просмотр своего профиля', 'users', 'view'),
            ('users.view_all', 'Просмотр всех профилей', 'users', 'view'),
            ('users.edit_self', 'Редактирование своего профиля', 'users', 'edit'),
            ('users.edit_all', 'Редактирование всех профилей', 'users', 'edit'),
            ('users.delete_self', 'Удаление своего аккаунта', 'users', 'delete'),
            ('users.delete_any', 'Удаление любого аккаунта', 'users', 'delete'),
            ('roles.view', 'Просмотр ролей', 'roles', 'view'),
            ('roles.manage', 'Управление ролями', 'roles', 'manage'),
        ]

        permissions = {}
        for codename, name, resource, action in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'resource': resource,
                    'action': action,
                    'description': f'{name} ({resource}.{action})'
                }
            )
            permissions[codename] = perm
            if created:
                self.stdout.write(f'  ✓ Создано разрешение: {codename}')

        self.stdout.write('\nСоздание ролей...')

        admin_role, created = Role.objects.get_or_create(
            name='Admin',
            defaults={
                'description': 'Полный доступ ко всем ресурсам',
                'is_system': True
            }
        )
        if created:
            self.stdout.write('  ✓ Создана роль: Admin')

        for perm in permissions.values():
            RolePermission.objects.get_or_create(role=admin_role, permission=perm)

        moderator_perms = [
            'users.view_all',
            'users.edit_self',
            'users.delete_self',
            'roles.view',
        ]
        moderator_role, created = Role.objects.get_or_create(
            name='Moderator',
            defaults={
                'description': 'Модератор с расширенными правами просмотра',
                'is_system': True
            }
        )
        if created:
            self.stdout.write('  ✓ Создана роль: Moderator')
        for codename in moderator_perms:
            RolePermission.objects.get_or_create(
                role=moderator_role,
                permission=permissions[codename]
            )

        user_perms = [
            'users.view_self',
            'users.edit_self',
            'users.delete_self',
        ]
        user_role, created = Role.objects.get_or_create(
            name='User',
            defaults={
                'description': 'Обычный пользователь',
                'is_system': True
            }
        )
        if created:
            self.stdout.write('  ✓ Создана роль: User')
        for codename in user_perms:
            RolePermission.objects.get_or_create(
                role=user_role,
                permission=permissions[codename]
            )

        self.stdout.write('\nНазначение ролей...')

        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'Adminov',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('Admin123!')
            admin_user.save()
            self.stdout.write('  ✓ Создан admin@example.com (пароль: Admin123!)')

        moderator_user, created = User.objects.get_or_create(
            email='moderator@example.com',
            defaults={
                'first_name': 'Moder',
                'last_name': 'Moderov',
            }
        )
        if created:
            moderator_user.set_password('Moderator123!')
            moderator_user.save()
            self.stdout.write('  ✓ Создан moderator@example.com (пароль: Moderator123!)')

        regular_user, created = User.objects.get_or_create(
            email='user@example.com',
            defaults={
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
            }
        )
        if created:
            regular_user.set_password('User123!')
            regular_user.save()
            self.stdout.write('  ✓ Создан user@example.com (пароль: User123!)')

        UserRole.objects.get_or_create(user=admin_user, role=admin_role)
        self.stdout.write('  ✓ admin@example.com → Admin')

        UserRole.objects.get_or_create(user=moderator_user, role=moderator_role)
        self.stdout.write('  ✓ moderator@example.com → Moderator')

        UserRole.objects.get_or_create(user=regular_user, role=user_role)
        self.stdout.write('  ✓ user@example.com → User')

        self.stdout.write(self.style.SUCCESS('\n✓ Тестовые данные RBAC успешно созданы!'))
        self.stdout.write('\nТестовые аккаунты:')
        self.stdout.write('  Admin:     admin@example.com / Admin123!')
        self.stdout.write('  Moderator: moderator@example.com / Moderator123!')
        self.stdout.write('  User:      user@example.com / User123!')
