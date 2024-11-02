from os import getenv
from dotenv import load_dotenv

load_dotenv()
database_name = getenv("DATABASE_NAME")


database_url = f"sqlite:///database/{database_name}"
test_db_url = "sqlite:///database/testing_db"
