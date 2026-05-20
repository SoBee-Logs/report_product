from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sobee FastAPI"
    GEMINI_API_KEY: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "sobee_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "1234"

    class Config:
        env_file = ".env"

settings = Settings()