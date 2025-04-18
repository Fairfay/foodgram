Находясь в папке infra, выполните команду docker-compose up --build.

Находясь в папке /infra, запустить сборку образа Docker:
sudo docker compose up -d
Выполните миграции:
sudo docker compose exec infra-backend python manage.py makemigrations
sudo docker compose exec infra-backend python manage.py migrate
Создайте суперпользователя:
sudo docker compose exec infra-backend python manage.py createsuperuser
Выполните команду collectstatic:
sudo docker compose exec infra-backend python manage.py collectstatic --no-input
Заполните базу данными:
sudo docker compose exec infra-backend python manage.py import_data ingredients.csv
не забудьте настроить env
DB_ENGINE=
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=
SECRET_KEY=
DEBUG=
ALLOWED_HOSTS=
