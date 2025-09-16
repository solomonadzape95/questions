import os
import json
import logging
import time
from typing import List, Optional
import psycopg
from google import genai
from dotenv import load_dotenv
from .prompts import PROMPT_TEMPLATES
from .schemas import Question, QuestionResponse, ShareRecord, ShareRecordCreate

load_dotenv()
#load gemini api key and start a client
api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)
logger = logging.getLogger("questions.service")

async def generate_questions(category:str, n:int = 10):
    if category not in PROMPT_TEMPLATES:
        raise ValueError("Invalid Category")

    prompt = PROMPT_TEMPLATES[category].format(n=n, category=category)
    
    logger.info("gen.start category=%s requested=%s", category, n)
    start = time.perf_counter()

    # Ask model to return JSON that matches our Pydantic schema
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": QuestionResponse,
        },
    )

    model_latency_ms = int((time.perf_counter() - start) * 1000)
    logger.info("gen.model_response category=%s latency_ms=%s", category, model_latency_ms)

    # If the SDK parsed into a Pydantic model, return it as a dict
    if hasattr(response, "parsed") and isinstance(response.parsed, QuestionResponse):
        data = response.parsed.model_dump()
        # Ensure category is set (model might omit it); fall back to input
        if not data.get("category"):
            data["category"] = category
        logger.info(
            "gen.parsed_success category=%s questions=%s",
            category,
            len(data.get("questions", [])) if isinstance(data, dict) else "-",
        )
        return data

    # Fallback: try to parse JSON text
    try:
        parsed_text = getattr(response, "text", "")
        data = json.loads(parsed_text)
        if "category" not in data:
            data["category"] = category
        logger.info(
            "gen.json_success category=%s questions=%s",
            category,
            len(data.get("questions", [])) if isinstance(data, dict) else "-",
        )
        return data
    except Exception as exc:
        logger.exception("gen.parse_error category=%s error=%s", category, str(exc))
        # Last resort: wrap raw text
        return {"category": category, "questions": [], "raw": getattr(response, "text", "")}


# =====================
# Postgres Integration
# =====================

def _get_dsn() -> str:
    dsn = os.getenv("POSTGRES_DSN")
    if dsn:
        return dsn
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db = os.getenv("POSTGRES_DB", "postgres")
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"


def init_projects_table() -> None:
    """Create share_records table if it does not exist."""
    dsn = _get_dsn()
    logger.info("db.init dsn_host=%s", os.getenv("POSTGRES_HOST", "env_dsn"))
    create_sql = (
        """
        CREATE TABLE IF NOT EXISTS share_records (
            id SERIAL PRIMARY KEY,
            pub_key TEXT NOT NULL,
            shared_by TEXT NOT NULL,
            shared_to TEXT NOT NULL,
            project TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
    )
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(create_sql)
        conn.commit()
    logger.info("db.init_done")


def insert_share_record(payload: ShareRecordCreate) -> ShareRecord:
    dsn = _get_dsn()
    insert_sql = (
        """
        INSERT INTO share_records (pub_key, shared_by, shared_to, project)
        VALUES (%s, %s, %s, %s)
        RETURNING id, pub_key, shared_by, shared_to, project;
        """
    )
    logger.info("db.insert_share_record shared_by=%s shared_to=%s project=%s", payload.shared_by, payload.shared_to, payload.project)
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                insert_sql,
                (payload.pub_key, payload.shared_by, payload.shared_to, payload.project),
            )
            row = cur.fetchone()
        conn.commit()
    share_record = ShareRecord(id=row[0], shared_by=row[2], shared_to=row[3], pub_key=row[1], project=row[4])
    logger.info("db.insert_share_record_success id=%s", share_record.id)
    return share_record


def find_share_records(project: Optional[str] = None, shared_by: Optional[str] = None) -> list[ShareRecord]:
    dsn = _get_dsn()
    where_clauses = []
    params: list = []
    if project:
        where_clauses.append("project = %s")
        params.append(project)
    if shared_by:
        where_clauses.append("shared_by = %s")
        params.append(shared_by)
    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    query = (
        "SELECT id, pub_key, shared_by, shared_to, project FROM share_records" + where_sql + " ORDER BY id DESC"
    )
    logger.info("db.find_share_records project=%s shared_by=%s", project or "*", shared_by or "*")
    results: list[ShareRecord] = []
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params if params else None)
            for row in cur.fetchall():
                results.append(
                    ShareRecord(id=row[0], shared_by=row[2], shared_to=row[3], pub_key=row[1], project=row[4])
                )
    logger.info("db.find_share_records_success count=%s", len(results))
    return results