from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_postgres_user: str
    db_postgres_password: str
    db_postgres_host: str
    db_postgres_name: str
    db_postgres_port: int = 5432

    r2_endpoint: str
    r2_storage_bucket: str
    r2_access_key_id: str
    r2_secret_access_key: str

    class Config:
        env_file = ".env"


settings = Settings()
