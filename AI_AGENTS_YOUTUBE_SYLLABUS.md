# AI Agents YouTube Channel Syllabus
## "Building Production-Grade AI" - A Comprehensive Guide

**Channel Philosophy:** This isn't just tutorials—this is **Building Production-Grade AI**. Most channels show toy examples. We build real systems that work in production, using actual projects like Mwalimu, Trivia Pals, Kunani, and XPChex.

**Teaching Style:**
- **Show the Errors**: Don't edit out where code crashes. Viewers learn more from watching you debug a `PydanticValidationError` than watching perfect code.
- **Kenyan/African Context**: Use local examples (M-Pesa receipts, Kenyan history for trivia). Makes content relatable and unique in a sea of generic "US-centric" tutorials.
- **Production-First**: Every example is production-ready, not a toy. Real error handling, real deployment, real monitoring.

---

## **BUILD KUNANI END-TO-END: 12-Video Series**

**What We're Building:** Kunani - A production-grade civic issue tracking system (like SeeClickFix/CivicPlus) where citizens report non-emergency issues to government. Built with LangGraph, multi-agent architecture, and PostgreSQL.

**Approach:** Each video introduces design elements as we need them, then we build that piece. By the end, you'll have a complete, deployable system.

**Framework: LangGraph** - Orchestration framework for multi-agent systems.

**LLM Access:** Custom `llm.py` service supporting any provider (Gemini, OpenAI, Anthropic, OpenRouter).

---

## **VIDEO 1: Building the LLM Service Foundation (`llm.py`)**

### Objective
Create a unified LLM service that works with any provider. This is the foundation Kunani uses for all AI calls.

### Design We'll Introduce
- **Why `llm.py`?** Single interface for multiple LLM providers
- **Architecture**: Client caching, provider abstraction, error handling
- **What we need**: Support for Gemini, OpenAI, OpenRouter with structured outputs

### What We Build
`app/shared_services/llm.py` - Multi-provider LLM service

### Content Structure

**1. The Problem: Multiple LLM Providers (10 min)**
- Different APIs (Gemini vs OpenAI vs OpenRouter)
- Different response formats
- Need unified interface
- **Design Decision**: One service, multiple providers

**2. Building the Service Structure (15 min)**
- Client caching pattern
- Provider detection
- Error handling
- Code structure:
  ```python
  # app/shared_services/llm.py
  def call_llm_api(
      messages: List[Dict[str, str]],
      model: Optional[str] = None,
      provider: Optional[str] = None,
      response_format: Optional[BaseModel] = None,
      temperature: float = 0.3,
      max_tokens: int = 2000
  ) -> Any:
  ```

**3. Implementing Gemini Support (15 min)**
- Google Generative AI SDK
- JSON mode for structured outputs
- Error handling

**4. Implementing OpenAI Support (15 min)**
- OpenAI SDK
- Instructor for structured outputs
- Error handling

**5. Implementing OpenRouter Support (10 min)**
- OpenAI-compatible API
- Multiple models
- Error handling

**6. Testing the Service (10 min)**
- Test with each provider
- Test structured outputs
- **Show errors**: Invalid API keys, rate limits, etc.

**Key Takeaways:**
- Unified interface = Flexibility
- Client caching = Performance
- Error handling = Production-ready
- This service powers all Kunani agents

---

---

## **VIDEO 2: Structured Outputs & Data Models (Pydantic for Kunani)**

### Objective
Learn Pydantic for structured outputs. Build all the data models Kunani needs for agents, handoffs, and issues.

### Design We'll Introduce
- **Kunani's Data Models**: What data structures we need
- **Agent Handoff Models**: How agents communicate
- **Issue Models**: How we represent civic issues
- **State Model**: How LangGraph manages state

### What We Build
`app/models/najua_models.py` - All Pydantic models for Kunani

### Content Structure

**1. Why Structured Outputs? (10 min)**
- LLMs output text, we need structured data
- Pydantic = Type-safe validation
- **Design**: All agent responses must be structured

**2. Building Handoff Models (20 min)**
- **WelcomeHandoffResponse**: Welcome agent's routing decision
  ```python
  class WelcomeHandoffResponse(BaseModel):
      agent: Literal["issue_reporting_agent", "issue_filler_agent", "respond_to_user_agent"]
      reasoning: str
      message_to_user: Optional[str]
      agent_after_human_response: Literal[...]
  ```
- **IssueFillerHandoffResponse**: Issue filler's routing decision
- **IssueReportingHandoffResponse**: Issue reporting's routing decision
- **Design Decision**: Each agent returns structured handoff decisions

**3. Building Issue Models (15 min)**
- **IssueFillerResponse**: Single issue data
  ```python
  class IssueFillerResponse(BaseModel):
      issue_type: Optional[Literal["Infrastructure", "Education", ...]]
      issue_description: Optional[str]
      issue_location: Optional[str]
      issue_date: Optional[str]
      issue_time: Optional[str]
      issue_severity: Optional[Literal["low", "medium", "high", "critical"]]
  ```
- **IssuesFillerResponse**: Multiple issues + handoff suggestion
- **Issue**: Complete issue model (for database)

**4. Building State Model (15 min)**
- **NajuaState**: LangGraph state structure
  ```python
  class NajuaState(TypedDict, total=False):
      conversation_history: List[Dict[str, str]]
      current_node: Optional[str]
      handoff_decision: Optional[Union[...]]
      current_issues: Optional[List[Issue]]
  ```
- **Design**: State is shared memory between agents

**5. Validation & Error Handling (10 min)**
- Field validation
- Model validators
- Error messages
- **Show errors**: Invalid data, missing fields

**Key Takeaways:**
- Pydantic = Type safety
- Structured outputs = Reliable agents
- State = Shared memory
- All Kunani agents use these models

### Content Structure

**1. Choosing an LLM Provider (10 min)**
- **Options**: Gemini, OpenAI, Anthropic, OpenRouter, etc.
- **Considerations**: Cost, latency, context window, multimodal support
- **Example - Gemini Flash**: Fast, cheap, massive context (1M tokens), multimodal
- **Example - GPT-4o-mini**: Good reasoning, OpenAI ecosystem
- **Key Point**: Choose based on your needs. We'll show patterns that work with any LLM.

**2. Setting Up LLM Access (10 min)**
- **Pattern 1: Direct API** (example with Gemini):
  ```bash
  pip install google-generativeai python-dotenv
  ```
  ```python
  import google.generativeai as genai
  import os
  from dotenv import load_dotenv
  
  load_dotenv()
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  model = genai.GenerativeModel("gemini-1.5-flash")
  ```
- **Pattern 2: Custom Service** (like Kunani's `llm.py`):
  ```python
  from app.shared_services.llm import call_llm_api
  
  # Works with any provider
  response = call_llm_api(
      messages=[{"role": "user", "content": "..."}],
      provider="gemini",  # or "openai", "anthropic", etc.
      model="gemini-1.5-flash"
  )
  ```

**3. Multimodality - The Game Changer (15 min)**
- **Explanation to Include:**
  > "Multimodality: We don't need OCR (Optical Character Recognition) libraries anymore. Models like Gemini can 'see' images natively. We just pass the image bytes directly to the API. No preprocessing, no Tesseract, no PIL manipulation. This is revolutionary for building agents that interact with real-world data."
- Code example (Gemini):
  ```python
  import PIL.Image
  
  # Load image
  img = PIL.Image.open("messy_desk.jpg")
  
  # Direct multimodal call
  response = model.generate_content([
      "Analyze this desk and list all items that need cleaning. Output as JSON.",
      img
  ])
  ```
- **Note**: Not all LLMs support multimodal. Check your provider's capabilities.

**4. Building the Desk Analyzer (20 min)**
- Complete script walkthrough
- Handling image input
- Parsing JSON response
- Error handling (show real errors!)

**5. Real-World Application (5 min)**
- How this pattern applies to:
  - Receipt scanning (M-Pesa receipts)
  - Document analysis
  - Quality control in manufacturing

**Hands-On Exercise:**
- Analyze a Kenyan receipt image
- Extract merchant name, amount, date
- Handle edge cases (blurry images, different formats)

**Key Takeaways:**
- Choose LLM based on needs (cost, latency, features)
- Direct API or custom service (llm.py) - both work
- Multimodality = No preprocessing needed (if supported)
- Production-ready from day one

---

---

## **VIDEO 3: LangGraph Basics & Kunani Workflow Design**

### Objective
Learn LangGraph fundamentals. Design Kunani's agent workflow - how agents hand off to each other.

### Design We'll Introduce
- **Kunani's Agent Architecture**: 3 agents + routing
- **Workflow Design**: 
  - Welcome Agent → Triage
  - Issue Filler Agent → Collect details
  - Issue Reporting Agent → Save to database
- **State Flow**: How state moves between agents
- **Routing Logic**: Conditional edges based on handoff decisions

### What We Build
Start `app/graph/najua_graph.py` - Basic graph structure

### Content Structure

**1. Kunani's Agent Architecture (15 min)**
- **Design Overview**:
  ```
  User Input
      ↓
  Welcome Agent (Triage)
      ↓
  ┌─────────────────┬──────────────────┐
  │                 │                  │
  Issue Filler    Issue Reporting    Respond to User
  (Collect)       (Save)             (Chat)
  ```
- **Agent Responsibilities**:
  - Welcome: Routes to right agent
  - Issue Filler: Collects issue details
  - Issue Reporting: Saves issues to DB

**2. LangGraph Core Concepts (20 min)**
- State (NajuaState)
- Nodes (agent functions)
- Edges (routing)
- Conditional routing

**3. Building Basic Graph Structure (20 min)**
- Create StateGraph
- Add nodes (stubs for now)
- Add edges
- Entry point logic
- Code:
  ```python
  # app/graph/najua_graph.py
  workflow = StateGraph(NajuaState)
  workflow.add_node("welcome_agent", welcome_agent_node)
  workflow.add_node("issue_filler_agent", issue_filler_agent_node)
  workflow.add_node("issue_reporting_agent", issue_reporting_agent_node)
  ```

**4. Routing Design (15 min)**
- **Design**: Each agent returns handoff decision
- Routing function: `route_after_agent()`
- Entry point: `determine_entry_point()`
- Conditional edges based on handoff

**5. Testing Basic Flow (10 min)**
- Test graph structure
- Test routing logic
- **Show errors**: Invalid routing, missing state

**Key Takeaways:**
- LangGraph = Orchestration
- State = Shared memory
- Routing = Agent handoffs
- This structure will hold all Kunani agents

### Content Structure

**1. The Problem: Parsing Hell (10 min)**
- **Explanation to Include:**
  > "The biggest bottleneck in AI engineering is 'parsing errors'. If the AI says 'Here is your JSON:', your code breaks. We solve this using Pydantic. Pydantic allows us to define a 'Data Schema' (a blueprint). We force the AI to adhere to this blueprint so our code never crashes. It's like having a bouncer at a club—only valid data gets in."

**2. Pydantic Basics (15 min)**
- Defining models:
  ```python
  from pydantic import BaseModel, Field
  from typing import Optional
  from datetime import datetime
  
  class ReceiptData(BaseModel):
      total_amount: float = Field(..., description="Total amount in KES")
      merchant: str = Field(..., description="Merchant name")
      date: str = Field(..., description="Date in YYYY-MM-DD format")
      items: Optional[list[str]] = Field(None, description="List of items purchased")
  ```
- Field validation
- Type coercion
- Error messages

**3. Structured Outputs (20 min)**
- **The Problem**: LLMs output text, but we need structured data
- **The Solution**: JSON mode + Pydantic validation
- **Pattern 1: Direct API** (example with Gemini):
  ```python
  from pydantic import ValidationError
  import json
  
  # Request JSON output
  response = model.generate_content(
      f"Extract receipt data. Output valid JSON matching this schema: {ReceiptData.model_json_schema()}",
      generation_config={"response_mime_type": "application/json"}
  )
  
  # Parse and validate
  try:
      data = json.loads(response.text)
      receipt = ReceiptData.model_validate(data)
  except (json.JSONDecodeError, ValidationError) as e:
      # Handle error - show this in video!
      print(f"Error: {e}")
  ```
- **Pattern 2: Using llm.py service** (works with any provider):
  ```python
  from app.shared_services.llm import call_llm_api
  
  receipt = call_llm_api(
      messages=[{"role": "user", "content": "Extract receipt data..."}],
      provider="gemini",  # or "openai", etc.
      model="gemini-1.5-flash",
      response_format=ReceiptData  # Pydantic model
  )
  # Already validated!
  ```
- **Show real errors**: Invalid JSON, missing fields, type mismatches

**4. Building the Receipt Parser (25 min)**
- Complete implementation
- Handling Kenyan receipts (M-Pesa, Naivas, etc.)
- Edge cases:
  - Different date formats
  - Currency symbols (KES, KSh)
  - Missing fields
- **Show real errors**: Invalid JSON, missing fields, type mismatches

**5. Production Patterns (10 min)**
- Retry logic for parsing failures
- Fallback strategies
- Logging validation errors
- Monitoring schema compliance

**Hands-On Exercise:**
- Parse 5 different receipt formats
- Handle all edge cases
- Build a validation report

**Key Takeaways:**
- Pydantic = Type-safe data validation
- Always validate LLM outputs
- Show errors, don't hide them
- Production = Error handling

---

### **Phase 2: The Agentic Shift (Framework-less Agents First)**
*Goal: Build agents with pure Python - no frameworks yet. Understand decision-making, state management, and tool calling from scratch. Then we'll see why LangGraph makes this easier.*

---

## **VIDEO 3: What is an Agent? (Framework-less First)**

### Objective
Design and set up Kunani's database. Create the schema for storing issues and LangGraph checkpoints.

### Design We'll Introduce
- **Database Schema**: Issues table structure
- **Fields Needed**: What data we store
- **Indexes**: Performance optimization
- **Checkpointing**: LangGraph memory tables (auto-created)

### What We Build
`db.sql` - Database schema
`app/shared_services/db.py` - Database connection & CRUD functions

### Content Structure

**1. Database Design (15 min)**
- **Issues Table Design**:
  ```sql
  CREATE TABLE issues (
      id SERIAL PRIMARY KEY,
      issue_id VARCHAR(255) UNIQUE NOT NULL,
      title VARCHAR(500) NOT NULL,
      description TEXT NOT NULL,
      status VARCHAR(50) DEFAULT 'open',
      priority VARCHAR(50) DEFAULT 'medium',
      category VARCHAR(100),
      tags TEXT[],
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      resolved_at TIMESTAMP,
      metadata JSONB DEFAULT '{}'::jsonb
  );
  ```
- **Design Decisions**: 
  - `issue_id` for unique tracking
  - `status` for workflow (open, in-progress, resolved, closed)
  - `metadata` JSONB for flexibility
  - Indexes for performance

**2. Building the Schema (20 min)**
- Create `db.sql`
- Add indexes
- Add triggers (auto-update `updated_at`)
- Test schema creation

**3. Database Service (`db.py`) (25 min)**
- Connection management
- CRUD functions:
  - `save_issue()` - Insert new issue
  - `get_issue()` - Get by ID
  - `get_all_issues()` - List with filtering
  - `update_issue_status()` - Update status
- Error handling
- Connection pooling considerations

**4. Testing Database Operations (10 min)**
- Test all CRUD operations
- Test error cases
- **Show errors**: Connection failures, constraint violations

**5. LangGraph Checkpointing (5 min)**
- **Design**: LangGraph auto-creates checkpoint tables
- No manual setup needed
- Just provide DATABASE_URL

**Key Takeaways:**
- Database = Persistent storage
- Schema design = Foundation
- CRUD functions = Data access layer
- This database stores all Kunani issues

### Content Structure

**1. Chains vs. Agents (15 min)**
- **Explanation to Include:**
  > "A Chain is a train on a track: Station A -> Station B -> Station C. It can't deviate. You write the code, and it follows exactly. An Agent is a taxi driver. You give it a goal ('Get me to the airport'), and it decides the route based on traffic (data). In LangGraph, we build the 'map' (Graph), but the AI drives the car. The agent decides which tools to use, when to loop back, and when to stop."

**2. Simple Chain Example (10 min)**
- Linear script (no LangGraph):
  ```python
  def weather_chain(location: str):
      # Always calls API, no decision
      weather = get_weather_api(location)
      return format_response(weather)
  ```
- Limitations: No decision-making, no memory, no adaptation

**3. Building Your First LangGraph Agent (25 min)**
- **Key Point**: LangGraph from the start - production-ready approach
- **Two ways to access LLMs in nodes:**
  
  **Pattern 1: Using llm.py service** (like Kunani):
  ```python
  from langgraph.graph import StateGraph, START, END
  from typing import TypedDict
  from app.shared_services.llm import call_llm_api
  
  class WeatherState(TypedDict):
      user_input: str
      intent: str
      weather_data: dict
      response: str
      memory: dict
  
  def classify_intent_node(state: WeatherState) -> WeatherState:
      # Using llm.py service - works with any provider
      intent = call_llm_api(
          messages=[{"role": "user", "content": f"Classify: {state['user_input']}"}],
          provider="gemini",  # or "openai", etc.
          model="gemini-1.5-flash"
      )
      state["intent"] = intent.strip()
      return state
  ```
  
  **Pattern 2: LangGraph's built-in LLM**:
  ```python
  from langchain_google_genai import ChatGoogleGenerativeAI
  from langchain_core.messages import HumanMessage
  
  def classify_intent_node(state: WeatherState) -> WeatherState:
      # LangGraph's built-in way
      llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
      response = llm.invoke([HumanMessage(content=f"Classify: {state['user_input']}")])
      state["intent"] = response.content.strip()
      return state
  ```
  
  **Complete example with llm.py**:
  ```python
  def get_weather_node(state: WeatherState) -> WeatherState:
      if state["memory"].get("last_location"):
          state["weather_data"] = state["memory"]["last_weather"]
      else:
          state["weather_data"] = get_weather_api(state["user_input"])
      return state
  
  def answer_node(state: WeatherState) -> WeatherState:
      response = call_llm_api(
          messages=[{"role": "user", "content": state["user_input"]}],
          provider="gemini",
          model="gemini-1.5-flash"
      )
      state["response"] = response
      return state
  
  # Build graph
  workflow = StateGraph(WeatherState)
  workflow.add_node("classify", classify_intent_node)
  workflow.add_node("get_weather", get_weather_node)
  workflow.add_node("answer", answer_node)
  
  workflow.add_edge(START, "classify")
  workflow.add_conditional_edges(
      "classify",
      lambda s: "get_weather" if "weather" in s["intent"] else "answer",
      {"get_weather": "get_weather", "answer": "answer"}
  )
  workflow.add_edge("get_weather", END)
  workflow.add_edge("answer", END)
  
  graph = workflow.compile()
  ```
- Decision logic with any LLM
- LangGraph state management
- Conditional routing
- **Both patterns work** - choose based on your needs

**4. Real Example: Mwalimu Routing Logic (10 min)**
- Preview of Mwalimu project
- How it routes: Math questions → Math Agent, History → History Agent
- LangGraph orchestration in action

**5. When to Use Agents vs. Chains (5 min)**
- Use Chains: Predictable workflows, no decisions needed
- Use Agents: Dynamic routing, tool selection, multi-step reasoning

**Hands-On Exercise:**
- Build a simple agent that decides when to use a calculator tool
- Add memory for previous calculations
- Test decision-making logic

**Key Takeaways:**
- Chains = Predictable, Agents = Adaptive
- Agents make decisions, chains follow scripts
- Memory enables context-aware decisions

---

---

## **VIDEO 5: Tools & Tool Calling (Database Tools for Kunani)**

### Objective
Deep dive into LangGraph - the framework for building production agents. Learn nodes, edges, state, and routing.

### The Build
A "Reflection Agent" that writes a tweet, critiques itself, and rewrites it until it's good. Built with LangGraph and Google Gemini.

### Content Structure

**1. LangGraph Core Concepts (20 min)**
- **Explanation to Include:**
  > "State: Think of State as a shared notebook passed around the room. Every 'Node' (worker) reads the notebook, adds their part, and passes it on. The notebook contains everything: conversation history, current task, intermediate results. In LangGraph, State is a TypedDict—Python's way of saying 'this dictionary has a specific structure.'"
  
  > "Nodes: These are just Python functions. One function writes the tweet, another critiques it. Each node receives the State, does its work (calling Gemini), updates the State, and returns it. No magic, just functions."
  
  > "Edges: The logic. 'If the critique is bad, go back to the writer node. If good, go to publish.' This conditional logic is the heartbeat of an agent. Without edges, you have a chain. With conditional edges, you have an agent."
  
  > "LLMs in Nodes: Inside each node, we call any LLM (via llm.py service or LangGraph's built-in). LangGraph orchestrates the flow, the LLM does the thinking."

**2. Defining State (10 min)**
- TypedDict example:
  ```python
  from typing import TypedDict, List, Dict, Optional
  
  class TweetState(TypedDict):
      conversation_history: List[Dict[str, str]]
      current_tweet: Optional[str]
      critique: Optional[str]
      iteration_count: int
      is_good_enough: bool
  ```
- Why TypedDict: Type hints, IDE support, validation

**3. Building Nodes (15 min)**
- Writer node (using llm.py service):
  ```python
  from app.shared_services.llm import call_llm_api
  
  def write_tweet_node(state: TweetState) -> TweetState:
      prompt = "Write a tweet about AI agents"
      
      # Using llm.py service - works with any provider
      tweet = call_llm_api(
          messages=[{"role": "user", "content": prompt}],
          provider="gemini",  # or "openai", etc.
          model="gemini-1.5-flash"
      )
      
      state["current_tweet"] = tweet
      state["iteration_count"] += 1
      return state
  ```
  
  **Or using LangGraph's built-in**:
  ```python
  from langchain_google_genai import ChatGoogleGenerativeAI
  from langchain_core.messages import HumanMessage
  
  def write_tweet_node(state: TweetState) -> TweetState:
      llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
      response = llm.invoke([HumanMessage(content="Write a tweet about AI agents")])
      state["current_tweet"] = response.content
      state["iteration_count"] += 1
      return state
  ```
- Critique node:
  ```python
  def critique_tweet_node(state: TweetState) -> TweetState:
      tweet = state["current_tweet"]
      critique = llm_call(f"Critique this tweet: {tweet}")
      state["critique"] = critique
      
      # Decide if good enough
      if "excellent" in critique.lower():
          state["is_good_enough"] = True
      else:
          state["is_good_enough"] = False
      return state
  ```

**4. Building the Graph (15 min)**
- Graph definition:
  ```python
  from langgraph.graph import StateGraph, START, END
  
  workflow = StateGraph(TweetState)
  workflow.add_node("write", write_tweet_node)
  workflow.add_node("critique", critique_tweet_node)
  
  # Edges
  workflow.add_edge(START, "write")
  workflow.add_conditional_edges(
      "critique",
      should_continue,  # Function that returns "rewrite" or "publish"
      {
          "rewrite": "write",  # Loop back
          "publish": END
      }
  )
  workflow.add_edge("write", "critique")
  
  graph = workflow.compile()
  ```
- Conditional routing function:
  ```python
  def should_continue(state: TweetState) -> str:
      if state["is_good_enough"]:
          return "publish"
      elif state["iteration_count"] >= 3:
          return "publish"  # Give up after 3 tries
      else:
          return "rewrite"
  ```

**5. Running the Graph (5 min)**
- Execution:
  ```python
  initial_state = {
      "conversation_history": [],
      "current_tweet": None,
      "critique": None,
      "iteration_count": 0,
      "is_good_enough": False
  }
  
  result = graph.invoke(initial_state)
  print(result["current_tweet"])
  ```

**6. Real Example: Kunani Graph Structure (10 min)**
- Show `app/graph/najua_graph.py`
- Explain node structure
- Show routing logic
- Show `app/shared_services/llm.py` - unified LLM service
- **Key Point**: Kunani uses LangGraph for orchestration, and calls LLMs via `llm.py` service inside the nodes. This pattern works with any LLM provider.

**Hands-On Exercise:**
- Build a reflection agent for code reviews
- Add max iteration limit
- Test the loop

**Key Takeaways:**
- State = Shared memory
- Nodes = Functions that update state
- Edges = Routing logic
- Conditional edges = Agent behavior

---

---

## **VIDEO 6: Memory & Persistence (Checkpointing for Kunani)**

### Objective
Add persistent memory to Kunani using LangGraph checkpointing. Users can resume conversations.

### Design We'll Introduce
- **Memory Design**: How Kunani remembers conversations
- **Checkpointing**: PostgreSQL-based persistence
- **Thread IDs**: User session management
- **State Persistence**: Automatic state saving

### What We Build
Add checkpointing to `app/graph/najua_graph.py`

### Content Structure

**1. Memory Design for Kunani (10 min)**
- **Problem**: Users report issues over multiple messages
- **Solution**: Checkpointing saves state after each step
- **Design**: Each user = thread_id, state persists in DB

**2. Setting Up Checkpointing (20 min)**
- PostgreSQL checkpointer
- Code:
  ```python
  from langgraph.checkpoint.postgres import PostgresSaver
  
  checkpointer = PostgresSaver.from_conn_string(
      os.getenv("DATABASE_URL")
  )
  
  graph = workflow.compile(checkpointer=checkpointer)
  ```
- Auto-created tables (checkpoints, checkpoint_blobs)

**3. Thread ID Management (15 min)**
- User sessions = thread_ids
- Resuming conversations
- Code:
  ```python
  config = {"configurable": {"thread_id": "user_123"}}
  result = graph.invoke(state, config=config)
  ```

**4. Testing Memory (15 min)**
- Start conversation
- Stop and resume
- Verify state persistence
- **Show errors**: Missing thread_id, DB connection issues

**5. Memory in Kunani Context (10 min)**
- How it works in issue reporting flow
- Multi-turn conversations
- State cleanup considerations

**Key Takeaways:**
- Checkpointing = Persistent memory
- Thread IDs = User sessions
- State = Conversation context
- Kunani remembers where users left off

### Content Structure

**1. What are Tools? (10 min)**
- Functions agents can call
- Examples: Database queries, API calls, file operations, calculations
- Tools vs. agents: Tools are stateless functions

**2. Creating LangGraph Tools (20 min)**
- Using `@tool` decorator:
  ```python
  from langchain_core.tools import tool
  from pydantic import BaseModel, Field
  
  class SaveIssueInput(BaseModel):
      title: str = Field(..., description="Issue title")
      description: str = Field(..., description="Issue description")
  
  @tool(args_schema=SaveIssueInput)
  def save_issue_tool(title: str, description: str) -> dict:
      """Save an issue to the database"""
      # Database logic
      return {"success": True, "issue_id": "..."}
  ```
- Input validation with Pydantic
- Tool descriptions (important for LLM understanding)

**3. Real Example: Database Tools from Kunani (20 min)**
- Code walkthrough: `app/tools/db_tools.py`
- Tools:
  - `save_issue_tool`
  - `get_issue_tool`
  - `get_all_issues_tool`
  - `update_issue_status_tool`
- Error handling in tools
- Tool composition

**4. Manual Tool Calling (15 min)**
- Agent decides to call tool, executes manually:
  ```python
  def agent_node(state: AgentState) -> AgentState:
      # Agent decides: Do I need to save?
      if should_save(state):
          result = save_issue_tool.invoke({
              "title": state["title"],
              "description": state["description"]
          })
          state["saved"] = True
      return state
  ```
- Full control over when/how tools are called

**5. Automatic Tool Calling with LangGraph (20 min)**
- Bind tools to LLM:
  ```python
  from langchain_google_genai import ChatGoogleGenerativeAI
  
  llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
  llm_with_tools = llm.bind_tools([save_issue_tool, get_issue_tool])
  
  # LLM automatically decides when to call tools
  response = llm_with_tools.invoke("Save an issue about broken streetlight")
  # Response includes tool calls!
  ```
- Tool execution in nodes:
  ```python
  def agent_node(state: AgentState) -> AgentState:
      llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
      llm_with_tools = llm.bind_tools([save_issue_tool])
      
      response = llm_with_tools.invoke(state["user_input"])
      
      # Check if LLM wants to call a tool
      if response.tool_calls:
          for tool_call in response.tool_calls:
              tool_name = tool_call["name"]
              tool_args = tool_call["args"]
              
              if tool_name == "save_issue_tool":
                  result = save_issue_tool.invoke(tool_args)
                  state["tool_result"] = result
      
      return state
  ```

**6. Tool Calling Patterns (10 min)**
- When to use manual vs. automatic
- Tool selection strategies
- Error handling
- Tool chaining

**Hands-On Exercise:**
- Create a calculator tool
- Create a weather API tool
- Build an agent that uses both
- Test automatic tool calling

**Key Takeaways:**
- Tools = Stateless functions agents can use
- Manual = Full control
- Automatic = LLM decides
- Always validate inputs
- Handle errors gracefully

---

---

## **VIDEO 7: Building the Welcome Agent (Triage & Routing)**

### Objective
Build Kunani's Welcome Agent - the entry point that triages user input and routes to the right agent.

### Design We'll Introduce
- **Welcome Agent Design**: Responsibilities and behavior
- **Routing Logic**: How it decides which agent to use
- **Prompt Design**: System prompt for triage
- **Handoff Patterns**: Structured handoff decisions

### What We Build
`app/agents/welcome_agent.py`
`app/prompts/welcome_prompt.py`

### Content Structure

**1. Welcome Agent Design (15 min)**
- **Responsibilities**:
  - Triage user input
  - Route to: Issue Filler, Issue Reporting, or Respond to User
  - Handle emergencies (reject, direct to emergency services)
  - Handle chitchat
- **Design Decision**: First point of contact, smart routing

**2. Building the Prompt (20 min)**
- System prompt design
- Routing instructions
- Emergency handling
- Code:
  ```python
  # app/prompts/welcome_prompt.py
  def get_welcome_prompt() -> str:
      return """
      You are an entry point to Najua, a system where citizens 
      in Kenya can post non-emergency issues...
      """
  ```

**3. Building the Agent Function (25 min)**
- Agent function structure
- Using `llm.py` service
- Structured output (WelcomeHandoffResponse)
- Code:
  ```python
  # app/agents/welcome_agent.py
  def welcome_agent(conversation_history: list) -> WelcomeHandoffResponse:
      prompt = get_welcome_prompt()
      messages = [{"role": "system", "content": prompt}] + conversation_history
      
      handoff_decision = call_llm_api(
          messages=messages,
          response_format=WelcomeHandoffResponse,
          provider="openrouter",
          model="tngtech/tng-r1t-chimera:free"
      )
      return handoff_decision
  ```

**4. Building the Graph Node (15 min)**
- Node function for LangGraph
- State updates
- Message handling
- Code:
  ```python
  def welcome_agent_node(state: NajuaState) -> NajuaState:
      handoff_decision = welcome_agent(state["conversation_history"])
      state["handoff_decision"] = handoff_decision
      # Add message to conversation
      return state
  ```

**5. Testing the Agent (10 min)**
- Test routing decisions
- Test emergency handling
- Test chitchat
- **Show errors**: Invalid routing, LLM failures

**Key Takeaways:**
- Welcome Agent = Smart router
- Structured handoffs = Reliable routing
- Prompt design = Agent behavior
- This is Kunani's entry point

### Content Structure

**1. The Memory Problem (10 min)**
- LLMs are stateless
- Each API call is independent
- Need persistence for real applications

**2. LangGraph Checkpointing (20 min)**
- **Explanation to Include:**
  > "LLMs are stateless—they have amnesia after every request. To fix this in LangGraph, we use a Checkpointer. It saves the 'State' (the notebook) to a database (like Postgres or just memory) after every step. When the user returns, we reload the notebook exactly where we left off. This is how Mwalimu remembers a student is struggling with Algebra."
- Setup:
  ```python
  from langgraph.checkpoint.postgres import PostgresSaver
  import os
  
  checkpointer = PostgresSaver.from_conn_string(
      os.getenv("DATABASE_URL")
  )
  
  graph = workflow.compile(checkpointer=checkpointer)
  ```
- Checkpoint tables (auto-created)

**3. Building the Tutor Bot (25 min)**
- State with student info:
  ```python
  class TutorState(TypedDict):
      conversation_history: List[Dict[str, str]]
      student_name: Optional[str]
      weak_subjects: List[str]
      current_topic: Optional[str]
  ```
- Agent that extracts and remembers:
  ```python
  def tutor_agent(state: TutorState) -> TutorState:
      # Extract student name from conversation
      if not state.get("student_name"):
          name = extract_name(state["conversation_history"])
          state["student_name"] = name
      
      # Remember weak subjects
      if "struggling with" in last_message:
          subject = extract_subject(last_message)
          if subject not in state["weak_subjects"]:
              state["weak_subjects"].append(subject)
      
      return state
  ```

**4. Resuming Conversations (15 min)**
- Loading previous state:
  ```python
  from langgraph.checkpoint.memory import MemorySaver
  
  # For development (in-memory)
  checkpointer = MemorySaver()
  
  # Run with thread_id (user session)
  config = {"configurable": {"thread_id": "student_123"}}
  result = graph.invoke(initial_state, config=config)
  
  # Later, resume
  result = graph.invoke(new_input, config=config)  # Loads previous state!
  ```

**5. Real Example: Mwalimu Memory (15 min)**
- How Mwalimu remembers:
  - Student progress
  - Weak topics
  - Learning style
- Code patterns from project
- **Key Point**: Memory is a LangGraph feature. We use any LLM for calls (via llm.py or built-in), but LangGraph handles the memory persistence.

**6. Production Considerations (10 min)**
- Thread IDs (user sessions)
- State cleanup (old conversations)
- Performance (checkpointing overhead)

**Hands-On Exercise:**
- Build tutor bot with memory
- Test conversation resumption
- Add state cleanup logic

**Key Takeaways:**
- Checkpointing = Persistent memory
- Thread IDs = User sessions
- State = Conversation context
- Production = Persistent state

---

### **Phase 3: Let's Build Together (Project Series)**
*Goal: Full-stack integration using your specific portfolio projects.*

---

---

## **VIDEO 8: Building the Issue Filler Agent (Collecting Issue Details)**

### Objective
Learn MCP - a protocol for connecting agents to external tools and data sources. Standardize how agents interact with databases, APIs, and services.

### Content Structure

**1. What is MCP? (10 min)**
- **Explanation to Include:**
  > "MCP (Model Context Protocol) is a standard way for AI agents to connect to external systems. Instead of writing custom code for each tool, MCP provides a protocol that any tool can implement. Think of it like USB - a standard connector that works with any device. Your agent can connect to databases, APIs, file systems, all through the same MCP interface."

**2. MCP Architecture (15 min)**
- MCP Servers: Tools that implement MCP protocol
- MCP Clients: Agents that use MCP servers
- Standardized interface for tools
- Benefits: Reusability, standardization, easier integration

**3. Setting Up MCP (15 min)**
- Install MCP SDK:
  ```bash
  pip install mcp
  ```
- Create an MCP server:
  ```python
  from mcp.server import Server
  from mcp.types import Tool
  
  server = Server("my-tools")
  
  @server.list_tools()
  async def list_tools() -> list[Tool]:
      return [
          Tool(
              name="save_issue",
              description="Save an issue to database",
              inputSchema={
                  "type": "object",
                  "properties": {
                      "title": {"type": "string"},
                      "description": {"type": "string"}
                  }
              }
          )
      ]
  
  @server.call_tool()
  async def call_tool(name: str, arguments: dict):
      if name == "save_issue":
          # Save logic
          return {"success": True}
  ```

**4. Using MCP in LangGraph (20 min)**
- Connect MCP server to LangGraph agent:
  ```python
  from mcp import ClientSession, StdioServerParameters
  from mcp.client.stdio import stdio_client
  
  # Connect to MCP server
  server_params = StdioServerParameters(
      command="python",
      args=["mcp_server.py"]
  )
  
  async with stdio_client(server_params) as (read, write):
      async with ClientSession(read, write) as session:
          # Get available tools
          tools = await session.list_tools()
          
          # Use in LangGraph node
          def agent_node(state: AgentState) -> AgentState:
              # Agent can use MCP tools
              result = await session.call_tool("save_issue", {
                  "title": state["title"],
                  "description": state["description"]
              })
              return state
  ```

**5. Real-World MCP Examples (15 min)**
- Database MCP server
- API MCP server
- File system MCP server
- Combining multiple MCP servers

**6. MCP vs. Direct Tool Calling (10 min)**
- When to use MCP: Multiple tools, standardization needed
- When to use direct: Simple, single-purpose tools
- Best practices

**Hands-On Exercise:**
- Create an MCP server for database operations
- Connect it to a LangGraph agent
- Test tool calling through MCP

**Key Takeaways:**
- MCP = Standard protocol for tools
- Enables reusable, standardized tool integration
- Works with LangGraph
- Production-ready pattern

---

---

## **VIDEO 9: Building the Issue Reporting Agent (Saving Issues)**

### Objective
Build Kunani's Issue Reporting Agent - saves completed issues to the database.

### Design We'll Introduce
- **Issue Reporting Design**: Final step in workflow
- **Tool Integration**: Using database tools
- **Status Management**: Updating issue status
- **Confirmation Flow**: User confirmation

### What We Build
`app/agents/issue_reporting_agent.py`
`app/prompts/issue_reporting_prompt.py`

### Content Structure

**1. Issue Reporting Agent Design (10 min)**
- **Responsibilities**:
  - Receive completed issues from Issue Filler
  - Save to database using tools
  - Confirm with user
  - Handle errors
- **Design**: Final step, uses tools

**2. Building the Prompt (15 min)**
- System prompt
- Issue review instructions
- Tool calling guidance
- Code:
  ```python
  # app/prompts/issue_reporting_prompt.py
  def get_issue_reporting_prompt(state: NajuaState) -> str:
      # Include current issues
      # Instructions for saving
  ```

**3. Building the Agent (25 min)**
- Agent function
- Tool calling logic
- Status updates
- Error handling
- Code:
  ```python
  # app/agents/issue_reporting_agent.py
  def issue_reporting_agent(conversation_history: list, state: NajuaState) -> IssueReportingHandoffResponse:
      # Get prompt
      # Call LLM for decision
      # If saving: call save_issue_tool
      # Update state
      # Return handoff
  ```

**4. Tool Integration (20 min)**
- Import tools
- Call `save_issue_tool`
- Handle tool results
- Update issue status to "saved"

**5. Building the Graph Node (10 min)**
- Node function
- Tool execution
- State updates

**6. Testing the Agent (15 min)**
- Test saving issues
- Test error handling
- Test confirmation flow
- **Show errors**: DB failures, tool errors

**Key Takeaways:**
- Tool integration = Agent capabilities
- Error handling = Production-ready
- Status management = Workflow tracking
- This agent saves issues to database

### Content Structure

**1. Why Telegram? (10 min)**
- **Explanation to Include:**
  > "Why Telegram? It's the path of least resistance. Building a React frontend takes days. A Telegram bot takes 10 minutes and lives on the user's phone. We use Webhooks: specific URLs that Telegram notifies whenever a user sends a message. Our Python server sits there listening for these 'pings'. When a message arrives, we process it with our agent, and send a response back. This is how Mwalimu works—students chat on Telegram, but the AI runs on our server."

**2. Setting Up Telegram Bot (15 min)**
- Create bot with @BotFather
- Get API token
- Basic bot setup

**3. FastAPI Webhook Server (20 min)**
- FastAPI setup:
  ```python
  from fastapi import FastAPI, Request
  from fastapi.responses import JSONResponse
  import httpx
  
  app = FastAPI()
  TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
  TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
  
  @app.post("/webhook")
  async def webhook(request: Request):
      data = await request.json()
      message = data.get("message", {})
      chat_id = message.get("chat", {}).get("id")
      text = message.get("text", "")
      
      # Process with agent (we'll build this)
      response = await process_with_agent(text, chat_id)
      
      # Send response
      async with httpx.AsyncClient() as client:
          await client.post(
              f"{TELEGRAM_API}/sendMessage",
              json={"chat_id": chat_id, "text": response}
          )
      
      return JSONResponse({"ok": True})
  ```

**4. Ngrok for Local Development (15 min)**
- Install ngrok
- Expose local server:
  ```bash
  ngrok http 8000
  ```
- Set webhook:
  ```python
  async def set_webhook(ngrok_url: str):
      async with httpx.AsyncClient() as client:
          await client.post(
              f"{TELEGRAM_API}/setWebhook",
              json={"url": f"{ngrok_url}/webhook"}
          )
  ```

**5. Testing the Connection (10 min)**
- Send test message
- Debug webhook issues
- **Show real errors**: Webhook failures, timeout issues

**6. Production Deployment Preview (5 min)**
- Render/Railway deployment
- Setting webhook in production
- Monitoring webhook health

**Hands-On Exercise:**
- Set up Telegram bot
- Create FastAPI webhook
- Test with ngrok
- Handle errors gracefully

**Key Takeaways:**
- Telegram = Fastest path to users
- Webhooks = Real-time communication
- FastAPI = Production-ready API
- Show errors = Better learning

---

---

## **VIDEO 10: Completing the Graph & Main Loop (Making Kunani Run)**

### Objective
Complete Kunani's LangGraph workflow. Build the main conversation loop that ties everything together.

### Design We'll Introduce
- **Complete Workflow**: All agents connected
- **Routing Logic**: Final routing implementation
- **Entry Point Logic**: Dynamic entry based on previous handoff
- **Main Loop**: Conversation interface

### What We Build
Complete `app/graph/najua_graph.py`
`main.py` - Conversation loop

### Content Structure

**1. Completing the Graph (20 min)**
- All nodes connected
- Routing logic complete
- Entry point logic
- Code:
  ```python
  # app/graph/najua_graph.py
  def build_graph():
      workflow = StateGraph(NajuaState)
      # Add all nodes
      # Add conditional entry
      # Add routing edges
      return workflow.compile()
  ```

**2. Routing Logic (15 min)**
- `route_after_agent()` - Complete implementation
- `determine_entry_point()` - Complete implementation
- Handle all handoff types
- Edge cases

**3. Building Main Loop (20 min)**
- Conversation interface
- State management
- Graph invocation
- User input handling
- Code:
  ```python
  # main.py
  async def run_conversation():
      graph = get_graph()
      state = {...}
      
      while True:
          user_input = input("You: ")
          state["conversation_history"].append({"role": "user", "content": user_input})
          result = await graph.ainvoke(state)
          state = result
          # Display response
  ```

**4. Testing Complete Flow (15 min)**
- Test full issue reporting flow
- Test routing between agents
- Test memory persistence
- **Show errors**: Graph failures, state issues

**5. Error Handling (10 min)**
- Graph errors
- Agent errors
- Tool errors
- User-friendly messages

**Key Takeaways:**
- Complete graph = Full workflow
- Main loop = User interface
- Error handling = Production-ready
- Kunani is now functional!

### Content Structure

**1. The Router Pattern (15 min)**
- **Explanation to Include:**
  > "This is the Router Pattern. We don't want one giant prompt handling everything. We create specialized mini-agents. The Router is the receptionist. It classifies the intent ('Is this a math question?') and hands it off. This reduces hallucinations because the Math Agent doesn't even know History exists. Each agent is an expert in one domain, and the router is the dispatcher."

**2. Building the Router Agent (20 min)**
- Router with structured output:
  ```python
  from pydantic import BaseModel
  from typing import Literal
  
  class RoutingDecision(BaseModel):
      intent: Literal["math", "history", "science", "general"]
      confidence: float
      reasoning: str
  
  def router_agent(user_message: str) -> RoutingDecision:
      prompt = f"""
      Classify this student question and route to the right agent.
      Question: {user_message}
      
      Output JSON with intent, confidence, and reasoning.
      """
      
      response = llm_call(prompt, response_format=RoutingDecision)
      return response
  ```

**3. Building Specialized Agents (25 min)**
- Math Agent (using llm.py service):
  ```python
  from app.shared_services.llm import call_llm_api
  
  def math_agent(question: str) -> str:
      prompt = f"""
      You are a math tutor. Answer this question clearly:
      {question}
      
      Use examples and step-by-step explanations.
      """
      return call_llm_api(
          messages=[{"role": "user", "content": prompt}],
          provider="gemini",  # or "openai" for better reasoning
          model="gemini-1.5-flash"
      )
  ```
- History Agent:
  ```python
  def history_agent(question: str) -> str:
      prompt = f"""
      You are a history tutor specializing in African history.
      Answer this question: {question}
      
      Focus on Kenyan and African context when relevant.
      """
      return call_llm_api(
          messages=[{"role": "user", "content": prompt}],
          provider="gemini",
          model="gemini-1.5-flash"
      )
  ```
- **Key Point**: All agents use any LLM (via llm.py). LangGraph orchestrates the routing between them. Different agents can use different LLMs if needed.

**4. Building the LangGraph Router (20 min)**
- Graph structure:
  ```python
  class MwalimuState(TypedDict):
      user_message: str
      routing_decision: Optional[RoutingDecision]
      agent_response: Optional[str]
      conversation_history: List[Dict[str, str]]
  
  def router_node(state: MwalimuState) -> MwalimuState:
      decision = router_agent(state["user_message"])
      state["routing_decision"] = decision
      return state
  
  def math_node(state: MwalimuState) -> MwalimuState:
      response = math_agent(state["user_message"])
      state["agent_response"] = response
      return state
  
  def history_node(state: MwalimuState) -> MwalimuState:
      response = history_agent(state["user_message"])
      state["agent_response"] = response
      return state
  
  # Graph
  workflow = StateGraph(MwalimuState)
  workflow.add_node("router", router_node)
  workflow.add_node("math", math_node)
  workflow.add_node("history", history_node)
  
  workflow.add_edge(START, "router")
  workflow.add_conditional_edges(
      "router",
      lambda s: s["routing_decision"].intent,
      {
          "math": "math",
          "history": "history",
          "general": "math"  # Default
      }
  )
  workflow.add_edge("math", END)
  workflow.add_edge("history", END)
  ```

**5. Integrating with Telegram (10 min)**
- Connect graph to webhook:
  ```python
  @app.post("/webhook")
  async def webhook(request: Request):
      data = await request.json()
      message = data.get("message", {})
      chat_id = message.get("chat", {}).get("id")
      text = message.get("text", "")
      
      # Load or create state for this user
      config = {"configurable": {"thread_id": str(chat_id)}}
      
      # Run graph
      result = graph.invoke(
          {"user_message": text, "conversation_history": []},
          config=config
      )
      
      # Send response
      await send_telegram_message(chat_id, result["agent_response"])
  ```

**6. Testing and Debugging (10 min)**
- Test routing decisions
- Handle edge cases
- **Show errors**: Wrong routing, agent failures

**Hands-On Exercise:**
- Build router with 3 agents
- Test routing accuracy
- Add fallback for unclear intents

**Key Takeaways:**
- Router Pattern = Specialized agents
- Structured routing = Better accuracy
- LangGraph = Clean orchestration
- Production = Error handling

---

---

## **VIDEO 11: Observability & Monitoring (Langfuse Integration)**

### Objective
Add observability to Kunani using Langfuse. Track agent performance, costs, and debug issues.

### Design We'll Introduce
- **Observability Design**: What to track in Kunani
- **Langfuse Integration**: How to instrument agents
- **Metrics**: Cost, latency, quality
- **Debugging**: Trace agent execution

### What We Build
Langfuse integration in Kunani
Instrument all agents

### Content Structure

**1. Observability Design for Kunani (10 min)**
- **What to track**:
  - Agent decisions (routing choices)
  - LLM calls (cost, latency)
  - Tool usage
  - Errors
- **Design**: Visibility = Trust

**2. Setting Up Langfuse (15 min)**
- Installation
- Configuration
- API keys
- Code:
  ```python
  from langfuse import Langfuse
  from langfuse.decorators import observe
  
  langfuse = Langfuse(...)
  ```

**3. Instrumenting Agents (25 min)**
- Add `@observe()` decorators
- Track LLM calls
- Track tool calls
- Track handoff decisions
- Code:
  ```python
  @observe()
  def welcome_agent(...):
      # Automatically traced
  ```

**4. LangGraph Integration (15 min)**
- Callback handler
- Trace graph execution
- Track state changes

**5. Viewing Traces (10 min)**
- Langfuse dashboard
- Debugging agent flow
- Cost analysis
- Performance metrics

**6. Production Monitoring (10 min)**
- Alerts
- Dashboards
- Error tracking

**Key Takeaways:**
- Observability = Production requirement
- Langfuse = Open-source option
- Traces = Debugging tool
- Kunani is now observable

### Content Structure

**1. Dynamic Content Generation (10 min)**
- Why generate vs. pre-written?
- User customization (difficulty, topic, count)
- Real-time generation

**2. Few-Shot Prompting (15 min)**
- **Explanation to Include:**
  > "We are using Few-Shot Prompting here. Instead of just asking for questions, we give the model 3 examples of perfect questions in the prompt. This drastically improves the quality and consistency of the output compared to zero-shot (just asking). The model learns the format, style, and difficulty level from the examples. It's like showing a student sample essays before asking them to write one."

**3. Building the Question Generator (25 min)**
- Pydantic model:
  ```python
  class TriviaQuestion(BaseModel):
      question: str
      options: List[str]  # 4 options
      correct_answer: str
      explanation: str
      difficulty: Literal["easy", "medium", "hard"]
      topic: str
  
  class TriviaSet(BaseModel):
      questions: List[TriviaQuestion]
      topic: str
      difficulty: str
  ```
- Few-shot prompt:
  ```python
  FEW_SHOT_EXAMPLES = """
  Example 1:
  Question: "Who was the first President of Kenya?"
  Options: ["Jomo Kenyatta", "Daniel arap Moi", "Mwai Kibaki", "Uhuru Kenyatta"]
  Correct Answer: "Jomo Kenyatta"
  Explanation: "Jomo Kenyatta served as Kenya's first President from 1964 to 1978."
  Difficulty: "easy"
  
  Example 2:
  Question: "What year did Kenya gain independence?"
  Options: ["1960", "1961", "1962", "1963"]
  Correct Answer: "1963"
  Explanation: "Kenya gained independence from British colonial rule on December 12, 1963."
  Difficulty: "medium"
  
  Example 3:
  [Another example...]
  """
  
  def generate_trivia(topic: str, difficulty: str, count: int = 5) -> TriviaSet:
      prompt = f"""
      Generate {count} trivia questions about {topic}.
      Difficulty level: {difficulty}
      
      {FEW_SHOT_EXAMPLES}
      
      Generate questions following this exact format.
      """
      
      response = llm_call(prompt, response_format=TriviaSet)
      return response
  ```

**4. Difficulty Calibration (15 min)**
- Easy: Basic facts, common knowledge
- Medium: Requires some thinking
- Hard: Expert-level, nuanced
- Prompt engineering for difficulty

**5. Kenyan Context Integration (15 min)**
- Topics: Kenyan history, culture, geography
- Examples: M-Pesa, Maasai culture, Nairobi landmarks
- Making it relatable

**6. Integration with Trivia Pals (10 min)**
- How it fits in the game flow
- API endpoint
- Caching strategies

**Hands-On Exercise:**
- Generate questions for 3 different topics
- Test difficulty levels
- Add validation (no duplicate questions)

**Key Takeaways:**
- Few-shot = Better quality
- Structured output = Consistent format
- Dynamic generation = User customization
- Local context = Better engagement

---

### **Phase 4: Advanced/Production (The "Senior Manager" Perspective)**
*Goal: Show you understand business value, not just code.*

---

---

## **VIDEO 12: Deployment & Production (Making Kunani Live)**

### Objective
Deploy Kunani to production. Make it accessible 24/7 with proper infrastructure.

### Design We'll Introduce
- **Deployment Architecture**: How to deploy Kunani
- **Environment Setup**: Production configuration
- **Database Setup**: Production PostgreSQL
- **Monitoring**: Production observability
- **Scaling**: Future considerations

### What We Build
Deploy Kunani to Render/Railway/Vercel
Production configuration

### Content Structure

**1. Deployment Architecture (15 min)**
- **Options**: Render, Railway, Vercel, AWS
- **Design**: FastAPI backend + PostgreSQL
- **Environment**: Production vs development

**2. Preparing for Production (20 min)**
- Environment variables
- Database setup (production)
- Security considerations
- Error handling
- Logging

**3. Deploying Backend (25 min)**
- Render/Railway setup
- Database connection
- Environment variables
- Health checks
- Code deployment

**4. Testing Production (10 min)**
- Test all endpoints
- Test agent flow
- Test database
- Monitor errors

**5. Production Checklist (10 min)**
- Security
- Performance
- Monitoring
- Backup strategy
- Scaling considerations

**6. Future Enhancements (5 min)**
- API endpoints (FastAPI)
- Web interface
- Mobile app
- Multi-language support

**Key Takeaways:**
- Deployment = Making it real
- Production = 24/7 reliability
- Monitoring = Staying alive
- Kunani is now live!

---

## **SERIES COMPLETE: What We Built**

By the end of this series, you've built **Kunani** - a complete, production-grade civic issue tracking system:

✅ **Multi-provider LLM service** (`llm.py`)  
✅ **Structured data models** (Pydantic)  
✅ **LangGraph orchestration** (multi-agent workflow)  
✅ **PostgreSQL database** (issues + checkpoints)  
✅ **Database tools** (CRUD operations)  
✅ **Persistent memory** (checkpointing)  
✅ **3 specialized agents** (Welcome, Issue Filler, Issue Reporting)  
✅ **Complete workflow** (triage → collect → save)  
✅ **Observability** (Langfuse)  
✅ **Production deployment** (live system)  

**You now have a complete, deployable AI agent system!**

### Content Structure

**1. The RAG Problem (15 min)**
- **Explanation to Include:**
  > "Vector databases are great for semantic search, but bad for analytics. If you ask 'How many customers complained yesterday?', a vector DB struggles. It's designed to find similar documents, not to count or aggregate. We need Agentic RAG: An agent that decides 'Do I need to search documents, or do I need to run a SQL query?' We give the agent a 'Calculator' tool and a 'Database' tool. The agent becomes a data analyst, not just a search engine."

**2. Simple RAG Limitations (10 min)**
- Vector search = Similarity, not analytics
- Can't aggregate, count, or calculate
- Example: "How many 5-star reviews?" → Vector DB fails

**3. Agentic RAG Architecture (20 min)**
- Agent with multiple tools:
  ```python
  class DataAnalysisState(TypedDict):
      user_query: str
      analysis_type: Optional[str]  # "search" or "analytics"
      tool_used: Optional[str]
      result: Optional[str]
  
  def analyst_agent(state: DataAnalysisState) -> DataAnalysisState:
      query = state["user_query"]
      
      # Agent decides: search or analyze?
      decision = llm_classify(
          f"Query: {query}\n"
          "Is this a search question (find similar) or analytics (count, sum, average)?"
      )
      
      if decision == "analytics":
          # Use SQL/calculation tool
          state["tool_used"] = "calculator"
          state["result"] = run_analytics(query)
      else:
          # Use vector search
          state["tool_used"] = "vector_db"
          state["result"] = vector_search(query)
      
      return state
  ```

**4. Building Tools (20 min)**
- Calculator tool:
  ```python
  @tool
  def calculator_tool(operation: str, data: List[float]) -> float:
      """Perform calculations on data"""
      if operation == "count":
          return len(data)
      elif operation == "sum":
          return sum(data)
      elif operation == "average":
          return sum(data) / len(data)
  ```
- Database tool:
  ```python
  @tool
  def database_query_tool(query: str) -> List[dict]:
      """Run SQL query on customer data"""
      # Execute SQL
      return results
  ```
- Vector search tool:
  ```python
  @tool
  def vector_search_tool(query: str, top_k: int = 5) -> List[str]:
      """Search similar documents"""
      # Vector DB search
      return similar_docs
  ```

**5. Real Example: XPChex Architecture (20 min)**
- Code walkthrough: `backend/app/graph/review_analysis_graph.py`
- How it combines:
  - Sentiment analysis (LLM)
  - Issue extraction (LLM)
  - Analytics (tools/database)
- Multi-step workflow

**6. Production Patterns (10 min)**
- Tool selection accuracy
- Fallback strategies
- Performance optimization

**Hands-On Exercise:**
- Build agentic RAG system
- Add multiple tools
- Test query routing

**Key Takeaways:**
- RAG = Search, Agentic RAG = Analysis
- Tools = Agent capabilities
- Multi-tool agents = Powerful systems
- Production = Right tool for the job

---


### Objective
How do you know your bot isn't lying? Production monitoring and observability for AI systems. Learn both Langfuse and LangSmith.

### Content Structure

**1. The Monitoring Problem (10 min)**
- **Explanation to Include:**
  > "In software, we have unit tests. In AI, we have Evals. We can't just assert result == expected. We need to trace the execution. Observability tools like Langfuse and LangSmith let us see the 'thought bubble' of the AI—why did it choose Tool A instead of Tool B? This visibility is required for production. Without it, you're flying blind."

**2. Langfuse - Open Source Observability (20 min)**
- **What is Langfuse?** Open-source LLM observability platform
- **Why Langfuse?** Self-hosted, full control, free
- Setup:
  ```bash
  pip install langfuse
  ```
- Instrumenting agents:
  ```python
  from langfuse import Langfuse
  from langfuse.decorators import langfuse_context, observe
  
  langfuse = Langfuse(
      secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
      public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
      host="https://cloud.langfuse.com"  # or self-hosted
  )
  
  @observe()
  def my_agent(input: str) -> str:
      # Automatically traced
      result = llm_call(input)
      langfuse_context.score(
          name="quality",
          value=0.9
      )
      return result
  ```
- LangGraph integration:
  ```python
  from langfuse.callback import CallbackHandler
  
  langfuse_handler = CallbackHandler(
      secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
      public_key=os.getenv("LANGFUSE_PUBLIC_KEY")
  )
  
  result = graph.invoke(
      state,
      config={"callbacks": [langfuse_handler]}
  )
  ```
- Real example: Kunani uses Langfuse (from README)

**3. LangSmith - LangChain's Observability (20 min)**
- **What is LangSmith?** LangChain's official observability platform
- Setup:
  ```bash
  pip install langsmith
  ```
- Instrumenting:
  ```python
  from langsmith import traceable
  from langchain_core.callbacks import LangChainTracer
  
  @traceable
  def my_agent(input: str) -> str:
      result = llm_call(input)
      return result
  
  # With LangGraph
  tracer = LangChainTracer()
  result = graph.invoke(state, config={"callbacks": [tracer]})
  ```

**4. Building Evals (20 min)**
- What to evaluate:
  - Correctness
  - Tool selection accuracy
  - Response quality
  - Latency
  - Cost
- Example eval with Langfuse:
  ```python
  def eval_agent_response(run, example):
      """Evaluate if agent response is correct"""
      expected = example.outputs["expected_answer"]
      actual = run.outputs["response"]
      
      correct = expected.lower() in actual.lower()
      
      langfuse_context.score(
          name="correctness",
          value=1.0 if correct else 0.0
      )
      
      return {"correct": correct, "score": 1.0 if correct else 0.0}
  ```

**5. Viewing Traces (15 min)**
- Langfuse dashboard:
  - Traces and spans
  - Token usage
  - Latency metrics
  - Cost tracking
- LangSmith dashboard:
  - Similar features
  - Integration with LangChain ecosystem
- Debugging tool calls
- Performance metrics

**6. Production Monitoring (10 min)**
- Alerts for failures
- Cost tracking
- Latency monitoring
- Error rate tracking
- Custom metrics

**7. Langfuse vs. LangSmith (5 min)**
- Langfuse: Open-source, self-hostable, flexible
- LangSmith: Official LangChain tool, cloud-hosted
- When to use each

**Hands-On Exercise:**
- Instrument an agent with Langfuse
- Create evals
- View traces in dashboard
- Set up alerts

**Key Takeaways:**
- Monitoring = Production requirement
- Langfuse = Open-source option
- LangSmith = LangChain official
- Evals = AI testing
- Traces = Debugging tool
- Visibility = Trust

---


### **VIDEO 13: Building the Agent**

### Objective
Build a complete production system: Job Application Agent that takes a PDF Resume + Job Link and rewrites the resume to match the job description.

### Content Structure

**1. Project Overview (10 min)**
- Requirements:
  - Parse PDF resume
  - Scrape job description from URL
  - Analyze match
  - Rewrite resume sections
  - Output formatted resume

**2. Architecture Design (15 min)**
- Multi-agent system:
  - Parser agent (PDF → structured data)
  - Scraper agent (URL → job description)
  - Matcher agent (analyze fit)
  - Rewriter agent (optimize resume)
- LangGraph orchestration

**3. Building the Parser (20 min)**
- PDF parsing with multimodal LLM
- Extract structured data:
  ```python
  class ResumeData(BaseModel):
      name: str
      email: str
      experience: List[Experience]
      skills: List[str]
      education: List[Education]
  ```
- Handle different resume formats

**4. Building the Scraper (15 min)**
- Web scraping job description
- Extract key requirements
- Structured output

**5. Building the Matcher (20 min)**
- Compare resume vs. job
- Identify gaps
- Score match
- Generate improvement suggestions

**6. Building the Rewriter (20 min)**
- Optimize resume sections
- Match keywords
- Improve descriptions
- Maintain truthfulness

**7. Integrating Everything (15 min)**
- LangGraph workflow
- Error handling
- Testing

**Hands-On:**
- Build complete system
- Test with real resumes
- Iterate on quality

---

### **VIDEO 14: Deployment**

### Objective
Taking the FastAPI backend and deploying it to Render/Vercel so it runs 24/7.

### Content Structure

**1. Preparing for Production (15 min)**
- Environment variables
- Database setup
- Dependencies
- Security checks

**2. Deploying to Render (25 min)**
- Create Render account
- Set up PostgreSQL
- Deploy FastAPI:
  ```yaml
  # render.yaml
  services:
    - type: web
      name: job-agent-api
      env: python
      buildCommand: pip install -r requirements.txt
      startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
      envVars:
        - key: DATABASE_URL
          fromDatabase:
            name: jobagent-db
            property: connectionString
  ```
- Set environment variables
- Test deployment

**3. Setting Up Monitoring (15 min)**
- Health checks
- Logging
- Error tracking
- Uptime monitoring

**4. CI/CD Basics (10 min)**
- GitHub Actions
- Auto-deploy on push
- Testing before deploy

**5. Production Checklist (10 min)**
- Security
- Performance
- Scaling
- Backup

**Hands-On:**
- Deploy to Render
- Set up monitoring
- Test production system

**Key Takeaways:**
- Deployment = Making it real
- Monitoring = Staying alive
- Production = 24/7 reliability

---

## **EXPANDED CONTENT: Additional Deep-Dive Episodes**

### **Episode 13: Advanced LangGraph Patterns**
*Complex workflows, parallel execution, state management, and production patterns from real projects.*

### **Episode 14: Advanced LangGraph Patterns**
*Complex workflows, parallel execution, state management*

### **Episode 15: Prompt Engineering Masterclass**
*Production-grade prompt patterns, few-shot examples, context management*

### **Episode 16: Error Handling & Debugging**
*Real-world debugging, logging strategies, production error handling*

### **Episode 17: Building Custom Tools**
*Creating reusable tools, tool composition, tool testing*

### **Episode 18: Agent Performance Optimization**
*Caching, parallel execution, cost optimization, latency reduction*

### **Episode 19: Security in AI Systems**
*API key management, input validation, rate limiting, data privacy*

### **Episode 20: Scaling Agent Systems**
*Horizontal scaling, load balancing, database optimization, async patterns*

---

## **TEACHING PRINCIPLES**

1. **Show Real Errors**: Don't edit out crashes. Debugging is where learning happens.
2. **Production-First**: Every example is production-ready, not a toy.
3. **Local Context**: Use Kenyan/African examples (M-Pesa, local history, etc.).
4. **Real Projects**: Reference actual projects from your portfolio.
5. **Progressive Complexity**: Start simple, build to production systems.
6. **Hands-On**: Every episode has exercises viewers can code along.

---

## **RESOURCES & REFERENCES**

### **Your Projects**
- **Mwalimu**: Telegram-based tutoring system with routing agents
- **Trivia Pals**: Dynamic question generation with few-shot prompting
- **Kunani**: Multi-agent issue tracking with LangGraph
- **XPChex**: Agentic RAG for review analysis
- **Portfolio**: www.wesleymogaka.com

### **Frameworks & Tools**
- LangGraph: https://langchain-ai.github.io/langgraph/
- Google Gen AI: https://ai.google.dev/
- Mastra: https://mastra.ai/
- Instructor: https://jxnl.github.io/instructor/
- LangSmith: https://smith.langchain.com/

### **Key Concepts**
- TypedDict for state
- Pydantic for validation
- Instructor for structured outputs
- LangGraph for orchestration
- Checkpointing for memory
- Tools for agent capabilities

---

## **SERIES OUTCOMES**

By the end of this series, viewers will:
1. ✅ Understand AI agents vs. simple LLM calls
2. ✅ Build production-grade multi-agent systems
3. ✅ Deploy agents to production
4. ✅ Monitor and evaluate agent performance
5. ✅ Handle errors and edge cases
6. ✅ Integrate agents with real-world interfaces (Telegram, APIs)
7. ✅ Use advanced patterns (routing, memory, tools)
8. ✅ Build complete, deployable projects

---

**This syllabus is designed to take someone from "I know Python" to "I built a Multi-Agent System that's running in production."**

