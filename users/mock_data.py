"""Данные бизнес-приложения "Система электронного документооборота"."""

DOCUMENTS = [
    {
        'id': 1,
        'title': 'Договор поставки №123',
        'author': 'admin@example.com',
        'status': 'approved',
        'created': '2026-01-15',
        'content': 'Текст договора поставки оборудования...',
        'access_level': 'public'
    },
    {
        'id': 2,
        'title': 'Техническое задание на разработку',
        'author': 'moderator@example.com',
        'status': 'draft',
        'created': '2026-02-20',
        'content': 'Технические требования к системе...',
        'access_level': 'restricted'
    },
    {
        'id': 3,
        'title': 'Финансовый отчёт Q1 2026',
        'author': 'admin@example.com',
        'status': 'approved',
        'created': '2026-03-30',
        'content': 'Конфиденциальные финансовые данные...',
        'access_level': 'confidential'
    },
    {
        'id': 4,
        'title': 'Пользовательская инструкция',
        'author': 'user@example.com',
        'status': 'draft',
        'created': '2026-04-05',
        'content': 'Инструкция по использованию системы...',
        'access_level': 'public'
    },
    {
        'id': 5,
        'title': 'План развития на 2026 год',
        'author': 'admin@example.com',
        'status': 'pending',
        'created': '2026-04-10',
        'content': 'Стратегические цели и задачи...',
        'access_level': 'confidential'
    },
]

PROJECTS = [
    {
        'id': 1,
        'name': 'Внедрение CRM',
        'manager': 'admin@example.com',
        'team': ['admin@example.com', 'moderator@example.com'],
        'status': 'active',
        'deadline': '2026-12-31',
        'budget': 5000000,
    },
    {
        'id': 2,
        'name': 'Разработка мобильного приложения',
        'manager': 'moderator@example.com',
        'team': ['moderator@example.com', 'user@example.com'],
        'status': 'planning',
        'deadline': '2026-09-30',
        'budget': 3000000,
    },
    {
        'id': 3,
        'name': 'Миграция на новую платформу',
        'manager': 'admin@example.com',
        'team': ['admin@example.com'],
        'status': 'completed',
        'deadline': '2026-03-01',
        'budget': 1500000,
    },
]

REPORTS = [
    {
        'id': 1,
        'title': 'Ежемесячный отчёт по продажам',
        'author': 'moderator@example.com',
        'type': 'sales',
        'period': '2026-04',
        'data': {'total_sales': 15000000, 'new_clients': 25}
    },
    {
        'id': 2,
        'title': 'Отчёт по производительности',
        'author': 'admin@example.com',
        'type': 'performance',
        'period': '2026-Q1',
        'data': {'avg_response_time': '120ms', 'uptime': '99.9%'}
    },
    {
        'id': 3,
        'title': 'Анализ рынка конкурентов',
        'author': 'admin@example.com',
        'type': 'analytics',
        'period': '2026-Q1',
        'data': {'market_share': '23%', 'competitors': 5}
    },
]


def filter_by_access_level(items, user_email, user_roles):
    """Фильтрует элементы по уровню доступа и роли пользователя."""
    if 'Admin' in user_roles:
        return items

    if 'Moderator' in user_roles:
        return [item for item in items
                if item.get('access_level', 'public') in ['public', 'restricted']
                or item.get('author') == user_email]

    return [item for item in items
            if item.get('access_level', 'public') == 'public'
            or item.get('author') == user_email]
