from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Sobee FastAPI"
    OPENAI_API_KEY: str = ""
    MYSQL_URL: str = ""
    
    # 추가할 필드들
    db_host: str = "127.0.0.1"
    db_port: str = "3306"
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "wonpick"
    csv_path: str = ""
    model_path: str = "ml/model.pkl"

    class Config:
        env_file = ".env"
        extra = "ignore"    

settings = Settings()