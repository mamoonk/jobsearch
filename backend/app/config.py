from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str = "jobsearch"
    postgres_password: str = "changeme"
    postgres_db: str = "jobsearch"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_host: str = "localhost"
    redis_port: int = 6379

    jwt_secret: str = "change-this-secret"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    openai_api_key: str = ""
    geoapify_api_key: str = ""
    theirstack_api_key: str = ""
    serpapi_api_key: str = ""

    backend_cors_origins: str = "http://localhost:3000"
    backend_port: int = 8000

    rate_limit_requests_per_minute: int = 5

    # S3 / Cloud storage
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    s3_bucket: str = "jobsearch-resumes"
    s3_region: str = "us-east-1"
    s3_endpoint: str = ""

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
