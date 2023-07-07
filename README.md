## Проект Foodgram

Проект позволяет просматривать рецепты и добавлять свои 


### Использованные технологии

Django, Django REST Framework, Node.js


### Установка и запуск проекта: 

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Maniackaa/kittygram_final.git
```

```
cd kittygram_final
```
В папку kittygram_final создать файл .env
```
nano .env
```

в котором указать переменные, например:
```
POSTGRES_USER=django
POSTGRES_PASSWORD=12345
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
SECRET_KEY='django-insecure-5!@(1#jwja4*pmu@0t2@r$!m8*g!tftwuotz4a527mqz99-u15'
DEBUG=False
ALLOWED_HOSTS='158.160.69.22,127.0.0.1,localhost,*' # Обязательно указать адрес сервера
NGINX_PORT=9000
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