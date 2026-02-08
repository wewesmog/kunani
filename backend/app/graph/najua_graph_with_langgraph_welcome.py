"""
LangGraph workflow for Najua - using LangGraph welcome agent.
Shows how to integrate LangGraph-based welcome agent with function-based other agents.
"""
from typing import TypedDict, Optional, Literal, Union
from langgraph.graph import StateGraph, END, START
import os
import logging
from dotenv import load_dotenv

from app.models.najua_models import NajuaState, WelcomeHandoffResponse, IssueReportingHandoffResponse, IssueFillerHandoffResponse
from app.agents.welcome_agent_langgraph import welcome_agent_node_langgraph, WelcomeAgentState, get_handoff_from_state
from app.agents.issue_reporting_agent import issue_reporting_agent
from app.agents.issue_filler_agent import issue_filler_agent

load_dotenv()
logger = logging.getLogger(__name__)


def convert_to_welcome_state(state: NajuaState) -> WelcomeAgentState:
    """Convert NajuaState to WelcomeAgentState for LangGraph welcome agent"""
    from langchain_core.messages import HumanMessage, AIMessage
    
    messages = []
    for msg in state.get("conversation_history", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    
    return WelcomeAgentState(
        messages=messages,
        conversation_history=state.get("conversation_history", [])
    )


def convert_from_welcome_state(welcome_state: WelcomeAgentState, original_state: NajuaState) -> NajuaState:
    """Convert WelcomeAgentState back to NajuaState"""
    # Extract handoff decision
    handoff_decision = welcome_state.get("handoff_decision")
    
    # Update original state
    original_state["current_node"] = "welcome_agent"
    original_state["handoff_decision"] = handoff_decision
    
    # Update conversation history if message was added
    if handoff_decision and handoff_decision.message_to_user:
        original_state["conversation_history"].append({
            "role": "assistant",
            "content": handoff_decision.message_to_user
        })
    
    return original_state


def welcome_agent_node_wrapper(state: NajuaState) -> NajuaState:
    """
    Wrapper node that converts state, calls LangGraph welcome agent, and converts back.
    This allows LangGraph welcome agent to work with function-based other agents.
    """
    # Convert to WelcomeAgentState
    welcome_state = convert_to_welcome_state(state)
    
    # Call LangGraph welcome agent node
    result_state = welcome_agent_node_langgraph(welcome_state)
    
    # Convert back to NajuaState
    return convert_from_welcome_state(result_state, state)


def issue_reporting_agent_node(state: NajuaState) -> NajuaState:
    """Issue reporting agent node - saves issues (unchanged)"""
    conversation_history = state["conversation_history"]
    handoff_decision = issue_reporting_agent(conversation_history, state)
    
    state["current_node"] = "issue_reporting_agent"
    state["handoff_decision"] = handoff_decision
    
    if handoff_decision.message_to_user:
        state["conversation_history"].append({"role": "assistant", "content": handoff_decision.message_to_user})
    
    return state


def issue_filler_agent_node(state: NajuaState) -> NajuaState:
    """Issue filler agent node - fills issue details (unchanged)"""
    conversation_history = state["conversation_history"]
    handoff_decision = issue_filler_agent(conversation_history, state)
    
    state["current_node"] = "issue_filler_agent"
    state["handoff_decision"] = handoff_decision
    
    if handoff_decision.message_to_user:
        state["conversation_history"].append({"role": "assistant", "content": handoff_decision.message_to_user})
    
    return state


def route_after_agent(state: NajuaState) -> str:
    """
    Route based on handoff decision from any agent.
    Returns the next node name or END.
    """
    handoff_decision = state.get("handoff_decision")
    
    if not handoff_decision:
        logger.warning("No handoff decision found, ending")
        return END
    
    agent_name = handoff_decision.agent
    
    if agent_name == "respond_to_user_agent":
        return END  # Ends graph, user input will restart
    elif agent_name == "issue_reporting_agent":
        return "issue_reporting_agent"
    elif agent_name == "issue_filler_agent":
        return "issue_filler_agent"
    elif agent_name == "issue_enquiry_agent":
        return END  # Not implemented yet
    elif agent_name == "welcome_agent":
        return "welcome_agent"
    else:
        logger.warning(f"Unknown agent: {agent_name}, ending")
        return END


def determine_entry_point(state: NajuaState) -> str:
    """
    Determine which agent to start with.
    Uses agent_after_human_response from previous handoff if available,
    otherwise starts with welcome_agent.
    """
    previous_handoff = state.get("handoff_decision")
    
    if previous_handoff and hasattr(previous_handoff, "agent_after_human_response"):
        entry_agent = previous_handoff.agent_after_human_response
        logger.info(f"Using previous handoff entry point: {entry_agent}")
        if entry_agent in ["welcome_agent", "issue_filler_agent", "issue_reporting_agent"]:
            return entry_agent
        else:
            logger.warning(f"Invalid entry agent {entry_agent}, defaulting to welcome_agent")
            return "welcome_agent"
    else:
        logger.info("No previous handoff, starting with welcome_agent")
        return "welcome_agent"


def build_graph_with_langgraph_welcome():
    """
    Build the Najua workflow graph using LangGraph-based welcome agent.
    Other agents remain function-based.
    """
    workflow = StateGraph(NajuaState)
    
    # Add nodes
    workflow.add_node("welcome_agent", welcome_agent_node_wrapper)  # LangGraph version
    workflow.add_node("issue_reporting_agent", issue_reporting_agent_node)  # Function-based
    workflow.add_node("issue_filler_agent", issue_filler_agent_node)  # Function-based
    
    # Conditional entry point
    workflow.add_conditional_edges(
        START,
        determine_entry_point,
        {
            "welcome_agent": "welcome_agent",
            "issue_reporting_agent": "issue_reporting_agent",
            "issue_filler_agent": "issue_filler_agent",
            "issue_enquiry_agent": END,
            "respond_to_user_agent": END,
        }
    )
    
    # Conditional routing from each agent
    common_routing = {
        "issue_reporting_agent": "issue_reporting_agent",
        "issue_filler_agent": "issue_filler_agent",
        "welcome_agent": "welcome_agent",
        "respond_to_user_agent": END,
        "issue_enquiry_agent": END,
    }
    
    for agent_node in ["welcome_agent", "issue_reporting_agent", "issue_filler_agent"]:
        workflow.add_conditional_edges(
            agent_node,
            route_after_agent,
            common_routing
        )
    
    return workflow.compile()


def get_graph_with_langgraph_welcome():
    """Get the compiled graph with LangGraph welcome agent"""
    return build_graph_with_langgraph_welcome()

