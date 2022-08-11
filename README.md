# Описание сервиса
Сайт Foodgram, «Продуктовый помощник». Cервис для публикации рецептов.<br>
Пользователи могут подписываться на публикации других пользователей,
добавлять понравившиеся рецепты в список «Избранное»,
а перед походом в магазин скачивать сводный список продуктов,
необходимых для приготовления одного или нескольких выбранных блюд.

# Сайт
http://51.250.22.204

# Документация API
http://51.250.22.204/api/redoc

# Установка
1. Клонируйте репрозиторий ```https://github.com/ilin-art/foodgram-project-react```
2. Установите Docker (https://docs.docker.com/engine/install/)
3. Выполните ```docker-compose up -d --build```
4. Выполните:<br>
  ```docker-compose exec web python manage.py migrate --noinput```<br>
  ```docker-compose exec web python manage.py createsuperuser```<br>
  ```docker-compose exec web python manage.py collectstatic --no-input ```
5. Теперь проект доступен по адресу http://51.250.22.204

# Технологии
* Python
* Django
* Django REST
* Docker

# Проект разработал:
* [Ильин Артём](https://github.com/ilin-art)
