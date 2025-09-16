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
- Path: `/projects`
- Description: Records a public key sharing event between team members
- Request body:
```json
{
  "project_name": "Aurora",
  "pub_key": "pk_live_xxx",
  "team_leader": "Ada Lovelace"
}
```
- **Field mapping**:
  - `project_name` → stored as `shared_to` and `project`
  - `team_leader` → stored as `shared_by`
  - `pub_key` → stored as `pub_key`
- Response `200 OK`:
```json
{
  "id": 1,
  "project_name": "Aurora",
  "pub_key": "pk_live_xxx",
  "team_leader": "Ada Lovelace"
}
```

#### cURL
```bash
curl -sS -X POST http://127.0.0.1:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"project_name":"Aurora","pub_key":"pk_live_xxx","team_leader":"Ada Lovelace"}' | jq .
```

### List/Filter Share Records
- Method: `GET`
- Path: `/projects`
- Description: Query key sharing records by project or sharer
- Query params (optional):
  - `project_name` (exact match on `project` field)
  - `team_leader` (exact match on `shared_by` field)
- Response `200 OK`:
```json
[
  {
    "id": 2,
    "project_name": "Aurora",
    "pub_key": "pk_live_yyy",
    "team_leader": "Ada Lovelace"
  }
]
```

#### cURL
```bash
# All share records
curl -sS "http://127.0.0.1:8000/projects" | jq .

# Filter by project name
curl -sS "http://127.0.0.1:8000/projects?project_name=Aurora" | jq .

# Filter by who shared the key
curl -sS "http://127.0.0.1:8000/projects?team_leader=Ada%20Lovelace" | jq .

# Filter by both
curl -sS "http://127.0.0.1:8000/projects?project_name=Aurora&team_leader=Ada%20Lovelace" | jq .
```

### Use Cases
- Track public key sharing between team members
- Audit who shared keys for which projects
- Query sharing history by project or team member

### Request/Response Types (Pseudocode)
```ts
// Request
interface ProjectCreate {
  project_name: string;
  pub_key: string;
  team_leader: string;
}

// Response
interface Project {
  id: number;
  project_name: string;
  pub_key: string;
  team_leader: string;
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
