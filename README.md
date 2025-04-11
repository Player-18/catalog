# catalog
1) Поднимаем базу в докере docker compose up db
2) Создаем в корне проекта .env из .env.example
3) Запускаем бэк локально uvicorn app.main:app --host 0.0.0.0 --port 8000
4) Выполняем команду alembic upgrade head для создания миграций
5) Необходимо накатить тестовую базу для этого в swagger дернуть запрос load-test-data