# 🧠 LogicDaily: Competitive Aptitude Engine

**LogicDaily** is a full-stack, state-of-the-art competitive aptitude engine. It delivers daily, curated reasoning challenges—covering mathematics, logical deduction, and verbal aptitude. It features high-performance daily challenge caching and automated background rotation.

Built with a modern, high-performance tech stack, LogicDaily is optimized for low-latency delivery, serverless scale, and premium user experience.

---

## 🚀 Key Features

*   **Daily Aptitude Challenges:** Seamlessly rotates questions covering math, logic, and verbal categories once every 24 hours.
*   **High-Performance Caching:** Uses **Redis** (fully compatible with Upstash Serverless) to deliver the active daily challenge with sub-millisecond response times.
*   **Intelligent Local Fallback:** Employs an intelligent in-memory cache fallback when Redis is unconfigured or unreachable, ensuring a seamless offline development experience.
*   **Dynamic Leaderboard:** Real-time aggregation of user scores, ranked with a premium, responsive leaderboard featuring top-performer accolades.
*   **Robust Background Jobs:** Automated daily challenge rotation triggered securely via serverless cron events.
*   **Fully Responsive UI:** Engineered with **Vue.js 3**, **Bootstrap 5**, and custom typography/micro-animations for a stunning mobile-first layout.

---

## 🛠 Tech Stack

*   **Backend:** FastAPI (Python 3.10+) with SQLAlchemy ORM
*   **Frontend:** Vue.js 3 (Composition API) scaffolded via Vite
*   **Styling:** Bootstrap 5 & Bootstrap Icons (Glassmorphic dark-mode accenting)
*   **Databases:** SQLite (Development) / PostgreSQL (Production)
*   **Caching:** Redis (Upstash) with localized memory cache failover
*   **Testing & CI/CD:** Pytest (Backend API tests), ESLint (Frontend validation), and GitHub Actions

---

## 📂 Project Architecture

The project is managed as a high-integrity monorepo:

```text
├── backend/            # FastAPI Backend Application
│   ├── main.py         # App Entry Point & CORSMiddleware
│   ├── database.py     # SQLAlchemy Connection & Session Management
│   ├── models.py       # DB Models (User, Question, Submission)
│   ├── schemas.py      # Pydantic Schemas for validation
│   ├── routers/        # Modular API route controllers
│   └── requirements.txt# Backend Dependencies
│
├── frontend/           # Vue 3 Frontend Single Page App
│   ├── src/            # App source code (Components, Views, Stores)
│   ├── package.json    # Frontend dependency manifest
│   └── vite.config.js  # Vite compilation settings
│
├── vercel.json         # Vercel Serverless & Cron configuration
└── README.md           # This document
```

---

## ⚙️ Local Development Setup

### 1. Prerequisites
Ensure you have the following installed:
*   Python 3.10 or higher
*   Node.js 18 or higher (with `npm`)

### 2. Backend Setup
1. Navigate to the backend directory:
    ```bash
    cd backend
    ```
2. Create and activate a virtual environment (already initialized as `.venv` in workspace root):
    ```bash
    source ../.venv/bin/activate
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Start the FastAPI development server:
    ```bash
    uvicorn main:app --reload
    ```
    The API documentation will be available at `http://localhost:8000/docs`.

### 3. Frontend Setup
1. Navigate to the frontend directory:
    ```bash
    cd ../frontend
    ```
2. Install dependencies:
    ```bash
    npm install
    ```
3. Start the Vite development server:
    ```bash
    npm run dev
    ```
    Open `http://localhost:5173` in your browser to view the application.

---

## 🧪 Testing

To run the test suite, ensure your virtual environment is active and execute:
```bash
PYTHONPATH=backend pytest backend/tests/
```
For frontend linting:
```bash
cd frontend && npm run lint
```

---

## 📄 License
This project is licensed under the MIT License.
