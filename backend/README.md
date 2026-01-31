# Inventix AI Backend - Phase 1

## Overview

Minimal, honest backend for Inventix AI that provides:
- **Project CRUD** - Create, read, update, delete projects
- **File Upload** - Store PDF/DOCX files on disk
- **Data Persistence** - SQLite database survives restarts
- **Honest State Tracking** - No fake AI claims or progress

### What This Backend Does NOT Do (by design)
- ❌ No AI/LLM integration
- ❌ No document parsing or text extraction
- ❌ No novelty scoring or similarity detection
- ❌ No multi-agent orchestration
- ❌ No fake percentages or progress

---

## Quick Start

### 1. Install Dependencies
```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Run the Server
```bash
python -m uvicorn main:app --reload --port 8000
```

### 3. Open API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## API Endpoints

### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/projects` | Create a new project |
| `GET` | `/api/projects` | List all projects |
| `GET` | `/api/projects/{id}` | Get project details + analysis state |
| `PUT` | `/api/projects/{id}` | Update project |
| `DELETE` | `/api/projects/{id}` | Delete project and files |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/projects/{id}/files` | Upload file (PDF, DOCX, TXT) |
| `GET` | `/api/projects/{id}/files` | List project files |
| `DELETE` | `/api/projects/{id}/files/{file_id}` | Delete a file |
| `GET` | `/api/files/{file_id}/download` | Download file |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/api/system/status` | Phase 1 status and limitations |

---

## Example Requests

### Create Project
```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Drone Navigation AI",
    "type": "RESEARCH",
    "description": "Autonomous navigation using ML",
    "idea_text": "Using neural networks for obstacle avoidance",
    "domain": "AI"
  }'
```

### Upload File
```bash
curl -X POST http://localhost:8000/api/projects/1/files \
  -F "file=@/path/to/document.pdf"
```

### Get Project with State
```bash
curl http://localhost:8000/api/projects/1
```

Response:
```json
{
  "id": 1,
  "name": "Drone Navigation AI",
  "type": "RESEARCH",
  "description": "Autonomous navigation using ML",
  "idea_text": "Using neural networks...",
  "domain": "AI",
  "created_at": "2026-01-31T13:00:00",
  "updated_at": "2026-01-31T13:00:00",
  "files": [],
  "analysis_state": {
    "id": 1,
    "project_id": 1,
    "idea_received": true,
    "files_uploaded": false,
    "analysis_status": "NOT_STARTED",
    "notes": "AI analysis not implemented. Phase 1 provides data persistence only.",
    "updated_at": "2026-01-31T13:00:00"
  }
}
```

---

## Database Schema

SQLite database (`inventix.db`) with tables:

- **projects** - Core project entities
- **files** - Uploaded file metadata
- **analysis_states** - Honest state tracking

---

## Frontend Integration

Replace mock data in the React frontend with API calls:

### Replace WorkflowContext.jsx
```javascript
// Instead of:
const [projects, setProjects] = useState([...mockData]);

// Use:
const [projects, setProjects] = useState([]);

useEffect(() => {
  fetch('http://localhost:8000/api/projects')
    .then(res => res.json())
    .then(data => setProjects(data.projects));
}, []);
```

### Replace mock file upload
```javascript
const uploadFile = async (projectId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(
    `http://localhost:8000/api/projects/${projectId}/files`,
    { method: 'POST', body: formData }
  );
  return res.json();
};
```

---

## Environment Variables

See `.env` file:
```
DATABASE_URL=sqlite:///./inventix.db
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
ALLOWED_EXTENSIONS=.pdf,.docx,.doc,.txt
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Verification

1. **Create a project** via API or Swagger
2. **Stop the server** (Ctrl+C)
3. **Restart the server**
4. **GET /api/projects** - Project should still exist
5. **Upload a file** - Check `uploads/` directory
6. **Verify honest responses** - `analysis_status` is always `NOT_STARTED`
