@echo off
echo This application requires a PostgreSQL server running on localhost to load successfully.
set /p DB_USER=Enter database username:
set /p DB_PASS=Enter database password:
set /p DB_NAME=Enter database name:

set DB_CONNECTION_STRING=postgresql+psycopg2://%DB_USER%:%DB_PASS%@localhost:5432/%DB_NAME%
set FLASK_APP=app.py

python -c "import os; os.environ['DB_CONNECTION_STRING'] = '%DB_CONNECTION_STRING%'; import app"
pause
