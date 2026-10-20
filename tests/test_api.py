from fastapi.testclient import TestClient

from research_agent import storage
from research_agent.api import app


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
