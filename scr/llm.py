import os
from pathlib import Path
from typing import Protocol

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError
from httpx import TransportError
from pydantic import BaseModel

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


class LLMError(RuntimeError):
    """Falha ao consultar o provedor ou receber uma resposta útil."""


class LLM(Protocol):
    """Operações que o agente espera de qualquer provedor de modelo."""

    def generate_text(self, message: str) -> str: ...

    def generate_structured_text(self, message: str, schema: type[BaseModel]) -> str: ...


class GeminiLLM:
    """Implementação do contrato LLM usando o Gemini."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "replace_with_your_api_key":
            raise RuntimeError("Configure GEMINI_API_KEY no arquivo .env do projeto.")

        self._client = genai.Client(api_key=api_key)
        self._model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def _generate(self, message: str, config: types.GenerateContentConfig | None = None) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=message,
                config=config,
            )
        except (APIError, TransportError) as error:
            raise LLMError("Não foi possível consultar o Gemini agora.") from error

        if not response.text:
            raise LLMError("O Gemini não retornou texto.")
        return response.text

    def generate_text(self, message: str) -> str:
        """Envia uma mensagem ao Gemini e devolve o texto da resposta."""
        return self._generate(message)

    def generate_structured_text(self, message: str, schema: type[BaseModel]) -> str:
        """Pede ao Gemini uma resposta JSON conforme o esquema informado."""
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
        )
        return self._generate(message, config)


if __name__ == "__main__":
    llm = GeminiLLM()
    print(llm.generate_text("Responda em português com uma saudação curta para um cliente."))
