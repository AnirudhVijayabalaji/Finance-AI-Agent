# 💰 Finance AI Agent

> A multi-modal personal finance intelligence system powered by **Google Gemini AI** — analyze bank statements, interpret spending graphs, and get actionable financial insights through a conversational AI interface.

---

## ✨ Features

- 📄 **PDF Bank Statement Parser** — Upload your bank statement and automatically extract structured transactions
- 🖼️ **Image / Graph Analyzer** — Interpret Google Pay / UPI spending screenshots using AI vision
- 💬 **Conversational AI Chat** — Ask natural language questions like *"Where did I overspend?"* or *"Can I afford a ₹50,000 laptop?"*
- 📊 **Financial Dashboard** — Visual summaries of income, expenses, and spending by category
- 🔐 **Password-Protected PDF Support** — Handles encrypted bank statements
- 🧮 **Financial Simulator** — Evaluate affordability and predict the impact of potential purchases
- 💾 **Dual Storage Modes** — PostgreSQL for production, in-memory JSON fallback for development
- 🚀 **Deployable on Vercel** — Full-stack deployment with frontend + Python backend

---

## 🏗️ Architecture

```
User Input (PDF / Image / Query)
        ↓
React Frontend (Vite + TailwindCSS)
        ↓
FastAPI Backend (Python)
        ↓
Gemini AI Agent (Google Gemini)
        ↓
Tool Layer (PDF Parser, Image Analyzer, Calculator, Simulator)
        ↓
Data Layer (PostgreSQL / In-Memory JSON)
        ↓
Insight Response → Dashboard / Chat
```

---

## 🧩 Tech Stack

| Layer       | Technology                                   |
|-------------|----------------------------------------------|
| Frontend    | React 19, Vite, TailwindCSS, Recharts, Framer Motion |
| Backend     | Python, FastAPI, Uvicorn                     |
| AI / LLM    | Google Gemini (`google-genai`)               |
| PDF Parsing | `pdfplumber`, `pikepdf`                      |
| Database    | PostgreSQL (`psycopg2`) / JSON in-memory     |
| ORM         | SQLAlchemy                                   |
| Deployment  | Vercel (frontend + backend)                  |

---

## 📁 Project Structure

```
FINANCE AI/
├── backend/
│   ├── main.py                  # FastAPI application & API routes
│   ├── models.py                # Pydantic / SQLAlchemy models
│   ├── requirements.txt         # Python dependencies
│   ├── memory_store.json        # In-memory fallback persistence
│   ├── .env.example             # Environment variable template
│   ├── agent/
│   │   └── gemini_agent.py      # Gemini AI agent logic
│   ├── tools/
│   │   ├── pdf_parser.py        # Bank statement PDF extractor
│   │   ├── image_analyzer.py    # GPay/UPI graph analyzer
│   │   ├── calculator.py        # Financial metrics calculator
│   │   ├── categorizer.py       # Expense categorizer
│   │   └── simulator.py         # Financial scenario simulator
│   └── db/
│       ├── database.py          # DB connection & session
│       └── crud.py              # Database operations
├── frontend/
│   ├── src/                     # React components & pages
│   ├── public/                  # Static assets
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── vercel.json                  # Vercel deployment config
├── architecture.md              # Detailed architecture docs
├── Tools.md                     # Tool layer documentation
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** v18+ and npm
- **Python** 3.10+
- **PostgreSQL** (optional — app runs in in-memory mode without it)
- A **Google Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

---

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "FINANCE AI"
```

---

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env
# Edit .env and fill in your values:
#   GEMINI_API_KEY=your-gemini-api-key-here
#   DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_ai

# Start the backend server
python main.py
```

The backend runs at **http://localhost:8000**

> 💡 **No PostgreSQL?** The app automatically falls back to in-memory mode using `memory_store.json`. No extra setup needed.

---

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend runs at **http://localhost:5173**

---

## 🔑 Environment Variables

Create a `.env` file in the `backend/` directory:

```env
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/finance_ai
```

| Variable         | Required | Description                             |
|------------------|----------|-----------------------------------------|
| `GEMINI_API_KEY` | ✅ Yes    | Google Gemini API key                   |
| `DATABASE_URL`   | ❌ No     | PostgreSQL connection string (optional) |

---

## 🛠️ API Endpoints

| Method | Endpoint            | Description                              |
|--------|---------------------|------------------------------------------|
| `GET`  | `/`                 | Health check                             |
| `GET`  | `/summary`          | Get financial dashboard summary          |
| `GET`  | `/summary?refresh=true` | Force re-analysis of uploaded data  |
| `POST` | `/upload/statement` | Upload a PDF bank statement              |
| `POST` | `/chat`             | Send a natural language query to the AI  |
| `GET`  | `/chat/history`     | Retrieve chat history for a session      |
| `GET`  | `/uploads`          | List all uploaded statements             |
| `GET`  | `/debug`            | Debug raw parsed transaction data        |

---

## 💬 Example Queries

The AI agent understands natural language questions such as:

- *"Where did I overspend this month?"*
- *"How much did I spend on food?"*
- *"Can I afford a ₹50,000 laptop?"*
- *"What's my daily average spend?"*
- *"How much have I received vs spent?"*

---

## 📊 Expense Categories

Transactions are automatically classified into:

| Category      | Examples                              |
|---------------|---------------------------------------|
| 🍔 Food        | Zomato, Swiggy, restaurants, cafes   |
| 🚗 Transport   | Uber, Ola, fuel, metro               |
| 🛍️ Shopping   | Amazon, Flipkart, retail stores      |
| 🏠 Bills       | Rent, electricity, utilities         |
| 📺 Subscriptions | Netflix, Spotify, OTT platforms   |
| 📦 Other       | Uncategorized transactions           |

---

## 🚀 Deployment (Vercel)

The project is pre-configured for Vercel deployment via `vercel.json`.

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from the project root
vercel
```

Make sure to configure the following environment variables in your Vercel project settings:
- `GEMINI_API_KEY`
- `DATABASE_URL` (if using PostgreSQL)

---

## 🔐 Security & Privacy

- All financial data is treated as **highly sensitive**
- API keys are stored in environment variables, never hardcoded
- Raw transaction logs are not exposed unnecessarily
- PDF files are processed in temporary storage and immediately deleted after parsing

---

## ⚠️ Disclaimer

This tool is intended for **personal financial awareness** only. It does **not** provide professional financial advice, stock recommendations, or investment guidance. Always consult a certified financial advisor for major financial decisions.

---

## 📄 License

This project is for personal use. Please review applicable licenses for all third-party dependencies.

---

> Built with ❤️ using Google Gemini AI, FastAPI, and React
