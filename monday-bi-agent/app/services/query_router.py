from __future__ import annotations

import json
from openai import OpenAI

from app.config import settings
from app.models import RoutedQuery
from app.prompts import ROUTER_SYSTEM_PROMPT


client = OpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)


def route_query(question: str) -> RoutedQuery:
    response = client.chat.completions.create(
        model=settings.llm_model,
        messages=[
            {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)
    return RoutedQuery(**data)