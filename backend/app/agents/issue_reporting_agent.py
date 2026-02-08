"""
Issue reporting agent - saves issues that have been filled.
Simple function, no framework overhead.
"""

from app.shared_services.llm import call_llm_api
from app.shared_services.logger_setup import setup_logger
from app.prompts.issue_reporting_prompt import get_issue_reporting_prompt
from app.models.najua_models import IssueReportingHandoffResponse, NajuaState

logger = setup_logger()


def issue_reporting_agent(conversation_history: list, state: NajuaState) -> IssueReportingHandoffResponse:
    """
    Issue reporting agent - saves issues that have been filled by issue_filler_agent.
    
    Args:
        conversation_history: List of message dicts [{"role": "user/assistant", "content": "..."}]
        state: Current NajuaState with issues to save
    
    Returns:
        IssueReportingHandoffResponse object (cannot handoff to itself, can handoff back to issue_filler_agent)
    """
    prompt = get_issue_reporting_prompt(state)
    
    # Build messages
    messages = [{"role": "system", "content": prompt}] + conversation_history
    
    # Call LLM with structured output - using model that prevents self-handoff
    response: IssueReportingHandoffResponse = call_llm_api(
        messages=messages,
        response_format=IssueReportingHandoffResponse,
        model="gpt-4o-mini",
        provider="openai",
        temperature=0.3
    )

    print(f"Issue reporting agent response: data {response.model_dump_json()}")
    logger.info(f"Issue reporting agent response: {response}")
    
    # TODO: Update issue_status to "saved" in state if agent confirms saving
    # This could be done here or in the node
    
    return response
