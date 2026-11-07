import httpx
import pytest

from backend import llm


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setattr(llm, "LLM_PROVIDER", "anthropic")
    with pytest.raises(llm.LLMError):
        llm.resolve_provider()
    text = llm.complete("system", "user", provider="anthropic")
    assert text.startswith("AI generation temporarily unavailable")
    assert "anthropic" in text


def test_openai_missing_key(monkeypatch):
    monkeypatch.setattr(llm, "OPENAI_API_KEY", "")
    text = llm.complete("system", "user", provider="openai")
    assert "OPENAI_API_KEY" in text


def test_openai_complete_uses_the_client(monkeypatch):
    monkeypatch.setattr(llm, "OPENAI_API_KEY", "test-key")

    class FakeMessage:
        content = "Grounded reply"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["model"]
            assert kwargs["temperature"] == llm.LIVE_TEMPERATURE
            return FakeResponse()

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "test-key"
            self.chat = FakeChat()

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    assert llm.complete("system", "user", provider="openai") == "Grounded reply"


def test_openai_stream_yields_tokens(monkeypatch):
    monkeypatch.setattr(llm, "OPENAI_API_KEY", "test-key")

    class Delta:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, content):
            self.delta = Delta(content)

    class Chunk:
        def __init__(self, content):
            self.choices = [Choice(content)]

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["stream"] is True
            return [Chunk("Hello "), Chunk(""), Chunk("doctor")]

    class FakeChat:
        completions = FakeCompletions()

    class FakeClient:
        def __init__(self, api_key):
            self.chat = FakeChat()

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    assert "".join(llm.stream_text("system", "user", provider="openai")) == "Hello doctor"


def test_ollama_connection_failure(monkeypatch):
    def boom(*_args, **_kwargs):
        raise httpx.ConnectError("refused")

    monkeypatch.setattr(httpx, "post", boom)
    text = llm.complete("system", "user", provider="ollama")
    assert "Could not reach Ollama" in text


def test_ollama_model_not_found(monkeypatch):
    class Response:
        status_code = 404
        reason_phrase = "Not Found"
        text = "model not found"

        def json(self):
            return {}

    monkeypatch.setattr(httpx, "post", lambda *_a, **_k: Response())
    text = llm.complete("system", "user", provider="ollama")
    assert "not found" in text.lower()


def test_ollama_complete_reads_message(monkeypatch):
    class Response:
        status_code = 200
        text = ""

        def json(self):
            return {"message": {"content": "Local reply"}}

    monkeypatch.setattr(httpx, "post", lambda *_a, **_k: Response())
    assert llm.complete("system", "user", provider="ollama") == "Local reply"


def test_default_provider_follows_the_environment(monkeypatch):
    monkeypatch.setattr(llm, "LLM_PROVIDER", "ollama")
    assert llm.resolve_provider() == "ollama"
    assert llm.resolve_provider("openai") == "openai"


def test_the_visit_uses_the_local_model_and_comparison_uses_gpt():
    assert llm.live_provider("twin") == "ollama"
    assert llm.live_provider("followup", "specialist") == "ollama"
    assert llm.live_provider("generic") == "openai"
    assert llm.live_provider("followup", "general") == "openai"
