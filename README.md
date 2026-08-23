# 🛡️ AgentGuard — AI Agent Reliability & Security Platform

> **Hackathon Submission — Problem Statement 4**
> AI Agent Evaluation and Reliability Engine
> G. L. Bajaj Institute of Technology and Management

---

## 📌 Problem Statement

Autonomous AI agents are increasingly deployed for consequential work, yet industry benchmarks report failure on the majority of real-world tasks — with cited rates near 70%. Teams typically ship agents against a handful of manually written test prompts, so real failure modes surface only after deployment on live data.

**AgentGuard** solves this by automatically generating adversarial test scenarios, running the agent in a sandboxed environment, classifying every failure mode, and producing a downloadable reliability report — functioning as **continuous integration for autonomous agents.**

---

## 🎯 What AgentGuard Does

AgentGuard is a 4-module pipeline:

```
Agent Definition (name + description + tools)
         │
         ▼
┌─────────────────────────────────┐
│  Module 1 — Scenario Synthesizer│  LLM generates 5 adversarial test cases
│  (synthesizer.py)               │  covering all 5 failure taxonomies
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Module 2 — Sandboxed Execution │  Real LangGraph ReAct agent runs each
│  (sandbox.py)                   │  test case with dynamically built tools
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Module 3 — Failure Classifier  │  LLM reads execution trace and classifies
│  (classifier.py)                │  failure type, severity score (0–100)
└─────────────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────┐
│  Module 4 — Dashboard + Report  │  Visual reliability dashboard + PDF report
│  (frontend + report.py)         │  with safety score and remediation advice
└─────────────────────────────────┘
```

---

## 🔥 5 Failure Taxonomies Detected

| Failure Type | Description |
|---|---|
| **Goal Drift** | Agent loses track of its primary objective due to ambiguous instructions |
| **Tool Hallucination** | Agent calls non-existent tools or passes invalid parameters |
| **Destructive Action** | Agent performs irreversible operations without confirmation |
| **Loop Lockout** | Agent enters an infinite tool-call loop with no exit condition |
| **Conflicting Parameters** | Agent receives contradictory instructions and enters inconsistent state |

---

## 🏗️ Architecture

```
Frontend (HTML/CSS/JS)
        │
        │  HTTP POST /evaluate, /generate-tests, /report
        ▼
FastAPI Backend (main.py)
        │
        ├── synthesizer.py  ──→  Groq API (openai/gpt-oss-120b)
        │                        Generates adversarial test cases
        │
        ├── sandbox.py      ──→  LangGraph ReAct Agent
        │                        Dynamic tool building + real execution
        │                        Parallel execution (ThreadPoolExecutor)
        │
        ├── classifier.py   ──→  Groq API (openai/gpt-oss-120b)
        │                        AI judge reads traces, scores failures
        │
        └── report.py       ──→  ReportLab
                                 Generates downloadable PDF report
```

---

## ✨ Key Features

- **Generic — works for any AI agent.** Define any agent with any tools. AgentGuard dynamically builds the execution environment from your tool definitions.
- **Real sandbox execution.** LangGraph ReAct agent actually runs adversarial prompts — not simulated, not mocked.
- **Parallel pipeline.** All 5 sandbox executions and all 5 classifications run concurrently using ThreadPoolExecutor — full evaluation completes in ~60 seconds.
- **AI-powered red teaming.** Uses GPT-OSS-120B on Groq to think adversarially — generating attacks specific to your agent's tools and description.
- **AI-powered judging.** The same LLM reads execution traces as an expert safety auditor — understands context, not just rule-based thresholds.
- **Downloadable PDF report.** Full reliability report with safety score, failure analysis, execution traces, and remediation recommendations.
- **CI/CD Deployment Gate.** Configurable safety score threshold — agents below the threshold are automatically blocked from deployment.
- **Regression Tracker.** Save evaluation snapshots across versions to track reliability improvements over time.
- **AI Copilot.** Ask natural language questions about your evaluation results.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn |
| LLM (Synthesis + Classification) | Groq API — openai/gpt-oss-120b |
| LLM (Sandbox Agent) | Groq API via LangChain-Groq |
| Agent Framework | LangGraph (ReAct agent pattern) |
| Parallel Execution | Python ThreadPoolExecutor |
| PDF Generation | ReportLab |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Environment | python-dotenv |

---

## 📁 Project Structure

```
agent-guard/
├── backend/
│   ├── main.py           # FastAPI server + orchestration engine
│   ├── synthesizer.py    # Module 1 — adversarial test case generator
│   ├── sandbox.py        # Module 2 — sandboxed LangGraph agent execution
│   ├── classifier.py     # Module 3 — AI failure classifier and judge
│   ├── report.py         # PDF report generator
│   ├── .env              # API keys (not committed)
│   └── requirements.txt  # Python dependencies
└── frontend/
    ├── index.html         # Main application UI
    ├── style.css       # Stylesheet
    └── script.js            # Application logic + backend integration
```

---

## 🚀 Local Setup and Run

### Prerequisites
- Python 3.10+
- A Groq API key (free at console.groq.com — no credit card required)

### Step 1: Clone the repository
```bash
git clone https://github.com/Kaust22/agent-guard.git
cd agent-guard
```

### Step 2: Set up the backend
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Configure API key
Create a `.env` file inside the `backend/` folder:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Step 4: Start the backend server
```bash
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`

### Step 5: Open the frontend
Open `frontend/type.html` directly in Chrome by double-clicking it in File Explorer.

---

## 📋 Requirements.txt

```
fastapi
uvicorn
groq
langchain
langgraph
langchain-groq
langchain-core
python-dotenv
reportlab
pydantic
```

---

## 🎬 How to Use

1. **Agent Setup** — Enter your agent's name, description, and available tools
2. **Attack Lab** — View the 5 auto-generated adversarial test cases specific to your agent
3. **Run Evaluation** — Watch the pipeline execute in real time (60–90 seconds)
4. **Live Traces** — Inspect step-by-step execution traces for each test case
5. **Reliability Report** — View the safety score, failure breakdown, and recommendations
6. **Download PDF** — Export the full reliability report as a PDF
7. **CI/CD Gate** — Set a deployment threshold — agents below it are blocked
8. **Regression Tracker** — Save and compare evaluation versions over time
9. **AI Copilot** — Ask questions about your results in natural language

---

## 📊 Example Output

| Agent | Safety Score | Critical Failures | Recommendation |
|---|---|---|---|
| Customer Support Agent | 48/100 | 2 | Add confirmation gates before bulk operations |
| Healthcare Appointment Agent | 52/100 | 1 | Enforce patient identity verification |
| Weather Information Agent | 82/100 | 0 | Agent is safe for deployment |

---

## 💡 Why AgentGuard?

> "Every autonomous action deserves a clear safety boundary."

Current AI agent testing is manual, incomplete, and reactive. AgentGuard makes it **automatic, comprehensive, and proactive** — catching failures before they reach production.

- ✅ No manual test writing
- ✅ Works for any agent, any domain
- ✅ Real execution, not simulation
- ✅ Actionable remediation advice
- ✅ CI/CD ready

---

## 👥 Team

| Name | Role |
|---|---|
| Kaustubh Kant Rastogi | Backend, LLM Integration, Architecture |
| Ayush Kumar | Frontend, UI/UX, Dashboard |
| Avinash | GenAI Research, Sandbox, System Design, Presentation |

**Institution:** G. L. Bajaj Institute of Technology and Management, Greater Noida
**Problem Statement:** PS4 — AI Agent Evaluation and Reliability Engine

---

