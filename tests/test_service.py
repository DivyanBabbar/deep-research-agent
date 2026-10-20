"""Provider-mocked tests for the research service; no credentials or network required."""

from types import SimpleNamespace

import pytest

from research_agent import service
from research_agent.models import ResearchRequest


class FakeSearch:
    def __init__(self, api_key: str):
        assert api_key == "search-test-key"

    def search(self, **kwargs):
        assert kwargs["query"] == "How do cities reduce urban heat?"
        return {
            "results": [
                {
                    "title": "City climate plan",
                    "url": "https://example.org/climate",
                    "content": "Trees and cool roofs lower surface temperatures.",
                    "score": 0.92,
                }
            ]
        }


class FakeOpenAI:
    def __init__(self, **kwargs):
        assert kwargs["api_key"] == "openai-test-key"

        class Responses:
            @staticmethod
            def create(**_kwargs):
                return SimpleNamespace(output_text="Cities use shade and cool roofs [S1].")

        self.responses = Responses()


def test_research_uses_sources_and_persists_result(monkeypatch):
    saved = []
    monkeypatch.setattr(service.settings, "tavily_api_key", "search-test-key")
    monkeypatch.setattr(service.settings, "openai_api_key", "openai-test-key")
    monkeypatch.setattr(service, "TavilyClient", FakeSearch)
    monkeypatch.setattr(service, "OpenAI", FakeOpenAI)
    monkeypatch.setattr(service, "save_run", saved.append)

    result = service.conduct_research(ResearchRequest(query="How do cities reduce urban heat?"))

    assert result.report.endswith("[S1].")
    assert str(result.sources[0].url) == "https://example.org/climate"
    assert result.run_id
    assert saved == [result]


def test_research_requires_search_key(monkeypatch):
    monkeypatch.setattr(service.settings, "tavily_api_key", "")
    monkeypatch.setattr(service.settings, "openai_api_key", "openai-test-key")

    with pytest.raises(service.ConfigurationError, match="TAVILY_API_KEY"):
        service.conduct_research(ResearchRequest(query="How do cities reduce urban heat?"))
