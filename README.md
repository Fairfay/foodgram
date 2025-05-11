cd /infra

Заполнить .env по примеру .env template


docker-compose up --build -d
 
docker exec  -it <container_name> python manage.py makemigrations 

docker exec -it <container_name> python manage.py migrate 

docker exec -it <container_name> python manage.py createsuperuser 

docker exec -it <container_name> python manage.py collectstatic --no-input
