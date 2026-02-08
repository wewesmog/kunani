"""
Welcome agent - LangGraph version using pure LangGraph agent pattern.
Returns structured output for conditional routing.
"""
from typing import Annotated, Sequence
from langgraph.graph import StateGraph, END, START, MessagesState
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
import os
from dotenv import load_dotenv

from app.models.najua_models import WelcomeHandoffResponse
from app.shared_services.logger_setup import setup_logger

load_dotenv()
logger = setup_logger()


class WelcomeAgentState(MessagesState):
    """State for welcome agent - extends MessagesState for LangGraph agent"""
    handoff_decision: Optional[WelcomeHandoffResponse] = None
    conversation_history: list = []  # Keep for compatibility


def create_welcome_agent_llm(provider: str = "gemini", model: str = "gemini-1.5-flash"):
    """
    Create LLM instance for welcome agent.
    Can use any provider - Gemini, OpenAI, etc.
    """
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=model,
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    elif provider == "openai":
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            temperature=0.3,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        # Default to Gemini
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )


def welcome_agent_node_langgraph(state: WelcomeAgentState) -> WelcomeAgentState:
    """
    Welcome agent node using pure LangGraph pattern.
    Returns structured output for conditional routing.
    """
    # Get conversation history from messages
    messages = state.get("messages", [])
    
    # Build system prompt
    system_prompt = """
You are an entry point to Najua, a system where citizens in Kenya can post any issues that need to be addressed by the government.
Najua only handles non-emergency issues.
If the user's issue is an emergency, you should respond with a message that the issue is an emergency and should be reported to the emergency services.

Your work is a triage, to understand the user's issue and redirect them to the appropriate agent.

Depending on your assessment, please handoff to any of the following agents:

i. issue_filler_agent:
This agent is responsible for picking the user's issue.
The issue must not be emergency or urgent.
Issues can range from: Infrastructure, Education, Health, Agriculture, Environment, Transport, Finance, Social Welfare, Other

ii. issue_enquiry_agent:
This agent is responsible for enquiring about the status of an issue or generally about any reported issues.
This agent handles enquiries only and not reporting of issues

iii. respond_to_user_agent:
This agent is responsible for talking directly to the user, handling chitchat and other non-issue related conversations.
Only use this agent if the user's issue is not clear or if you need to gather more information from the user.
You can also use this agent if the user's issue is an emergency.

IMPORTANT: You must respond with a valid JSON object matching the WelcomeHandoffResponse schema.
"""
    
    # Create LLM with structured output parser
    llm = create_welcome_agent_llm(provider="gemini", model="gemini-1.5-flash")
    
    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=WelcomeHandoffResponse)
    
    # Add format instructions to prompt
    format_instructions = parser.get_format_instructions()
    full_prompt = f"{system_prompt}\n\n{format_instructions}"
    
    # Build messages with system prompt
    agent_messages = [SystemMessage(content=full_prompt)] + messages
    
    # Call LLM
    try:
        response = llm.invoke(agent_messages)
        
        # Parse structured output
        # For Gemini, response might be in JSON mode
        response_text = response.content
        
        # Try to parse as JSON first (Gemini JSON mode)
        import json
        try:
            # Check if response is JSON
            if response_text.strip().startswith('{'):
                parsed_json = json.loads(response_text)
                handoff_decision = WelcomeHandoffResponse.model_validate(parsed_json)
            else:
                # Use parser to extract JSON from text
                handoff_decision = parser.parse(response_text)
        except (json.JSONDecodeError, Exception) as e:
            # Fallback: try parser
            try:
                handoff_decision = parser.parse(response_text)
            except Exception as parse_error:
                logger.error(f"Failed to parse structured output: {parse_error}")
                logger.error(f"Response text: {response_text}")
                # Fallback to default
                handoff_decision = WelcomeHandoffResponse(
                    agent="respond_to_user_agent",
                    reasoning="Failed to parse response, defaulting to respond_to_user_agent",
                    message_to_user="I'm having trouble understanding. Could you please rephrase?",
                    agent_after_human_response="welcome_agent"
                )
        
        # Update state
        state["handoff_decision"] = handoff_decision
        
        # Add assistant message to conversation if message_to_user exists
        if handoff_decision.message_to_user:
            state["messages"] = state.get("messages", []) + [
                AIMessage(content=handoff_decision.message_to_user)
            ]
        
        logger.info(f"Welcome agent (LangGraph) completed. Handoff decision: {handoff_decision}")
        
    except Exception as e:
        logger.error(f"Error in welcome agent (LangGraph): {e}", exc_info=True)
        # Fallback handoff
        state["handoff_decision"] = WelcomeHandoffResponse(
            agent="respond_to_user_agent",
            reasoning=f"Error occurred: {str(e)}",
            message_to_user="I encountered an error. Please try again.",
            agent_after_human_response="welcome_agent"
        )
    
    return state


def create_welcome_agent_graph():
    """
    Create a standalone LangGraph for welcome agent.
    This can be used independently or as part of larger graph.
    """
    workflow = StateGraph(WelcomeAgentState)
    
    # Add welcome agent node
    workflow.add_node("welcome_agent", welcome_agent_node_langgraph)
    
    # Start -> welcome agent
    workflow.add_edge(START, "welcome_agent")
    
    # Welcome agent -> END (handoff_decision is in state for parent graph to use)
    workflow.add_edge("welcome_agent", END)
    
    return workflow.compile()


def welcome_agent_langgraph(conversation_history: list) -> WelcomeHandoffResponse:
    """
    Standalone function to run welcome agent using LangGraph.
    Converts conversation_history to LangGraph messages format.
    
    Args:
        conversation_history: List of message dicts [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        WelcomeHandoffResponse with routing decision
    """
    # Convert conversation history to LangGraph messages
    messages = []
    for msg in conversation_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    # Create initial state
    initial_state = WelcomeAgentState(messages=messages)
    
    # Create and run graph
    graph = create_welcome_agent_graph()
    result = graph.invoke(initial_state)
    
    # Extract handoff decision
    handoff_decision = result.get("handoff_decision")
    
    if not handoff_decision:
        # Fallback
        handoff_decision = WelcomeHandoffResponse(
            agent="respond_to_user_agent",
            reasoning="No handoff decision returned",
            message_to_user="I'm having trouble understanding. Could you please rephrase?",
            agent_after_human_response="welcome_agent"
        )
    
    return handoff_decision


# For use in conditional routing - extract handoff from state
def get_handoff_from_state(state: WelcomeAgentState) -> str:
    """
    Extract handoff agent name from state for conditional routing.
    Use this in conditional_edges.
    """
    handoff_decision = state.get("handoff_decision")
    if handoff_decision:
        return handoff_decision.agent
    return "respond_to_user_agent"  # Default

