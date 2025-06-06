# Foodgram - Продуктовый помощник

[![Docker CI](https://github.com/Daviiks/foodgram-st/actions/workflows/docker-image.yml/badge.svg)](https://github.com/Daviiks/foodgram-st/actions/workflows/docker-image.yml)
[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-foodgram--backend-blue)](https://hub.docker.com/r/daviiel/foodgram-backend)

## Запуск приложения

### Вариант 1: Запуск в режиме DEBUG (SQLite3)
1. **Активация виртуального окружения** (рекомендуется):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   # или
   venv\Scripts\activate  # Windows
2. **Установка зависимостей**:
   ```bash
   pip install -r requirements.txt
3. **Запуск сервера**:
   ```bash
   python manage.py runserver --mode dev
4. **После создаем супер пользователя**:
   ```bash
   python manage.py createsuperuser
5. **Затем создаем миграции и запускаем их**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
6. **Затем загружаем ингредиенты командой**:
   ```bash
   python manage.py load_ingredients --path data/ingredients.csv   
7. **Можно заргузить тестовых users и recipes:**:
   ```bash
   python manage.py load_recipes --path data/users.json
   python manage.py load_recipes --path data/recipes.json   
8. **После создаем супер пользователя**:
   Сайт доступен по адресу http://localhost:8000, http://localhost:8000/api
   Панель администратора доступна по адресу http://localhost:8000/admin/.
   Спецификация API доступна по адресу http://localhost:8000/api/docs/

### Вариант 2: Запуск с Docker (PostgreSQL)
1. **Перейдите в папку infra**:
   ```bash
   cd infra
2. **Собираем и запускаем контейнеры:**:
При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.
   ```bash
   docker-compose up --build
3. **После создаем супер пользователя**:
   ```bash
   docker compose run backend python manage.py createsuperuser
4. **Затем создаем миграции и запускаем их**:
   ```bash
   docker-compose exec backend python manage.py makemigrations
   docker-compose exec backend python manage.py migrate
5. **Затем загружаем ингредиенты командой**:
   ```bash
   docker-compose exec backend python manage.py load_ingredients --path data/ingredients.csv   
6. **Можно заргузить тестовых users и recipes:**:
   ```bash
   docker-compose exec backend python manage.py load_recipes --path data/users.json
   docker-compose exec backend python manage.py load_recipes --path data/recipes.json
   
### Доступные адреса
После успешного запуска приложение будет доступно по следующим адресам:

Режим	Адрес	Описание
DEBUG	http://localhost:8000	Главная страница
DEBUG	http://localhost:8000/api	API
DEBUG	http://localhost:8000/admin	Панель администратора
DEBUG	http://localhost:8000/api/docs	Документация API
Docker	http://localhost	Главная страница
Docker	http://localhost/admin	Панель администратора
Docker	http://localhost/api/docs	Документация API

### Для тестирования API рекомендуется использовать Postman. Важные замечания:

- Перед началом тестирования убедитесь, что в базе нет пользователей, созданных предыдущими тестами

- Для повторного тестирования:

 -- Удалите тестовых пользователей через админ-панель

 -- Или очистите базу данных полностью

