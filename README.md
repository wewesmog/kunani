# Kunani - Issue Tracking System MVP

A no-nonsense issue tracking system built with LangGraph and Langfuse.

## Documentation

| Link | Description |
|------|-------------|
| **[Building Kunani end-to-end](docs/BUILDING_KUNANI_END_TO_END.md)** | Chaptered guide (setup → LLM → models → DB → tools → graph → agents → API → frontend → observability → deployment). For the [Agentic AI e2e](https://youtube.com/@agenticaie2e) YouTube series. |
| [Tools & memory](TOOLS_AND_MEMORY.md) | How tools and PostgreSQL checkpointer work in this repo. |

## Features

- Create and track issues
- AI-powered issue analysis and categorization
- Database persistence with LangGraph tools
- LangGraph workflow orchestration with memory
- Langfuse observability
- Conversation memory via PostgreSQL checkpointer

## Setup

1. Create and activate virtual environment:

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up database:
```bash
# Create database and user
createdb kunani
createuser kunani_user
# Set password (use psql or your DB admin tool)

# Run schema (LangGraph checkpoint tables are auto-created)
psql -U kunani_user -d kunani -f db.sql
```

Or use the setup script:
```bash
python setup_db.py
```

4. Configure environment:
```bash
cp env.example .env
# Edit .env with your credentials
# IMPORTANT: Set DATABASE_URL for memory/checkpointing
```

5. Run:
```bash
python main.py
```

## Usage

The terminal interface provides options to:
1. Create new issues
2. List all issues
3. View specific issue
4. Update issue status

## Architecture

### Tools
- `save_issue_tool` - Save new issues to database
- `get_issue_tool` - Retrieve issue by ID
- `get_all_issues_tool` - List issues with filtering
- `update_issue_status_tool` - Update issue status

### Memory
- **PostgreSQL Checkpointer**: Persists conversation state across runs
- **State Messages**: Conversation history stored in state
- Set `DATABASE_URL` in `.env` to enable memory persistence

### Structure

- `app/models/` - Pydantic models and TypedDict state
- `app/agents/` - LangGraph node functions
- `app/graph/` - Graph definition with tools and memory
- `app/tools/` - LangGraph tools for DB operations
- `app/shared_services/` - DB, LLM, logger utilities
- `db.sql` - Database schema (issues + checkpoint tables)
- `main.py` - Terminal interface

## Memory Configuration

To enable memory persistence, set `DATABASE_URL` in your `.env`:
```
DATABASE_URL=postgresql://kunani_user:kunani_password@localhost:5432/kunani
```

The checkpointer automatically creates and manages checkpoint tables for conversation state.
