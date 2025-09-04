import os
import json
import logging
import time
from typing import List
from google import genai
from dotenv import load_dotenv
from .prompts import PROMPT_TEMPLATES
from .schemas import Question, QuestionResponse

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