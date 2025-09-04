# app/schemas.py
from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    category: str
    num_questions: int = 10

class Question(BaseModel):
    question: str
    options: List[str]
    answer: str

class QuestionResponse(BaseModel):
    category: str
    questions: List[Question]
