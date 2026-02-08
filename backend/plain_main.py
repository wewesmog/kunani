from app.shared_services.llm import call_llm_api
from app.shared_services.logger_setup import setup_logger
from app.agents.welcome_agent import welcome_agent
from app.models.najua_models import WelcomeHandoffResponses
import json
from langraph import LangGraph
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

logger = setup_logger()

langgraph = LangGraph()


def router_after_welcome_agent(handoff_responses: WelcomeHandoffResponses, state: dict) -> str:
    """Process the handoff responses and route to appropriate agents"""
    if not handoff_responses.responses:
        return "No routing decision made."
    
    user_messages = []
    
    # Process ALL responses (handle multiple agents)
    for handoff in handoff_responses.responses:
        print(f"Routing to {handoff.agent}")
        logger.info(f"Routing decision: {handoff.agent} - {handoff.reasoning}")
        
        # Route to the appropriate agent based on the decision
        if handoff.agent == "issue_reporting_agent":
            # TODO: Import and call issue_reporting_agent
            # result = issue_reporting_agent(state, handoff.message_to_agent)
            message = handoff.message_to_user or "Routing to issue reporting agent..."
            user_messages.append(message)
        
        elif handoff.agent == "issue_enquiry_agent":
            # TODO: Import and call issue_enquiry_agent
            # result = issue_enquiry_agent(state, handoff.message_to_agent)
            message = handoff.message_to_user or "Routing to issue enquiry agent..."
            user_messages.append(message)
        
        elif handoff.agent == "respond_to_user_agent":
            # TODO: Import and call respond_to_user_agent
            # result = respond_to_user_agent(state, handoff.message_to_agent)
            message = handoff.message_to_user or "Continuing conversation..."
            user_messages.append(message)
    
    # Combine all user messages
    if user_messages:
        return "\n".join(user_messages)
    
    return "No agent found"


if __name__ == "__main__":
    # state
    state = {
        "messages": []
    }
    while True:
        input_message = input("Enter your message: ")
        state["messages"].append({"role": "user", "content": input_message})
        response = welcome_agent(state)
        
        # Process routing decision
        user_message = router_after_welcome_agent(response, state)
        
        # Convert structured response to JSON string for messages
        response_json = response.model_dump_json() if hasattr(response, 'model_dump_json') else json.dumps(response.model_dump())
        
        print(f"Response: {response}")
        print(f"Response JSON: {response_json}")
        print(f"User Message: {user_message}")
        
        # Append the JSON string to messages (for LLM context)
        state["messages"].append({"role": "assistant", "content": response_json})
        # Also append the user-facing message
        state["messages"].append({"role": "assistant", "content": user_message})
        # logger.info(f"State: {state}")
        # print(f"State: {state}")
        if input_message.lower() == "exit" or input_message.lower() == "quit":
            break
    logger.info(f"Exiting the program")