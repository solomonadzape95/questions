# Share Records API – Store and Query Key Sharing Records

### Environment (Database)
- Provide one of:
  - `POSTGRES_DSN=postgresql://user:pass@host:5432/dbname`
  - or all of: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- Table `share_records` is auto-created on startup if missing.

### Database Schema
```sql
CREATE TABLE share_records (
    id SERIAL PRIMARY KEY,
    pub_key TEXT NOT NULL,
    shared_by TEXT NOT NULL,    -- who shared the key
    shared_to TEXT NOT NULL,    -- who received the key  
    project TEXT NOT NULL,      -- project name
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Create Share Record
- Method: `POST`
- Path: `/share-records`
- Description: Records a public key sharing event between team members
- Request body:
```json
{
  "shared_by": "Ada Lovelace",
  "shared_to": "Bob Smith",
  "pub_key": "pk_live_xxx",
  "project": "Aurora"
}
```
- Response `200 OK`:
```json
{
  "id": 1,
  "shared_by": "Ada Lovelace",
  "shared_to": "Bob Smith",
  "pub_key": "pk_live_xxx",
  "project": "Aurora"
}
```

#### cURL
```bash
curl -sS -X POST http://127.0.0.1:8000/share-records \
  -H 'Content-Type: application/json' \
  -d '{"shared_by":"Ada Lovelace","shared_to":"Bob Smith","pub_key":"pk_live_xxx","project":"Aurora"}' | jq .
```

### List/Filter Share Records
- Method: `GET`
- Path: `/share-records`
- Description: Query key sharing records by project or sharer
- Query params (optional):
  - `project` (exact match on `project` field)
  - `shared_by` (exact match on `shared_by` field)
- Response `200 OK`:
```json
[
  {
    "id": 2,
    "shared_by": "Ada Lovelace",
    "shared_to": "Bob Smith",
    "pub_key": "pk_live_yyy",
    "project": "Aurora"
  }
]
```

#### cURL
```bash
# All share records
curl -sS "http://127.0.0.1:8000/share-records" | jq .

# Filter by project
curl -sS "http://127.0.0.1:8000/share-records?project=Aurora" | jq .

# Filter by who shared the key
curl -sS "http://127.0.0.1:8000/share-records?shared_by=Ada%20Lovelace" | jq .

# Filter by both
curl -sS "http://127.0.0.1:8000/share-records?project=Aurora&shared_by=Ada%20Lovelace" | jq .
```

### Use Cases
- Track public key sharing between team members
- Audit who shared keys for which projects
- Query sharing history by project or team member

### Request/Response Types (Pseudocode)
```ts
// Request
interface ShareRecordCreate {
  shared_by: string;
  shared_to: string;
  pub_key: string;
  project: string;
}

// Response
interface ShareRecord {
  id: number;
  shared_by: string;
  shared_to: string;
  pub_key: string;
  project: string;
}
```

### Error Responses
- `400/422` (Validation): Invalid or missing fields
- `500` (Server): Database or internal error
- Body example:
```json
{
  "detail": "<error message>"
}
```
