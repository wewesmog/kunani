# Tools and Memory Implementation

## Tools Created

I've created LangGraph-compatible tools in `app/tools/db_tools.py`:

### 1. `save_issue_tool`
- **Purpose**: Save new issues to the database
- **Input**: title, description, status, priority, category, tags, metadata
- **Output**: Success status and saved issue data
- **Usage**: Agents can call this tool to persist issues

### 2. `get_issue_tool`
- **Purpose**: Retrieve a specific issue by ID
- **Input**: issue_id
- **Output**: Issue data or error message
- **Usage**: Look up existing issues

### 3. `get_all_issues_tool`
- **Purpose**: List multiple issues with optional filtering
- **Input**: limit, status (optional filter)
- **Output**: List of issues
- **Usage**: Query issues by status or get recent issues

### 4. `update_issue_status_tool`
- **Purpose**: Update issue status
- **Input**: issue_id, new status
- **Output**: Updated issue data
- **Usage**: Change issue lifecycle state

### Integration
- Tools are registered in the graph via `ToolNode`
- Available to all agents in the workflow
- Tools use structured input/output with Pydantic schemas
- All tools return consistent response format with success/error handling

## Memory Implementation

### 1. PostgreSQL Checkpointer (State Persistence)
- **Location**: `app/graph/issue_graph.py`
- **Implementation**: `PostgresSaver` from LangGraph
- **Purpose**: Persists conversation state across runs
- **Tables**: 
  - `checkpoints` - Stores graph state snapshots
  - `checkpoint_blobs` - Stores channel-specific state data
- **Configuration**: Set `DATABASE_URL` in `.env`
- **Usage**: Automatically saves/loads state using thread_id

### 2. State Messages (Conversation Memory)
- **Location**: `IssueState` model in `app/models/issue_models.py`
- **Field**: `messages: Annotated[List[Dict[str, str]], "add"]`
- **Purpose**: Stores conversation history within state
- **Format**: List of message dicts with `role` and `content`
- **Usage**: Agents append messages to track conversation flow

### 3. How Memory Works

#### Checkpointer Memory:
```python
# In graph compilation
checkpointer = PostgresSaver.from_conn_string(db_url)
workflow.compile(checkpointer=checkpointer)

# When invoking with memory
config = {"configurable": {"thread_id": "user_session_1"}}
result = await graph.ainvoke(state, config=config)
```

#### State Messages:
- Agents append messages during execution
- Messages track: user inputs, agent actions, tool results, errors
- Persisted automatically via checkpointer
- Can be retrieved in subsequent runs using same thread_id

### 4. Database Schema
The `db.sql` includes:
- `issues` table - Main data storage
- **Note**: LangGraph's `PostgresSaver` automatically creates `checkpoints` and `checkpoint_blobs` tables when initialized - no manual creation needed

## Usage Example

```python
# Tools can be called by agents
from app.tools.db_tools import save_issue_tool

result = save_issue_tool.invoke({
    "title": "Bug in login",
    "description": "Users cannot log in",
    "priority": "high"
})

# Memory persists across runs
config = {"configurable": {"thread_id": "session_123"}}
state1 = await graph.ainvoke(initial_state, config=config)
# Later...
state2 = await graph.ainvoke(new_state, config=config)  # Loads previous state
```

## Benefits

1. **Tools**: Agents can interact with database without direct DB calls
2. **Memory**: Conversations persist across sessions
3. **Observability**: Langfuse tracks tool usage and memory state
4. **Scalability**: Checkpointer supports concurrent sessions via thread_id

