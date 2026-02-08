"""
Conversation loop using LangGraph for flow control only.
Agents use instructor for LLM calls.
"""

import asyncio
import sys
from app.shared_services.logger_setup import setup_logger
from app.graph.najua_graph import get_graph
from app.models.najua_models import NajuaState

logger = setup_logger()

# Set Windows event loop policy for compatibility
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def run_conversation():
    """Run the conversation loop with LangGraph flow control"""
    
    graph = get_graph()

    # State - your memory/context
    state: NajuaState = {
        "conversation_history": [],
        "current_node": None,
        "handoff_decision": None,
        "current_issues": [],
    }
    
    print("Najua System - Enter 'exit' to quit\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ["exit", "quit"]:
            break
        
        # Add user message to conversation
        state["conversation_history"].append({"role": "user", "content": user_input})
        
        try:
            # Invoke graph - LangGraph handles flow/routing
            # Entry point is determined by agent_after_human_response from previous handoff
            result = await graph.ainvoke(state)
            
            # Update state with result
            state = result
            
            # Display the last assistant message if any
            conversation_history = result.get("conversation_history", [])
            if conversation_history:
                last_message = conversation_history[-1]
                if last_message.get("role") == "assistant":
                    print(f"\nAssistant: {last_message.get('content', '')}\n")
            
            logger.info(f"Graph execution completed. Current node: {result.get('current_node')}")
            
        except Exception as e:
            logger.error(f"Error in graph execution: {e}", exc_info=True)
            print(f"\nError: {e}\n")
    
    logger.info("Exiting the program")


if __name__ == "__main__":
    asyncio.run(run_conversation())
