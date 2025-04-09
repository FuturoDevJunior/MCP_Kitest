from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MCP Test Assistant"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = """
    API para auxiliar desenvolvedores na criação de testes unitários de qualidade.
    Fornece análise, geração e validação de testes seguindo as melhores práticas.
    """

    # Configurações de segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Configurações de teste
    TEST_FRAMEWORKS: list[str] = ["pytest", "unittest"]
    MAX_CODE_SIZE: int = 1000000  # 1MB
    DEFAULT_TEST_TEMPLATE: str = "pytest"

    class Config:
        case_sensitive = True


settings = Settings()
