from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # "openrouter" = cascade multi-model via OpenRouter (default)
    # "trocr"      = local Microsoft TrOCR model (requires torch + transformers)
    ocr_backend: str = "openrouter"

    # Cascade confidence thresholds (0.0–1.0)
    # If a free model scores below ocr_free_threshold, the next free model is tried.
    # If all free models score below ocr_free_threshold, Claude Haiku is used.
    # If Haiku scores below ocr_haiku_threshold, Claude Sonnet (final) is used.
    ocr_free_threshold: float = 0.70
    ocr_haiku_threshold: float = 0.82

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
