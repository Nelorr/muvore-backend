from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_MINUTES: int=60

    class Config:
        env_file = ".env"
    
settings = Settings()