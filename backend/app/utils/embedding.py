from typing import List, Optional

import openai

from app.config import settings

_client: Optional[openai.OpenAI] = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_text_embedding(content_string: str) -> List[float]:
    if not settings.openai_api_key:
        return [0.0] * 1536

    clean_string = content_string.replace("\n", " ")
    client = _get_client()
    response = client.embeddings.create(
        input=[clean_string],
        model="text-embedding-3-small",
    )
    return response.data[0].embedding
