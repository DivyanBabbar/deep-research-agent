from datetime import UTC, datetime

from fastapi.testclient import TestClient

from research_agent import api, storage
from research_agent.api import app
from research_agent.models import ResearchResponse, Source


def test_health_and_homepage(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "database_path", str(tmp_path / "research.db"))

    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        page = client.get("/")
        assert page.status_code == 200
        assert "Good questions" in page.text
        assert client.get("/static/app.js").status_code == 200


def test_research_detail_returns_not_found_for_unknown_run(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "database_path", str(tmp_path / "research.db"))

    with TestClient(app) as client:
        assert client.get("/research/missing").status_code == 404


def test_research_endpoint_returns_cited_results_without_provider_calls(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "database_path", str(tmp_path / "research.db"))
    expected = ResearchResponse(
        run_id="run-123",
        query="How do cities reduce urban heat?",
        report="Trees and cool roofs reduce heat [S1].",
        sources=[
            Source(
                id="S1",
                title="City climate plan",
                url="https://example.org/climate",
                content="Trees and reflective roofs cool neighborhoods.",
            )
        ],
        created_at=datetime.now(UTC),
    )
    monkeypatch.setattr(api, "conduct_research", lambda _request: expected)

    with TestClient(app) as client:
        response = client.post(
            "/research",
            json={"query": expected.query, "depth": "advanced", "max_results": 8},
        )

    assert response.status_code == 200
    assert response.json()["sources"][0]["id"] == "S1"
    assert response.json()["report"] == expected.report
