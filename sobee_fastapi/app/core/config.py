from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sobee FastAPI"

    OPENAI_API_KEY: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "sobee_db"
    DB_USER: str = "root"
    DB_PASSWORD: str = "1234"

    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-northeast-2"
    S3_BUCKET_NAME: str = "sobee-prd-s3-media"

    csv_path: str = ""
    model_path: str = "ml/model.pkl"

    FASTAPI_BASE_URL: str = "http://localhost:8000"
    INTERNAL_SECRET_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()