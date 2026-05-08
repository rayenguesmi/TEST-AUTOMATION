<div align="center">

# AUTOTEST

### AI-Powered Test Automation Platform

*From functional specification to executed Selenium tests — fully automated.*

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Node.js](https://img.shields.io/badge/Node.js-Express-339933?logo=nodedotjs&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-8.x-47A248?logo=mongodb&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4.x-43B02A?logo=selenium&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Multi--LLM-1C3C3C?logo=chainlink&logoColor=white)

</div>

---

## Overview

AUTOTEST is a full-stack platform that takes a **plain-text or markdown functional specification** and a **target URL**, then automatically:

1. Parses the spec with an LLM to extract testable features
2. Generates exhaustive test cases (positive, negative, edge cases)
3. Scans the live DOM of the target site to collect real CSS selectors
4. Generates executable **Selenium + pytest** scripts grounded in real DOM elements
5. Runs the tests against the target browser
6. Produces a rich **HTML/JSON report**

Everything is accessible through a React dashboard with user authentication, test history, and run comparisons.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│               React Frontend  :5173                      │
│  Spec input · Progress tracking · Reports · History      │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP
                      ▼
┌──────────────────────────────────────────────────────────┐
│           Node.js / Express API  :5000                   │
│  Auth (JWT) · Test orchestration · MongoDB · Webhook     │
└─────────────────────┬────────────────────────────────────┘
                      │ HTTP (async)
                      ▼
┌──────────────────────────────────────────────────────────┐
│              FastAPI Engine  :8000                       │
│                                                          │
│  [1] Spec Parser  →  [2] Test Case Generator             │
│  [3] DOM Scanner  →  [4] Selenium Script Generator       │
│  [5] Test Runner (pytest)  →  [6] Report Generator       │
└──────────────────────────────────────────────────────────┘
                      │ Webhook callback
                      ▼
              MongoDB  :27017
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, TailwindCSS, Recharts |
| Backend API | Node.js, Express, Mongoose, JWT, Nodemailer |
| AI Engine | Python 3.12, FastAPI, LangChain |
| LLM Providers | Groq, OpenAI, Anthropic, Google Gemini, Mistral, Ollama |
| Test Execution | Selenium 4, pytest, WebDriver Manager |
| Database | MongoDB |
| Report | Jinja2 HTML templates + JSON |

---

## Features

- **Multi-LLM support** — switch between Groq, OpenAI, Anthropic, Gemini, Mistral, or a local Ollama model per test run; users supply their own API keys
- **Live DOM scanning** — Selenium crawls the target site before generation so selectors are real, not hallucinated
- **Full pipeline in one click** — spec → test cases → scripts → execution → report
- **Background processing** — non-blocking FastAPI tasks with progress polling and webhook callbacks
- **Test history & comparison** — filter by status / LLM / date; diff two runs side by side
- **Admin dashboard** — global stats and all-users test overview
- **Multi-browser** — Chrome or Firefox, headless or headed
- **PDF spec support** — upload a PDF specification instead of pasting text

---

## Prerequisites

| Requirement | Version |
|---|---|
| Node.js | ≥ 18 |
| Python | 3.12 |
| MongoDB | local or Atlas |
| Google Chrome | latest (for Selenium) |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rayenguesmi/portfolio.git
cd "Desktop/PFE RAYEN/AUTOTEST"
```

### 2. Python dependencies

```bash
cd autotest_package
pip install -r requirements.txt
pip install uvicorn
```

### 3. Node.js — server

```bash
cd user/user-entity-REACT-NODE-JS-/server
npm install
```

### 4. Node.js — client

```bash
cd user/user-entity-REACT-NODE-JS-/client
npm install
```

---

## Configuration

### Server — `user/user-entity-REACT-NODE-JS-/server/.env`

```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/user-auth
JWT_SECRET=your_long_random_secret

# Gmail (App Password, not your normal password)
EMAIL_USER=your@gmail.com
EMAIL_PASS=your_app_password

CLIENT_URL=http://localhost:5173
SERVER_URL=http://localhost:5000
FASTAPI_URL=http://localhost:8000
```

### Python Engine — `autotest_package/config.yaml`

```yaml
llm:
  provider: "groq"          # groq | openai | anthropic | google | mistral | ollama
  model: "llama-3.3-70b-versatile"

selenium:
  browser: "chrome"         # chrome | firefox
  headless: false
```

> LLM API keys are supplied at runtime per test run — they are never stored in config.

---

## Running the Platform

Open **three terminals** and start each service:

### Terminal 1 — FastAPI Engine

```bash
cd autotest_package
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2 — Node.js API

```bash
cd user/user-entity-REACT-NODE-JS-/server
npm run dev
```

### Terminal 3 — React Frontend

```bash
cd user/user-entity-REACT-NODE-JS-/client
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Node.js API | http://localhost:5000 |
| FastAPI Engine | http://localhost:8000 |
| FastAPI Swagger | http://localhost:8000/docs |

---

## API Reference

### FastAPI Engine `:8000`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/generate` | Full pipeline: parse → generate → run → report |
| `POST` | `/run-test` | Generation only (no execution) |
| `GET` | `/status/{task_id}` | Real-time task status and progress |
| `GET` | `/autotest-output/{task_id}/reports/report.html` | Serve generated HTML report |

### Node.js API `:5000`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/auth/register` | — | Register a new user |
| `POST` | `/api/auth/login` | — | Login (JWT cookie) |
| `POST` | `/api/tests/run` | JWT | Start a new test run |
| `POST` | `/api/tests/webhook` | — | FastAPI result callback |
| `GET` | `/api/tests/my-tests` | JWT | User test history |
| `GET` | `/api/tests/filtered` | JWT | Filter by status / LLM / date |
| `GET` | `/api/tests/compare` | JWT | Diff two test runs |
| `GET` | `/api/tests/:id/progress` | JWT | Live progress for a test |
| `GET` | `/api/tests/stats` | JWT + Admin | Platform-wide statistics |
| `GET` | `/api/health` | — | Health check (all services) |

---

## Project Structure

```
AUTOTEST/
├── autotest_package/          # Python FastAPI engine
│   ├── api.py                 # FastAPI app & endpoints
│   ├── main.py                # CLI entry point
│   ├── spec_parser.py         # LLM spec → features
│   ├── test_case_generator.py # LLM features → test cases
│   ├── spec_to_selenium.py    # LLM test cases → Selenium scripts
│   ├── dom_scanner.py         # Live DOM crawler
│   ├── test_runner.py         # pytest execution wrapper
│   ├── report_generator.py    # HTML/JSON report builder
│   ├── config.yaml            # LLM & Selenium config
│   ├── requirements.txt
│   └── utils/
│       ├── llm_client.py      # Multi-provider LangChain wrapper
│       ├── file_loader.py     # PDF/Markdown loader
│       └── logger.py
│
└── user/
    └── user-entity-REACT-NODE-JS-/
        ├── server/            # Node.js Express API
        │   ├── server.js
        │   ├── controllers/
        │   ├── models/
        │   ├── routes/
        │   └── middleware/
        └── client/            # React + Vite frontend
            ├── src/
            └── public/
```

---

## Supported LLM Providers

| Provider | Model example | Notes |
|---|---|---|
| Groq | `llama-3.3-70b-versatile` | Recommended — fast inference |
| OpenAI | `gpt-4o` | |
| Anthropic | `claude-3-5-sonnet-20241022` | |
| Google | `gemini-1.5-pro` | |
| Mistral | `mistral-large-latest` | |
| Ollama | `qwen2.5-coder:7b-instruct` | Local — no API key required |

---

## License

This project was developed as part of a final-year engineering project (PFE).

---

<div align="center">
  Built by <strong>Rayen Guesmi</strong>
</div>
