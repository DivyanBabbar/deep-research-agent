import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from research_agent.config import settings
from research_agent.models import HistoryItem, ResearchRequest, ResearchResponse
from research_agent.service import ConfigurationError, conduct_research
from research_agent.storage import get_run, initialize_database, list_runs

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
ASSET_DIR = Path(__file__).parent


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(
    title=settings.app_name,
    summary="Web research with source-grounded synthesis and traceable citations.",
    description=(
        "Search the web, synthesize evidence into a cited report, and retain a local history "
        "of completed research runs."
    ),
    version="1.0.0",
    contact={"name": "Project maintainers"},
    license_info={"name": "MIT"},
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=ASSET_DIR / "static"), name="static")
templates = Jinja2Templates(directory=ASSET_DIR / "templates")


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"history": list_runs(8)},
    )


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/history", response_model=list[HistoryItem], tags=["research"])
def history(limit: int = Query(default=20, ge=1, le=100)) -> list[HistoryItem]:
    return list_runs(limit)


@app.get("/research/{run_id}", response_model=ResearchResponse, tags=["research"])
def research_detail(run_id: str) -> ResearchResponse:
    result = get_run(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Research run not found.")
    return result


@app.post("/research", response_model=ResearchResponse, tags=["research"])
def research(request: ResearchRequest) -> ResearchResponse:
    try:
        return conduct_research(request)
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        logging.getLogger(__name__).exception("Research request failed")
        raise HTTPException(
            status_code=502,
            detail="Research provider failed. Check server logs and provider status.",
        ) from exc
