# Automation Value Intelligence Platform (AVIP)

AVIP is a decision-support platform for pre-sales consultants to quantify, visualize, and present the business value of intelligent automation.

## Stack

- Frontend: React.js
- UI: Material Tailwind CSS
- Backend: FastAPI
- Database: MySQL 8.0
- ORM: SQLAlchemy
- Authentication: JWT
- AI: OpenAI GPT / Azure OpenAI / Gemini
- Document Processing: PyMuPDF, pdfplumber, python-docx
- OCR: Tesseract OCR
- Charts: Recharts
- Background Tasks: Celery + Redis
- File Storage: Local storage for MVP
- Report Generation: ReportLab and python-pptx

## Repository Layout

```text
backend/
  app/
    api/
    core/
    db/
    models/
    schemas/
    services/
    utils/
  requirements.txt
frontend/
  src/
  package.json
```

## Getting Started

### Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## MVP Scope

- Process discovery and document upload
- AI-assisted task classification
- Automation readiness scoring
- Value and ROI dashboards
- Proposal and presentation generation
- Multi-project portfolio dashboard with benchmark comparison
- Project edit and delete actions
- Uploaded document edit, download, and delete actions

## Core API Flow

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `POST /api/v1/projects/{project_id}/documents`
- `POST /api/v1/projects/{project_id}/analysis`
- `POST /api/v1/projects/{project_id}/proposal`
- `GET /api/v1/projects/{project_id}/proposal/download/pdf`
- `GET /api/v1/projects/{project_id}/proposal/download/pptx`

## AI Provider Modes

Set `ANALYSIS_PROVIDER` to one of:

- `auto`
- `openai`
- `azure-openai`
- `gemini`
- `rule`

If no provider key is configured, AVIP falls back to deterministic analysis automatically.
