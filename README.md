# Se7ti — Health Companion Web App

<div align="center">

**Track chronic disease medications • Find nearby providers • Scan prescriptions • Stock alerts**

*A community health platform connecting chronic disease patients with local pharmacies in Oujda, Morocco*

</div>

---

## Quick Start

```bash
# 1. Create virtual environment & install dependencies
python -m venv .venv
.venv\Scripts\activate     # Windows
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials and API keys

# 3. Initialize the database
# Run backend/database/schema.sql in your Supabase SQL editor
# Then seed mock data:
python scripts/seed_database.py

# 4. Launch the app
uvicorn backend.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## What is Se7ti?

Se7ti (صحتّي — "my health" in Moroccan Arabic) is a web platform that connects **chronic disease patients (ALD)** with **on-duty pharmacies** in Oujda. It enables patients to:

- **Visualize** nearby patients sharing the same medications on an interactive map
- **Scan** a prescription → OCR → AI parsing → geo-medication matching
- **Track** medication stock with in-app alerts when running low
- **Find** on-duty pharmacies with real-time calendar and map badges

### Target Users

| Role | Primary Need |
|------|-------------|
| Chronic disease patient (ALD) | Find nearby patients with same meds, get stock alerts |
| Pharmacist | Publish on-duty status, see local demand |
| Doctor / Community worker | Upload prescriptions, visualize the local network |

---

## Features

### Interactive Map
- Distinct icons for patients and pharmacies on a Leaflet + OSM map centered on Oujda
- Click → popup with details (pseudo, pathology, meds, stock for users — name, address, phone, on-duty status for pharmacies)
- Toggle "On-duty only" / "All", search by name/medication, legend overlay

### Prescription Scan & Analysis
- Upload photo/PDF → multi-model OCR cascade → raw text
- LLM Parser via OpenRouter → GPT-4o (fallback Claude) → structured medication JSON
- Matching Engine → geo + medication query → matching patients + stock alerts

### OCR Cascade (Multi-Model)
- **Tier 1 — Free** (5 models: LLaMA 3.2 Vision, Qwen2-VL, Gemma 3, Phi-4, LLaMA 4 Scout)
- **Tier 2 — Claude Haiku**
- **Tier 3 — Claude Sonnet** (final, always accepted)
- Best result preserved across all attempts

### Stock Tracking & Alerts
- Manual purchase declaration
- Estimated stock calculation based on dosage
- In-app alert when stock < 7 days

### On-Duty Calendar
- Pharmacies with on-duty schedules
- "On duty" badge on map markers
- Real-time API for currently on-duty pharmacies

---

## Architecture

```
[Navigateur]  ←→  [FastAPI]  ←→  [Supabase (PostgreSQL + PostGIS)]
                      │
               ┌──────┼──────┐
               ▼      ▼      ▼
            [TrOCR] [OpenRouter] [Supabase Storage]
                      │
                   [GPT-4o/Claude]
```

### Upload Flow
1. Upload photo → Supabase Storage
2. TrOCR (CPU local) → raw text
3. OpenRouter → GPT-4o → structured medication JSON
4. Matching Engine → geo + medication query
5. Returns: `{meds, matching_users, map_markers}`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + PostGIS (Supabase) |
| Auth | Supabase Auth (email/password, OTP) |
| OCR | TrOCR Microsoft + OpenRouter vision cascade |
| LLM | OpenRouter → OpenAI GPT-4o → Claude (fallback) |
| Frontend | Vanilla HTML/CSS/JS + Leaflet.js + OSM + Supabase JS Client |
| Map | Leaflet.js + OSM tiles + Nominatim + Turf.js |
| Storage | Supabase Storage (prescription images) |

---

## Project Structure

```
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── LICENSE
├── Rules.md
│
├── backend/
│   ├── main.py                     # FastAPI entry point
│   ├── config.py                   # Pydantic settings
│   ├── database/
│   │   ├── schema.sql              # PostgreSQL DDL
│   │   ├── seed_mock.sql           # Mock data
│   │   └── connection.py           # Supabase client
│   ├── routes/
│   │   ├── users.py                # User API
│   │   ├── pharmacies.py           # Pharmacy API
│   │   ├── prescriptions.py        # Prescription upload + OCR
│   │   ├── matching.py             # Geo + medication matching
│   │   ├── stock.py                # Stock tracking
│   │   └── alerts.py               # In-app alerts
│   ├── services/
│   │   ├── ocr_service.py          # TrOCR + OpenRouter cascade
│   │   ├── llm_parser.py           # OpenRouter → GPT/Claude
│   │   ├── matching_engine.py      # Geo-medication matching
│   │   ├── stock_calculator.py     # Stock estimation
│   │   └── alert_service.py        # Alert generation
│   ├── models/
│   │   ├── user.py                 # Pydantic models
│   │   ├── pharmacy.py
│   │   ├── medication.py
│   │   └── prescription.py
│   └── auth/
│       └── supabase_auth.py        # Supabase auth middleware
│
├── frontend/
│   ├── index.html                  # SPA entry point
│   ├── pages/
│   │   ├── login.html              # Login / signup
│   │   ├── map.html                # Interactive map (Leaflet)
│   │   ├── upload.html             # Prescription upload
│   │   ├── stock.html              # Stock dashboard
│   │   └── admin.html              # Admin: on-duty calendar
│   ├── css/
│   │   ├── style.css               # Global theme
│   │   ├── map.css                 # Map styling
│   │   └── responsive.css          # Mobile adaptations
│   ├── js/
│   │   ├── app.js                  # SPA routing, global state
│   │   ├── auth.js                 # Supabase auth
│   │   ├── api.js                  # REST client
│   │   ├── map.js                  # Leaflet initialization
│   │   ├── markers.js              # User/pharmacy markers
│   │   ├── filters.js              # Map filters
│   │   ├── matching.js             # Matching results display
│   │   ├── prescription.js         # Upload & validation
│   │   ├── stock.js                # Stock dashboard
│   │   ├── alerts.js               # In-app notifications
│   │   └── admin.js                # Admin features
│   └── assets/icons/               # SVG marker icons
│
├── data/
│   ├── mock_pharmacies.json        # 5 mocked pharmacies
│   └── mock_users.json             # 5 mocked ALD patients
│
├── scripts/
│   ├── seed_database.py            # Import mock data → Supabase
│   ├── test_trocr.py               # TrOCR inference test
│   └── check_compatibility.py      # Hardware compatibility check
│
└── tests/
    ├── test_api.py                 # API integration tests
    ├── test_matching.py            # Matching engine tests
    ├── test_stock.py               # Stock calculator tests
    └── test_ocr.py                 # OCR service tests
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/users` | List users + coords + pathologies + meds + stock |
| GET | `/api/pharmacies` | List pharmacies (optional on-duty filter) |
| GET | `/api/pharmacies/garde/now` | Currently on-duty pharmacies |
| POST | `/api/prescriptions/upload` | Upload prescription → OCR → parse |
| POST | `/api/prescriptions/manual` | Manual medication entry |
| GET | `/api/matching` | Geo + medication matching |
| POST | `/api/stock/purchase` | Declare a purchase |
| GET | `/api/stock/:userId` | Stock dashboard |
| GET | `/api/alerts/:userId` | Active alerts |
| GET | `/api/medications/search` | Search known ALD medications |

---

## Database Schema

**PostgreSQL + PostGIS** on Supabase with 6 tables:

- `users` — Patient profiles with geolocation
- `medications` — Prescribed medications with stock tracking
- `prescriptions` — Uploaded prescriptions with OCR + LLM results
- `pharmacies` — Pharmacy registry
- `garde_calendar` — On-duty schedules
- `stock_logs` — Purchase history

See [backend/database/schema.sql](backend/database/schema.sql).

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` / `SUPABASE_KEY` | Supabase project credentials |
| `OPENROUTER_API_KEY` | OpenRouter API key (LLM + OCR cascade) |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` | Fallback LLM keys |
| `OCR_BACKEND` | `"openrouter"` (default) or `"trocr"` (local) |
| `OCR_FREE_THRESHOLD` / `OCR_HAIKU_THRESHOLD` | Confidence thresholds (0.0–1.0) |

---

## Hardware Compatibility

- Target device: Dell Latitude 5400 (Intel Core i5 8th gen, 8-16 GB RAM)
- TrOCR: `trocr-base-printed` ~300-600 MB RAM, CPU inference ~2-5s/image
- No dedicated GPU required
- Recommended: Windows 10/11 or Linux

---

## License

MIT
