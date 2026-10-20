from datetime import UTC, datetime

from research_agent import storage
from research_agent.models import ResearchResponse, Source


def test_saved_runs_can_be_listed_and_retrieved(tmp_path, monkeypatch):
    monkeypatch.setattr(storage.settings, "database_path", str(tmp_path / "research.db"))
    storage.initialize_database()
    expected = ResearchResponse(
        run_id="run-123",
        query="How do cities reduce urban heat?",
        report="Trees reduce heat [S1].",
        sources=[
            Source(
                id="S1",
                title="City climate plan",
                url="https://example.org/climate",
                content="Trees and cool roofs lower surface temperatures.",
                score=0.92,
            )
        ],
        created_at=datetime.now(UTC),
    )

    storage.save_run(expected)

    assert storage.get_run(expected.run_id) == expected
    assert storage.list_runs(1)[0].run_id == expected.run_id
    assert storage.list_runs(1)[0].source_count == 1
