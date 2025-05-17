from pydantic_settings import BaseSettings

SQLITE_DB_FILE = "./test_database.db"

class Settings(BaseSettings):
    DATABASE_URL: str = f"sqlite+pysqlite:///{SQLITE_DB_FILE}"

    LOW_STOCK_THRESHOLD: int = 10 

settings = Settings()
