# app/main.py
import logging
import time
from fastapi import FastAPI, HTTPException, Request
from .schemas import QuestionRequest, QuestionResponse, ProjectCreate, Project
from .services import generate_questions, init_projects_table, insert_project, find_projects

app = FastAPI()

logger = logging.getLogger("questions.api")
logging.basicConfig(level=logging.INFO)

@app.on_event("startup")
async def on_startup():
    logger.info("API startup complete")
    # Ensure DB is ready (no-op if already created)
    try:
        init_projects_table()
    except Exception as exc:
        logger.exception("db.init_failed error=%s", str(exc))

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    logger.info(
        "request.start method=%s path=%s client=%s",
        request.method,
        request.url.path,
        request.client.host if request.client else "-",
    )
    try:
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.info(
            "request.end method=%s path=%s status=%s duration_ms=%s",
            request.method,
            request.url.path,
            getattr(response, "status_code", "-"),
            duration_ms,
        )
        return response
    except Exception as exc:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.exception(
            "request.error method=%s path=%s duration_ms=%s error=%s",
            request.method,
            request.url.path,
            duration_ms,
            str(exc),
        )
        raise

@app.post("/generate", response_model=QuestionResponse)
async def generate(request: QuestionRequest):
    try:
        logger.info(
            "generate.called category=%s num_questions=%s",
            request.category,
            request.num_questions,
        )
        result = await generate_questions(request.category, request.num_questions)
        try:
            num_q = len(result.get("questions", [])) if isinstance(result, dict) else "-"
        except Exception:
            num_q = "-"
        logger.info(
            "generate.success category=%s num_questions=%s returned=%s",
            request.category,
            request.num_questions,
            num_q,
        )
        return result
    except Exception as e:
        logger.exception(
            "generate.error category=%s num_questions=%s error=%s",
            request.category,
            request.num_questions,
            str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"message": "api healthy, ok", "status":"200"}


@app.post("/projects", response_model=Project)
async def create_project(body: ProjectCreate):
    try:
        logger.info(
            "projects.create called name=%s leader=%s",
            body.project_name,
            body.team_leader,
        )
        project = insert_project(body)
        logger.info("projects.create success id=%s", project.id)
        return project
    except Exception as exc:
        logger.exception("projects.create error=%s", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/projects", response_model=list[Project])
async def list_projects(project_name: str | None = None, team_leader: str | None = None):
    try:
        logger.info("projects.list called name=%s leader=%s", project_name or "*", team_leader or "*")
        results = find_projects(project_name=project_name, team_leader=team_leader)
        logger.info("projects.list success count=%s", len(results))
        return results
    except Exception as exc:
        logger.exception("projects.list error=%s", str(exc))
        raise HTTPException(status_code=500, detail=str(exc))
