from os import getenv
from dotenv import load_dotenv


load_dotenv()
user = getenv("USER")
password = getenv("PASSWORD")
database_name = getenv("DATABASE_NAME")


database_url = f"postgresql://{user}:{password}@localhost/{database_name}"
