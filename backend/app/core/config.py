from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    port: int
    aws_access_key_id: str
    aws_bucket_name: str
    aws_region: str
    aws_secret_access_key: str

    # Google OAuth
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str


    class Config:
        env_file = ".env"

settings = Settings()