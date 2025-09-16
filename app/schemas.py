# app/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

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


# Projects API
class ProjectCreate(BaseModel):
    project_name: str = Field(..., min_length=1)
    pub_key: str = Field(..., min_length=1)
    team_leader: str = Field(..., min_length=1)

class Project(BaseModel):
    id: int
    project_name: str
    pub_key: str
    team_leader: str
