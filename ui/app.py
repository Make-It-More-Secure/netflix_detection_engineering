from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import text
from detect.db import get_engine
from detect.rule_loader import load_rules

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Detection Lab UI")

static_dir = BASE_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


@app.get("/rules", response_class=HTMLResponse)
def list_rules(request: Request):
    rules_dir = PROJECT_ROOT / "detections" / "rules"
    rules = load_rules(rules_dir)
    return templates.TemplateResponse("rules.html", {"request": request, "rules": rules})


@app.get("/alerts", response_class=HTMLResponse)
def list_alerts(request: Request, rule_id: str | None = None):
    engine = get_engine()
    query = "select * from alerts order by created_at desc limit 200"
    params = {}
    if rule_id:
        query = "select * from alerts where rule_id = :rule_id order by created_at desc limit 200"
        params = {"rule_id": rule_id}

    with engine.begin() as conn:
        rows = conn.execute(text(query), params).mappings().all()

    return templates.TemplateResponse("alerts.html", {"request": request, "alerts": rows, "rule_id": rule_id})


@app.get("/alerts/{alert_id}", response_class=HTMLResponse)
def alert_detail(request: Request, alert_id: str):
    engine = get_engine()
    with engine.begin() as conn:
        row = conn.execute(
            text("select * from alerts where id = :id"),
            {"id": alert_id},
        ).mappings().first()
    if not row:
        # simple 404
        return HTMLResponse("Alert not found", status_code=404)

    return templates.TemplateResponse("alert_detail.html", {"request": request, "alert": row})
