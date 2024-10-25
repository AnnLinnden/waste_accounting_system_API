from fastapi import FastAPI
import database.sql_models as sql

app = FastAPI()


@app.on_event("startup")  # при запуске приложения
def on_startup():
    sql.create_tables()

