# Building Kunani End-to-End

**A chaptered guide for the [Agentic AI e2e](https://youtube.com/@agenticaie2e) YouTube series.**

This document describes how to build **Kunani** — a production-style civic issue tracking system where citizens report non-emergency issues. It follows the same structure and principles as the Trivia Pals project: **frontend** (Next.js, React, shadcn) and **backend** (FastAPI, LangGraph, PostgreSQL, Pydantic). Use it as your reference while following the tutorial or reading the codebase.

---

## Table of Contents

1. [Introduction & What We're Building](#chapter-0-introduction--what-were-building)
2. [Repo Structure & Tech Stack](#chapter-1-repo-structure--tech-stack)
3. [Project Setup & Environment](#chapter-2-project-setup--environment)
4. [The LLM Service (`llm.py`)](#chapter-3-the-llm-service-llmpy)
5. [Data Models with Pydantic](#chapter-4-data-models-with-pydantic)
6. [Database Schema & DB Service](#chapter-5-database-schema--db-service)
7. [LangGraph Tools](#chapter-6-langgraph-tools)
8. [LangGraph Workflow Design](#chapter-7-langgraph-workflow-design)
9. [Building the Agents](#chapter-8-building-the-agents)
10. [Memory & Checkpointing](#chapter-9-memory--checkpointing)
11. [Backend API with FastAPI](#chapter-10-backend-api-with-fastapi)
12. [Frontend with Next.js, React & shadcn](#chapter-11-frontend-with-nextjs-react--shadcn)
13. [End-to-End Flow & Running the App](#chapter-12-end-to-end-flow--running-the-app)
14. [Observability & Monitoring (Langfuse)](#chapter-13-observability--monitoring-langfuse)
15. [Deployment & Production](#chapter-14-deployment--production)

---

## Chapter 0: Introduction & What We're Building

### What is Kunani?

Kunani (Najua) is a **civic issue tracking system**: citizens report non-emergency issues (e.g. potholes, broken streetlights, waste) and the system triages, collects details, and saves issues to a database. It is built with:

- **Multi-agent workflow**: Welcome (triage) → Issue Filler (collect details) → Issue Reporting (save).
- **LangGraph** for orchestration (state, nodes, conditional routing).
- **Structured outputs** via Pydantic and Instructor.
- **PostgreSQL** for issues and optional conversation checkpoints.
- **Same repo layout as Trivia Pals**: `frontend/` and `backend/` folders.

### Principles (No Deviation)

- **Backend**: Python, FastAPI, LangGraph, Pydantic, shared `llm.py`-style service, routers under `app/routers`, agents under `app/agents`, graph under `app/graph`, models under `app/models`, tools under `app/tools`, shared services under `app/shared_services`.
- **Frontend**: Next.js (App Router), React, TypeScript, shadcn/ui (Radix), Tailwind CSS, Axios for API calls, Zustand for client state where needed.
- **API**: REST; frontend calls backend with `NEXT_PUBLIC_API_URL`; CORS configured for frontend origin.
- **Packages**: React, Next.js, shadcn, LangGraph, PostgreSQL, Pydantic, Instructor, OpenAI-compatible clients, FastAPI, Axios — as used in the reference projects.

---

## Chapter 1: Repo Structure & Tech Stack

### Target Repo Layout (Like Trivia Pals)

```
kunani/
├── frontend/                 # Next.js App Router app
│   ├── app/
│   │   ├── (marketing)/      # Landing/marketing routes
│   │   ├── (rooms)/          # App routes (e.g. create, room)
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/               # shadcn components
│   │   └── ...
│   ├── lib/
│   │   ├── api-client.ts     # Axios instance, base URL, interceptors
│   │   ├── api/              # API functions (e.g. issue-report-api.ts)
│   │   └── hooks/            # Custom hooks (e.g. use-generate-quiz style)
│   ├── types/                # TypeScript types (e.g. issue.ts)
│   ├── package.json
│   └── next.config.ts
├── backend/                  # FastAPI + LangGraph backend
│   ├── app/
│   │   ├── agents/           # LangGraph node logic (welcome, issue_filler, issue_reporting)
│   │   ├── graph/            # StateGraph definition, build_graph, routing
│   │   ├── models/           # Pydantic models & state TypedDict
│   │   ├── prompts/          # System/user prompts per agent
│   │   ├── routers/          # FastAPI routers (e.g. chat, issues)
│   │   ├── shared_services/  # llm.py, db.py, logger_setup
│   │   └── tools/            # LangGraph tools (db_tools)
│   ├── main.py               # FastAPI app, CORS, include_router
│   ├── requirements.txt
│   └── .env (from env.example)
├── db.sql                    # PostgreSQL schema (issues, etc.)
├── docs/
│   └── BUILDING_KUNANI_END_TO_END.md
└── README.md
```

### Tech Stack Summary

| Layer        | Technology |
|-------------|------------|
| Frontend    | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS, shadcn/ui (Radix), Axios, Zustand |
| Backend     | Python 3.9+, FastAPI, LangGraph, Pydantic, Instructor, OpenAI/OpenRouter/Gemini clients |
| Database    | PostgreSQL (issues table; LangGraph checkpointer tables optional) |
| API         | REST; JSON; frontend uses `NEXT_PUBLIC_API_URL` and Axios |

---

## Chapter 2: Project Setup & Environment

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend)
- PostgreSQL
- Git

### Backend Setup

1. **Create and activate a virtual environment**

   Windows (PowerShell):
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

   Linux/Mac:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database**
   - Create database and user (e.g. `kunani`, `kunani_user`).
   - Run schema: `psql -U kunani_user -d kunani -f db.sql`
   - Or use `python setup_db.py` if provided.

4. **Environment**
   ```bash
   cp env.example .env
   ```
   Set in `.env`:
   - `DATABASE_URL` (for app DB and optional LangGraph checkpointer)
   - `OPENAI_API_KEY` or `OPENROUTER_API_KEY` (and optional `GOOGLE_API_KEY` for Gemini)
   - Optional: Langfuse keys for observability.

### Frontend Setup (When You Add It)

1. From repo root: `cd frontend`
2. `npm install`
3. Create `.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000` (or your backend URL).

### Running Backend Only (Current Kunani)

From the **backend** directory (or repo root with backend on `PYTHONPATH`):

```bash
# From repo root (recommended)
cd kunani
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Or run the terminal conversation loop (no API):

```bash
python main.py
```

---

## Chapter 3: The LLM Service (`llm.py`)

### Purpose

A **single shared service** for all LLM calls: one interface, multiple providers (OpenAI, OpenRouter, Gemini). Same idea as in Trivia Pals (maswali backend) and current Kunani.

### Location

`backend/app/shared_services/llm.py`

### Design

- **Client caching**: One client per provider (e.g. OpenAI, OpenRouter, Gemini), created once and reused.
- **Unified function**: e.g. `call_llm_api(messages, model=..., provider=..., response_format=..., temperature=..., max_tokens=...)`.
- **Structured output**: Use Pydantic models with Instructor (OpenAI/OpenRouter) or provider-specific JSON mode (e.g. Gemini).
- **Error handling**: Log and re-raise; no silent failures.

### Signature (Concept)

```python
def call_llm_api(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    response_format: Optional[BaseModel] = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    fallback_providers: Optional[List[str]] = None
) -> Any:
```

- `messages`: `[{"role": "system"|"user"|"assistant", "content": "..."}]`
- `provider`: e.g. `"openai"`, `"openrouter"`, `"gemini"`.
- `response_format`: Pydantic model for structured output when supported.

### Usage in Agents

Agents import and call this; they do not instantiate LLM clients themselves:

```python
from app.shared_services.llm import call_llm_api

handoff = call_llm_api(
    messages=messages,
    provider="openrouter",
    model="tngtech/deepseek-r1t-chimera:free",
    response_format=WelcomeHandoffResponse,
    temperature=0.3,
)
```

---

## Chapter 4: Data Models with Pydantic

### Purpose

- **Structured outputs**: Every agent response that the app relies on is a Pydantic model so the code never assumes raw text.
- **State shape**: LangGraph state is defined with a TypedDict (and optionally Pydantic) so the graph and nodes share a clear contract.

### Location

`backend/app/models/najua_models.py` (Kunani naming; you can keep or align with your module names).

### Handoff Models

Used for routing between agents. Each agent returns a handoff model that includes:

- `agent`: next agent (e.g. `"issue_filler_agent"`, `"issue_reporting_agent"`, `"respond_to_user_agent"`, `"welcome_agent"`).
- `reasoning`: short explanation.
- `message_to_agent`: optional context for the next agent.
- `message_to_user`: optional reply to show the user (e.g. when handing to `respond_to_user_agent`).
- `agent_after_human_response`: which agent handles the next user message.

Examples (match your current Kunani names):

- `WelcomeHandoffResponse`
- `IssueFillerHandoffResponse`
- `IssueReportingHandoffResponse`

Use `Literal` for agent names and `model_validator` where needed (e.g. clear `message_to_user` when not handing to `respond_to_user_agent`).

### Issue Models

- **Issue Filler output**: e.g. `IssueFillerResponse` (single issue fields: type, description, location, date, time, severity) and `IssuesFillerResponse` (list of issues + message_to_user + suggested_handoff).
- **Stored issue**: e.g. `Issue` (status, type, description, location, date, time, severity) for in-state and DB representation.

### State Model

- **NajuaState** (TypedDict, `total=False`):
  - `conversation_history`: `List[Dict[str, str]]` (role + content).
  - `current_node`: current agent name.
  - `handoff_decision`: last handoff (e.g. `WelcomeHandoffResponse | IssueReportingHandoffResponse | IssueFillerHandoffResponse`).
  - `current_issues`: `Optional[List[Issue]]`.

All agent nodes read and update this state; the graph routes based on `handoff_decision`.

---

## Chapter 5: Database Schema & DB Service

### Schema (`db.sql`)

- **issues** table**: `id`, `issue_id` (unique), `title`, `description`, `status`, `priority`, `category`, `tags`, `created_at`, `updated_at`, `resolved_at`, `metadata` (JSONB).
- Indexes on `issue_id`, `status`, `created_at`.
- Trigger to keep `updated_at` in sync.

LangGraph’s PostgresSaver (if used) creates its own checkpoint tables; no need to add them to `db.sql`.

### DB Service (`app/shared_services/db.py`)

- Connection using `DATABASE_URL` or `PGHOST`, `PGDATABASE`, etc.
- CRUD-style functions used by both the API and the tools:
  - `save_issue(issue_data)` → insert and return saved issue.
  - `get_issue(issue_id)` → one issue or None.
  - `get_all_issues(limit, status=None)` → list of issues.
  - `update_issue_status(issue_id, status)` → updated issue or None.

Use the same patterns as in Kunani/Trivia Pals: parameterized queries, no raw string interpolation, basic error handling and logging.

---

## Chapter 6: LangGraph Tools

### Purpose

Tools give the graph (and agents) a fixed, validated way to touch the database instead of ad-hoc SQL. Same idea as Kunani’s `app/tools/db_tools.py`.

### Location

`backend/app/tools/db_tools.py`

### Tool Definitions

- **Inputs**: Pydantic models (e.g. `SaveIssueInput`, `GetIssueInput`, `GetIssuesInput`, `UpdateIssueStatusInput`) with `Field(..., description="...")` so the schema is clear for humans and for future tool-calling agents.
- **Tools**: Use `@tool(args_schema=...)` (LangChain/LangGraph style) and call the shared DB service (`save_issue`, `get_issue`, etc.).

Example tools:

1. **save_issue_tool** – title, description, status, priority, category, tags, metadata → save and return issue (e.g. with generated `issue_id`).
2. **get_issue_tool** – issue_id → one issue or error.
3. **get_all_issues_tool** – limit, optional status → list of issues.
4. **update_issue_status_tool** – issue_id, status → updated issue.

Return consistent structures (e.g. `{success, data | error}`) and handle exceptions inside the tool so the graph sees a predictable shape.

---

## Chapter 7: LangGraph Workflow Design

### Concepts

- **State**: One shared state (e.g. `NajuaState`) passed to every node.
- **Nodes**: Python functions that take state, call LLM/tools, update state, return state.
- **Edges**: Define flow: `START` → first node; then conditional edges based on `handoff_decision.agent` (and optionally `agent_after_human_response` for entry).
- **Entry point**: Dynamic: e.g. `determine_entry_point(state)` uses `handoff_decision.agent_after_human_response` so the next user message goes to the right agent; otherwise start at `welcome_agent`.

### Graph Layout (Kunani)

- **Nodes**: `welcome_agent`, `issue_filler_agent`, `issue_reporting_agent`.
- **Routing**: After each agent, read `state["handoff_decision"].agent` and route to that node or `END` (e.g. when `respond_to_user_agent` or user must reply).
- **Entry**: `add_conditional_edges(START, determine_entry_point, {"welcome_agent": "welcome_agent", "issue_filler_agent": "issue_filler_agent", "issue_reporting_agent": "issue_reporting_agent", ...})`.

### Location

`backend/app/graph/` – e.g. `najua_graph.py` or `najua_graph_with_langgraph_welcome.py` depending on whether the welcome agent is a subgraph or a single node.

### Build and Run

- `build_graph()` (or `build_graph_with_langgraph_welcome()`) builds the `StateGraph(NajuaState)`, adds nodes and edges, returns `workflow.compile()`.
- Optional: `workflow.compile(checkpointer=PostgresSaver.from_conn_string(...))` for persistence.
- Invoke: `await graph.ainvoke(state)` or `graph.ainvoke(state, config={"configurable": {"thread_id": "..."}})` when using a checkpointer.

---

## Chapter 8: Building the Agents

### Welcome Agent

- **Role**: Triage; decide whether the user wants to report an issue, fill details, or just chat.
- **Input**: `conversation_history` (and full state if needed).
- **Output**: A handoff model (e.g. `WelcomeHandoffResponse`) with `agent`, `message_to_user`, `agent_after_human_response`.
- **Implementation**: Build a system prompt (in `app/prompts/welcome_prompt.py`) that explains routing rules; call `call_llm_api(..., response_format=WelcomeHandoffResponse)`; return the parsed object. In the graph node, set `state["handoff_decision"]` and append `message_to_user` to `conversation_history` if present.

### Issue Filler Agent

- **Role**: Collect issue details (type, description, location, date, time, severity) over one or more turns.
- **Input**: `conversation_history`, `current_issues`.
- **Output**: e.g. `IssuesFillerResponse` (updated issues + message_to_user + suggested_handoff) and a handoff (e.g. `IssueFillerHandoffResponse`) for routing.
- **Implementation**: Prompt in `app/prompts/issue_filler_prompt.py`; LLM returns structured issue fields; update `state["current_issues"]`; decide handoff (continue_filling vs issue_reporting_agent vs welcome_agent vs respond_to_user_agent). No direct DB write here — only state.

### Issue Reporting Agent

- **Role**: Persist completed issues and confirm to the user.
- **Input**: `conversation_history`, `current_issues`.
- **Output**: Handoff (e.g. `IssueReportingHandoffResponse`) and optional `message_to_user`.
- **Implementation**: Use `save_issue_tool` (or direct `save_issue`) for each completed issue in `current_issues`; then clear or mark them in state; set handoff and optional user message. Prompt in `app/prompts/issue_reporting_prompt.py`.

All agents use the shared `llm.py` and the same handoff/state patterns as in the current Kunani codebase.

---

## Chapter 9: Memory & Checkpointing

### Why

- Multi-turn conversations: the graph must remember `conversation_history`, `current_issues`, and the last `handoff_decision`.
- Without checkpointing: state lives only in memory; restart loses context.
- With checkpointing: state is stored in PostgreSQL after each step and can be loaded by `thread_id`.

### How (LangGraph)

- Use `PostgresSaver.from_conn_string(DATABASE_URL)` and pass it to `workflow.compile(checkpointer=...)`.
- On each `ainvoke`, pass `config={"configurable": {"thread_id": "<user_or_session_id>"}}`. LangGraph will read/write checkpoint data so the next invocation continues from the last state.

### State vs Checkpointer

- **State**: The in-memory structure (e.g. `NajuaState`) that nodes read and update.
- **Checkpointer**: Persists that state (and optionally message history) so it survives restarts and is keyed by `thread_id`.

See Kunani’s `TOOLS_AND_MEMORY.md` for tool + checkpointer usage in the same project.

---

## Chapter 10: Backend API with FastAPI

### Layout (Like Trivia Pals Backend)

- **Entry**: `backend/main.py` – create FastAPI app, add CORS (allow frontend origin), include routers.
- **Routers**: Under `backend/app/routers/` (e.g. `chat.py`, `issues.py`). Each router uses a prefix and tags.

### CORS

- Allow the frontend origin (e.g. `http://localhost:3000`) and any production domain.
- Allow credentials if you use cookies/auth later.

### Example Endpoints for Kunani

- **POST /report/** or **POST /chat/** – receive user message (and optional session/thread_id); load or create state; run `graph.ainvoke(state, config=...)`; return assistant message and updated state/session info.
- **GET /issues/** – list issues (optional filters); call `get_all_issues` or a service that uses it.
- **GET /issues/{issue_id}** – get one issue; call `get_issue`.

Use Pydantic request/response models so the API contract is clear and validated.

### Running the API

From repo root (with backend on path):

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Or from inside `backend` with proper `PYTHONPATH` so that `backend` is the package name.

---

## Chapter 11: Frontend with Next.js, React & shadcn

### Structure (Like Trivia Pals Frontend)

- **App Router**: `app/(marketing)` for landing, `app/(rooms)` for app pages (e.g. create, report, list).
- **Components**: Reusable UI in `components/`; shadcn in `components/ui/`.
- **API layer**: `lib/api-client.ts` – Axios instance with `baseURL: process.env.NEXT_PUBLIC_API_URL`, timeouts, and response/error interceptors. Thin functions in `lib/api/` (e.g. `reportIssue`, `listIssues`) that call this client.
- **Types**: `types/issue.ts` (or similar) for request/response shapes.
- **State**: Use Zustand only where you need cross-component client state (e.g. selected issue, modal open); otherwise local state and server state (e.g. React Query if you add it).

### Key Packages

- Next.js 16, React 19, TypeScript.
- Tailwind CSS, shadcn/ui (Radix primitives), Tailwind-based theme.
- Axios for HTTP; optional: TanStack Query for server state.

### Flows to Implement

1. **Report flow**: Form or chat UI → collect message (and optional session id) → POST to backend `/report/` or `/chat/` → show assistant reply and optionally continue conversation (same thread_id).
2. **List issues**: GET `/issues/` → display in a table or cards.
3. **Issue detail**: GET `/issues/{id}` → show one issue.

Keep the same patterns as Trivia Pals: api-client base URL, error handling in interceptors, typed requests/responses.

---

## Chapter 12: End-to-End Flow & Running the App

### Happy Path

1. User opens frontend, goes to “Report issue”.
2. User sends a message (e.g. “I want to report a pothole”).
3. Frontend POSTs to backend with message (and optional thread_id).
4. Backend loads state (or creates new) for that thread_id, appends user message to `conversation_history`, runs `graph.ainvoke(state, config={"configurable": {"thread_id": thread_id}})`.
5. Welcome agent runs, returns handoff to `issue_filler_agent` (and possibly a message_to_user).
6. Issue filler runs, updates `current_issues`, may ask for more details or hand off to `issue_reporting_agent`.
7. Issue reporting runs, calls `save_issue_tool` for completed issues, returns confirmation and handoff (e.g. to `respond_to_user_agent` or `welcome_agent`).
8. Backend returns the last assistant message and any session/state info the frontend needs.
9. Frontend shows the reply; user can send another message (same thread_id) to continue.

### Running Locally

- **Backend**: `uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload` (from repo root).
- **Frontend**: `cd frontend && npm run dev` (e.g. port 3000).
- **Database**: PostgreSQL running; `DATABASE_URL` and `NEXT_PUBLIC_API_URL` set correctly.

---

## Chapter 13: Observability & Monitoring (Langfuse)


### Why observability

- **Trace agent flow**: See which node ran, what handoff was chosen, and what state changed.
- **LLM usage**: Token counts, latency, cost per provider/model.
- **Debugging**: When the graph misroutes or the LLM returns bad structure, traces show where it broke.
- **Production**: Alerts on errors, dashboards for cost and latency.

### How (Langfuse)

- **Setup**: Install Langfuse SDK; set `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` in `.env` (cloud or self-hosted).
- **Instrumentation**: Use `@observe()` on agent functions and/or a LangGraph callback handler so each node and LLM call is recorded.
- **Viewing**: Use the Langfuse UI to inspect traces, spans, and (if configured) scores/evals.

Use one observability layer (e.g. Langfuse), same teaching style (show errors, production-first).

---

## Chapter 14: Deployment & Production

### Backend

- Deploy the FastAPI app (e.g. Railway, Render, or a VPS) with:
  - Production `DATABASE_URL`.
  - Production env vars for LLM keys and optional Langfuse.
  - Single process or multiple workers; if using sync LLM calls, consider async or worker count to avoid blocking (as in the Trivia Pals notes).
- Expose the app on a public URL and set CORS to allow the frontend origin.

### Frontend

- Build: `npm run build`. Deploy to Vercel, Netlify, or static host.
- Set `NEXT_PUBLIC_API_URL` to the production backend URL.

### Database

- Use a managed PostgreSQL instance; run `db.sql` (and migrations if you add any). Ensure the backend can reach it (security groups, connection string).

### Checklist

- [ ] Env vars set in production (no secrets in repo).
- [ ] CORS restricted to your frontend (and any mobile app) origin.
- [ ] Health endpoint (e.g. `GET /`) for monitoring.
- [ ] Logging and error handling in place; optional Langfuse for traces.

---

## References

- **Kunani (current)**: `app/` backend, `main.py` conversation loop, `najua_models.py`, `najua_graph_with_langgraph_welcome.py`, `db_tools.py`, `TOOLS_AND_MEMORY.md`.
- **Trivia Pals**: `frontend/` (Next.js, shadcn, api-client, create flow), `maswali/backend/` (FastAPI, routers, LangGraph, llm, Pydantic).

---

*This guide is intended for the Agentic AI e2e YouTube series and for readers who want to see how Kunani is built end-to-end using the same principles and stack as the reference projects.*
