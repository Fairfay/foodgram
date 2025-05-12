## Фудграм (Foodgram)
Описание проекта
Фудграм — это онлайн-платформа, где пользователи могут публиковать рецепты, просматривать рецепты других авторов, добавлять их в избранное, подписываться на любимых авторов и формировать список покупок для приготовления блюд.

## Возможности проекта:
Публикация рецептов : пользователи могут создавать и редактировать собственные рецепты.

Избранное : добавление рецептов в список избранных для быстрого доступа.

Подписки : возможность подписаться на других авторов и следить за их новыми рецептами.

Список покупок : автоматическое формирование списка необходимых ингредиентов для выбранных рецептов.

Фильтрация по тегам : удобный поиск рецептов по категориям.

Короткие ссылки : генерация прямых ссылок на рецепты для простого обмена.

## Используемые технологии
Backend :

Python 3.12

Django 4.2

Django REST Framework (DRF)

Djoser (JWT-аутентификация)

PostgreSQL (основная БД)

Pillow (обработка изображений)

Gunicorn (WSGI-сервер)

Nginx (обратный прокси-сервер)

Docker (для контейнеризации)

Frontend :

React (SPA-приложение)

Base64-изображения

JavaScript/TypeScript

API документация :

drf-yasg (Swagger UI)

Дополнительно :

Debug Toolbar (для отладки)

Decouple (управление конфигурациями)

## Инструкция по запуску
```bash
cd /infra 
```

Заполнить .env по примеру .env template

Соберите образы :
```bash
docker-compose up -d --build
```
Выполните миграции :
```bash
docker exec -it <container_name> python manage.py makemigrations
docker exec -it <container_name> python manage.py migrate
```
Создайте суперпользователя :
```bash
docker exec -it <container_name> python manage.py createsuperuser
```
Соберите статику :
```bash
docker exec -it <container_name> python manage.py collectstatic --no-input
```

## Примеры запросов к API
Получение списка рецептов
GET /api/recipes/

Получение конкретного рецепта
GET /api/recipes/1/

Создание рецепта
POST /api/recipes/
Content-Type: application/json
{
  "name": "Рецепт",
  "text": "Описание рецепта",
  "cooking_time": 30,
  "image": "data:image/png;base64,...",
  "tags": [1, 2],
  "ingredients": [
    {"id": 1, "amount": 500},
    {"id": 2, "amount": 200}
  ]
}

Добавление в избранное
POST /api/recipes/1/favorite/

Скачивание списка покупок
GET /api/recipes/download-shopping-cart/

Автор

Тычин Денис Александрович

Email: tycindenis@gmail.com

Вклад

Любые предложения по улучшению проекта приветствуются! Создавайте issue или pull request в репозитории проекта.
