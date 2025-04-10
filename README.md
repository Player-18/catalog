# catalog
1) Поднимаем базу в докере docker compose up db
2) Запускаем бэк локально uvicorn app.main:app --host 0.0.0.0 --port 8000
3) Необходимо накатить тестовую базу для этого в swagger дернуть запрос load-test-data