## Questions API – Integration Guide

### Base URL
- Local: `http://127.0.0.1:8000`

### Health Check
- Method: `GET`
- Path: `/health`
- Response: `200 OK`
```json
{
  "message": "api healthy, ok",
  "status": "200"
}
```

### Generate Questions
- Method: `POST`
- Path: `/generate`
- Description: Generates multiple-choice questions for a given category.
- Request `Content-Type`: `application/json`
- Request body:
```json
{
  "category": "applied_math",
  "num_questions": 5
}
```

#### Categories
- `applied_math`
- `statistics`
- `verbal_reasoning`
- `general_knowledge`
- `specialized`

#### Successful Response
- Status: `200 OK`
- Body:
```json
{
  "category": "applied_math",
  "questions": [
    {
      "question": "What is the derivative of x^2?",
      "options": ["x", "2x", "x^3", "2"],
      "answer": "2x"
    }
  ]
}
```

#### Error Responses
- `400/422` (Validation): Invalid or missing fields
- `500` (Server): Model or internal error
- Body example:
```json
{
  "detail": "<error message>"
}
```

### cURL Examples
```bash
# Health
curl -sS http://127.0.0.1:8000/health | jq .

# Generate 5 Applied Math questions
curl -sS -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{"category":"applied_math","num_questions":5}' | jq .
```

### Request/Response Types (Pseudocode)
```ts
// Request
interface QuestionRequest {
  category: 'applied_math' | 'statistics' | 'verbal_reasoning' | 'general_knowledge' | 'specialized';
  num_questions?: number; // default 10
}

// Response
interface QuestionResponse {
  category: string;
  questions: Question[];
}

interface Question {
  question: string;
  options: string[]; // length = 4
  answer: string;    // must be one of options
}
```

### OpenAPI/Swagger
- Interactive docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

### Environment
- Requires `GEMINI_API_KEY` to be set (e.g., via `.env`).



