from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Protein Embedding Workbench API"
    env: str = "local"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ]
    cache_dir: str = "../data/cache"
    embedding_backend: str = "hash"  # hash | esm
    embedding_model_name: str = "facebook/esm2_t6_8M_UR50D"
    embedding_cache_path: str = "data/embedding_cache.sqlite"
    enable_embedding_cache: bool = True

settings = Settings()
