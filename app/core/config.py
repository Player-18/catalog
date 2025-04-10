from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASS: str

    class Config:
        env_file = ".env"


    def get_database_url(self) -> str:
        """Получить ссылку на базу."""
        user = self.DB_USER
        name = self.DB_NAME
        password = self.DB_PASS
        host = self.DB_HOST
        port = self.DB_PORT

        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

        return url


settings = Settings()