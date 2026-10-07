# Floora Bakes

Floora Bakes is a full-stack bakery sales analytics application. It supports CSV/XLSX uploads, data mapping, sales reporting, product and time analysis, automated insights, global filters, and batch upload deletion.

## Features

- FastAPI backend with SQLAlchemy and SQLite
- React and Vite frontend
- CSV and XLSX import with column mapping
- Sales history and upload history
- Dashboard, product, time, and insight analytics
- CSV/XLSX report export
- Global date, product, and category filters
- Responsive dashboard UI
- Automated tests and sample data generation

## Architecture

- `backend/` — FastAPI API, database models, services, routers, migrations, and tests
- `frontend/` — React application, Vite configuration, Tailwind CSS, and API client

## Setup

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API runs at `http://localhost:8000`.

## Tests

```powershell
cd backend
pytest
```

## Sample data

```powershell
cd backend
python scripts/generate_sample_data.py
```

The generated workbook is written to `backend/sample_sales.xlsx`.
