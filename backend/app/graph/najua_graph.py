"""
LangGraph workflow for Najua - flow control only.
Uses your agent functions as nodes.
Agents use instructor for LLM calls (no LangChain).
"""

from typing import TypedDict, Optional, Literal
from langgraph.graph import StateGraph, END, START
import os
import logging
from dotenv import load_dotenv

from app.models.najua_models import NajuaState, WelcomeHandoffResponse, IssueReportingHandoffResponse, IssueFillerHandoffResponse
from app.agents.welcome_agent import welcome_agent
from app.agents.issue_reporting_agent import issue_reporting_agent
from app.agents.issue_filler_agent import issue_filler_agent

load_dotenv()
logger = logging.getLogger(__name__)


def welcome_agent_node(state: NajuaState) -> NajuaState:
    """Welcome agent node - triages and routes"""
    conversation_history = state["conversation_history"]
    handoff_decision = welcome_agent(conversation_history)
    
    # Update state
    state["current_node"] = "welcome_agent"
    state["handoff_decision"] = handoff_decision
    
    # Add message_to_user to conversation if it exists
    if handoff_decision.message_to_user:
        state["conversation_history"].append({"role": "assistant", "content": handoff_decision.message_to_user})
    
    return state


def issue_reporting_agent_node(state: NajuaState) -> NajuaState:
    """Issue reporting agent node - saves issues"""
    conversation_history = state["conversation_history"]
    handoff_decision = issue_reporting_agent(conversation_history, state)
    
    # Update state
    state["current_node"] = "issue_reporting_agent"
    state["handoff_decision"] = handoff_decision
    
    # Add message_to_user to conversation if it exists
    if handoff_decision.message_to_user:
        state["conversation_history"].append({"role": "assistant", "content": handoff_decision.message_to_user})
    
    # TODO: Update issue_status to "saved" if agent confirms saving
    # if handoff_decision.agent != "issue_filler_agent":
    #     # Update issues status to "saved"
    
    return state


def issue_filler_agent_node(state: NajuaState) -> NajuaState:
    """Issue filler agent node - fills issue details and creates handoff"""
    conversation_history = state["conversation_history"]
    handoff_decision = issue_filler_agent(conversation_history, state)
    
    # Update state
    state["current_node"] = "issue_filler_agent"
    state["handoff_decision"] = handoff_decision
    
    # Add message_to_user to conversation if it exists
    if handoff_decision.message_to_user:
        state["conversation_history"].append({"role": "assistant", "content": handoff_decision.message_to_user})
    
    # Issues are already updated in issue_filler_agent function
    
    return state


def route_after_agent(state: NajuaState) -> str:
    """
    Route based on handoff decision from any agent.
    Returns the next node name or END.
    Note: respond_to_user_agent always ends the graph (user input expected to restart).
    """
    handoff_decision = state.get("handoff_decision")
    
    if not handoff_decision:
        logger.warning("No handoff decision found, ending")
        return END
    
    # Get agent name from handoff decision (works for all handoff response types)
    agent_name = handoff_decision.agent
    
    # Return the agent name - the mapping will handle END for respond_to_user_agent
    if agent_name == "respond_to_user_agent":
        return "respond_to_user_agent"  # Mapping will convert this to END
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
        # Map to valid entry points
        if entry_agent in ["welcome_agent", "issue_filler_agent", "issue_reporting_agent"]:
            return entry_agent
        else:
            logger.warning(f"Invalid entry agent {entry_agent}, defaulting to welcome_agent")
            return "welcome_agent"
    else:
        logger.info("No previous handoff, starting with welcome_agent")
        return "welcome_agent"


def build_graph():
    """Build the Najua workflow graph"""
    workflow = StateGraph(NajuaState)
    
    # Add nodes
    workflow.add_node("welcome_agent", welcome_agent_node)
    workflow.add_node("issue_reporting_agent", issue_reporting_agent_node)
    workflow.add_node("issue_filler_agent", issue_filler_agent_node)
    # TODO: Add more agent nodes as they're created
    
    # Conditional entry point - can start from any agent
    workflow.add_conditional_edges(
        START,
        determine_entry_point,
        {
            "welcome_agent": "welcome_agent",
            "issue_reporting_agent": "issue_reporting_agent",
            "issue_filler_agent": "issue_filler_agent",
            "issue_enquiry_agent": END,  # Not implemented
            "respond_to_user_agent": END,  # Shouldn't be entry point
        }
    )
    
    # Conditional routing from each agent based on handoff decision
    # All agents use the same routing logic - no agent can route to itself
    common_routing = {
        "issue_reporting_agent": "issue_reporting_agent",
        "issue_filler_agent": "issue_filler_agent",
        "welcome_agent": "welcome_agent",
        "respond_to_user_agent": END,  # Ends graph (user input will restart based on agent_after_human_response)
        "issue_enquiry_agent": END,  # Not implemented yet
    }
    
    for agent_node in ["welcome_agent", "issue_reporting_agent", "issue_filler_agent"]:
        workflow.add_conditional_edges(
            agent_node,
            route_after_agent,
            common_routing
        )
    
    return workflow.compile()


def get_graph():
    """Get the compiled graph"""
    return build_graph()
