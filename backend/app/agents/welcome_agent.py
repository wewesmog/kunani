"""
Welcome agent - handles user triage and routing decisions.
Simple function, no framework overhead.
"""

from app.shared_services.llm import call_llm_api
from app.shared_services.logger_setup import setup_logger
from app.prompts.welcome_prompt import get_welcome_prompt
from app.models.najua_models import WelcomeHandoffResponse

logger = setup_logger()



def welcome_agent(conversation_history: list) -> WelcomeHandoffResponse:
    """
    Welcome agent - triages user input and decides routing.
    
    Args:
        conversation_history: List of message dicts [{"role": "user/assistant", "content": "..."}]
    
    Returns:
        HandoffResponses with routing decision
    """
    prompt = get_welcome_prompt()
    
    # Build messages: system prompt + conversation history
    messages = [{"role": "system", "content": prompt}] + conversation_history
    
    # Call LLM with structured output using instructor
    handoff_decision: WelcomeHandoffResponse = call_llm_api(
        messages=messages,
        response_format=WelcomeHandoffResponse,
        model="tngtech/tng-r1t-chimera:free",
        provider="openrouter",
        temperature=0.3
    )
    
    print(f"Welcome agent response: data {handoff_decision.model_dump_json()}")
    logger.info(f"Welcome agent completed. Handoff decision: {handoff_decision}")
    
    return handoff_decision
