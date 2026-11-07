"""Chat providers. OpenAI is the default. Ollama is a local open-source model.

Live consultations use temperature 0.2, the same setting as before.
The held-out experiment, when it is run, uses temperature 0.
"""

from __future__ import annotations

from typing import Iterator, Optional

import httpx

from config import LLM_PROVIDER, OLLAMA_BASE_URL, OLLAMA_MODEL, OPENAI_API_KEY, OPENAI_MODEL

PROVIDERS = ("openai", "ollama")
LIVE_TEMPERATURE = 0.2
OLLAMA_TIMEOUT = 90.0


class LLMError(Exception):
    pass


def resolve_provider(override: Optional[str] = None) -> str:
    name = (override or LLM_PROVIDER or "openai").strip().lower()
    if name not in PROVIDERS:
        raise LLMError(f"Unknown LLM provider '{name}'. Use openai or ollama.")
    return name


def active_model(provider: Optional[str] = None) -> str:
    name = resolve_provider(provider)
    return OPENAI_MODEL if name == "openai" else OLLAMA_MODEL


def live_provider(kind: str, mode: str = "general") -> str:
    """The Vimlesh visit uses the local model. The plain comparison answer uses GPT."""
    if kind == "twin" or (kind == "followup" and mode == "specialist"):
        return "ollama"
    return "openai"


def _unavailable(detail: str) -> str:
    return f"AI generation temporarily unavailable: {detail}"


def complete(system_prompt: str, user_prompt: str, provider: Optional[str] = None, temperature: float = LIVE_TEMPERATURE) -> str:
    try:
        name = resolve_provider(provider)
    except LLMError as exc:
        return _unavailable(str(exc))
    try:
        if name == "ollama":
            return _ollama_complete(system_prompt, user_prompt, temperature)
        return _openai_complete(system_prompt, user_prompt, temperature)
    except LLMError as exc:
        return _unavailable(str(exc))
    except Exception as exc:
        return _unavailable(str(exc))


def stream_text(system_prompt: str, user_prompt: str, provider: Optional[str] = None, temperature: float = LIVE_TEMPERATURE) -> Iterator[str]:
    try:
        name = resolve_provider(provider)
    except LLMError as exc:
        yield _unavailable(str(exc))
        return
    try:
        if name == "ollama":
            yield from _ollama_stream(system_prompt, user_prompt, temperature)
            return
        yield from _openai_stream(system_prompt, user_prompt, temperature)
    except LLMError as exc:
        yield _unavailable(str(exc))
    except Exception as exc:
        yield _unavailable(str(exc))


def _openai_complete(system_prompt: str, user_prompt: str, temperature: float) -> str:
    if not OPENAI_API_KEY:
        raise LLMError("OpenAI API key not configured. Add OPENAI_API_KEY in .env.")
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    return response.choices[0].message.content or ""


def _openai_stream(system_prompt: str, user_prompt: str, temperature: float) -> Iterator[str]:
    if not OPENAI_API_KEY:
        raise LLMError("OpenAI API key not configured. Add OPENAI_API_KEY in .env.")
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    stream = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=temperature,
        stream=True,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content
        if text:
            yield text


def _ollama_messages(system_prompt: str, user_prompt: str) -> list[dict]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]


def _raise_for_ollama(response: httpx.Response) -> None:
    if response.status_code == 404:
        raise LLMError(f"Ollama model '{OLLAMA_MODEL}' was not found at {OLLAMA_BASE_URL}. Pull it with: ollama pull {OLLAMA_MODEL}")
    if response.status_code >= 400:
        detail = response.text.strip()[:300] or response.reason_phrase
        raise LLMError(f"Ollama returned {response.status_code}: {detail}")


def _ollama_complete(system_prompt: str, user_prompt: str, temperature: float) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": _ollama_messages(system_prompt, user_prompt),
        "options": {"temperature": temperature},
    }
    try:
        response = httpx.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT)
    except httpx.ConnectError as exc:
        raise LLMError(f"Could not reach Ollama at {OLLAMA_BASE_URL}. Start it with: ollama serve") from exc
    except httpx.TimeoutException as exc:
        raise LLMError(f"Ollama timed out after {int(OLLAMA_TIMEOUT)} seconds.") from exc
    _raise_for_ollama(response)
    body = response.json()
    message = body.get("message") or {}
    return str(message.get("content") or "")


def _ollama_stream(system_prompt: str, user_prompt: str, temperature: float) -> Iterator[str]:
    payload = {
        "model": OLLAMA_MODEL,
        "stream": True,
        "messages": _ollama_messages(system_prompt, user_prompt),
        "options": {"temperature": temperature},
    }
    try:
        with httpx.stream("POST", f"{OLLAMA_BASE_URL}/api/chat", json=payload, timeout=OLLAMA_TIMEOUT) as response:
            if response.status_code >= 400:
                response.read()
                _raise_for_ollama(response)
            for line in response.iter_lines():
                if not line:
                    continue
                import json

                body = json.loads(line)
                if body.get("error"):
                    raise LLMError(str(body["error"]))
                piece = ((body.get("message") or {}).get("content")) or ""
                if piece:
                    yield piece
    except httpx.ConnectError as exc:
        raise LLMError(f"Could not reach Ollama at {OLLAMA_BASE_URL}. Start it with: ollama serve") from exc
    except httpx.TimeoutException as exc:
        raise LLMError(f"Ollama timed out after {int(OLLAMA_TIMEOUT)} seconds.") from exc
