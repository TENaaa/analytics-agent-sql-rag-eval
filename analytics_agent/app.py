from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from .agent import answer_question, llm_mode
from .catalog import source_status
from .config import PROJECT_ROOT, REPORT_DIR
from .evaluation import run_eval


app = FastAPI(title="Analytics Agent SQL RAG Eval")
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "web" / "templates"))
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "web" / "static")), name="static")
REPORT_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/reports", StaticFiles(directory=str(REPORT_DIR)), name="reports")


class AskRequest(BaseModel):
    question: str


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request, "sources": source_status(), "llm_mode": llm_mode()})


@app.get("/api/sources")
def api_sources() -> list[dict[str, object]]:
    return source_status()


@app.post("/api/ask")
def api_ask(payload: AskRequest) -> dict[str, object]:
    answer = answer_question(payload.question)
    return answer.__dict__


@app.post("/api/eval")
def api_eval() -> dict[str, object]:
    return run_eval()
