# Foodgram - Продуктовый помощник

[![Docker CI](https://github.com/Daviiks/foodgram-st/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Daviiks/foodgram-st/actions/workflows/docker-image.yml)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-foodgram--backend-blue)](https://hub.docker.com/r/daviiel/foodgram-backend)

Foodgram - это веб-приложение для публикации рецептов. Пользователи могут создавать свои рецепты, подписываться на других авторов, добавлять рецепты в избранное и в список покупок.

## 🚀 Запуск приложения

### Вариант 1: Запуск в режиме DEBUG (SQLite3)

1. **Запуск сервера**:
   ```bash
   python manage.py runserver --mode dev
# Инструкция
## Запуск приложения c DEBUG и использованием SQLlite3
Запуск приложения
Запустить приложение можно двумя способами.
1 способ в режиме DEBUG: 
Находясь в папке backend, выполняем команду:
python manage.py runserver --mode dev
После создаем супер пользователя
python manage.py createsuperuser
Затем создаем миграции и запускаем их:
python manage.py makemigrations
python manage.py migrate
Затем загружаем ингредиенты командой:
python manage.py load_ingredients --path data/ingredients.csv
Можно заргузить ещё тестовых user и recipes:
python manage.py load_recipes --path data/users.json
python manage.py load_recipes --path data/recipes.json
Сайт доступен по адресу http://localhost:8000, http://localhost:8000/api
Панель администратора доступна по адресу http://localhost:8000/admin/.
Спецификация API доступна по адресу http://localhost:8000/api/docs/
## Импортирование ингредиентов
## Конфигурация foodgram-backend
Инструкция
Запуск приложения
Запустить приложение можно двумя способами.
## Запуск приложения c Docker и использованием PostgreSQL
2 способ с помощью Docker:
Находясь в папке infra, выполняем команду:
docker-compose up --build
При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.
После создаем супер пользователя:
docker compose run backend python manage.py createsuperuser
Затем создаем миграции и запускаем их:
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
Затем загружаем ингредиенты командой:
docker-compose exec backend python manage.py load_ingredients --path data/ingredients.csv
Можно заргузить ещё тестовых user и recipes:
docker-compose exec backend python manage.py load_recipes --path data/users.json
docker-compose exec backend python manage.py load_recipes --path data/recipes.json
Приложение доступно по адресу http://localhost
Панель администратора доступна по адресу http://localhost/admin/
Спецификация API доступна по адресу http://localhost/api/docs/
Панель администратора доступна по адресу http://localhost/admin/
Можно выполнить тесты Postman для работоспособности сайта. Все тесты выполнять с бд без пользователей которые создаются тестами. Для повторного тестирования советую удалить пользователей созданные тестами postman из админки или удалить бд.
