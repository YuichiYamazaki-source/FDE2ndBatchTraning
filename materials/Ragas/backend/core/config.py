from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    chroma_host: str = "localhost"
    chroma_port: int = 8000
    chroma_collection_name: str = "products"

    model_config = {"env_file": ".env"}


settings = Settings()
