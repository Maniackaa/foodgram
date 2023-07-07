## Проект Foodgram

Проект позволяет просматривать рецепты и добавлять свои 


### Использованные технологии

Django, Django REST Framework, Node.js


### Установка и запуск проекта: 

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Maniackaa/foodgram
```

```
cd foodgram/infra
```
В папку infra создать файл .env
```
nano .env
```

в котором указать переменные, например:
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=111333
POSTGRES_DB=postgres_db
DB_HOST=db_postgres_container
#DB_HOST=localhost
DB_PORT=5432
PGADMIN_DEFAULT_EMAIL=maniac_kaa@mail.ru
PGADMIN_DEFAULT_PASSWORD=111333
SECRET_KEY='django-insecure-5!@(1#jwja4*pmu@0t2@r$!m8*g!tftwuotz4a527mqz99-u12'
DEBUG=True
ALLOWED_HOSTS='158.160.69.22,127.0.0.1,localhost,taskikiski.hopto.org,*'
NGINX_PORT=80
```
Сохранить содержимое ctrl+O, ctrl+x. 

Для запуска выполнить команду 
```
docker compose-up -d
```

# Об авторе
### Об авторе.
<h1 align="center">Hi there, I'm <a href="https://oldit.ru" target="_blank">Alexey</a> 
<img src="https://github.com/blackcater/blackcater/raw/main/images/Hi.gif" height="32"/></h1>
<h3 align="center">Python backend student from Russia.</h3>