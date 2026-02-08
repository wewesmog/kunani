"""
Issue filler agent - helps users fill in issue details.
Simple function, no framework overhead.
"""

from app.shared_services.llm import call_llm_api
from app.shared_services.logger_setup import setup_logger
from app.prompts.issue_filler_prompt import get_issue_filler_prompt
from app.models.najua_models import IssuesFillerResponse, NajuaState, IssueFillerHandoffResponse
from app.shared_services.issue_validation import validate_issues, get_missing_fields

logger = setup_logger()


def issue_filler_agent(conversation_history: list, state: NajuaState) -> IssueFillerHandoffResponse:
    """
    Issue filler agent - helps users fill in issue details.
    Updates state, validates completion, and creates handoff response programmatically.
    
    Args:
        conversation_history: List of message dicts [{"role": "user/assistant", "content": "..."}]
        state: Current NajuaState to check existing issues and update
    
    Returns:
        IssueFillerHandoffResponse object with validated handoff decision
    """
    prompt = get_issue_filler_prompt(state)
    
    # Build messages
    messages = [{"role": "system", "content": prompt}] + conversation_history
    
    # Call LLM with structured output
    llm_response: IssuesFillerResponse = call_llm_api(
        messages=messages,
        response_format=IssuesFillerResponse,
        model="gemini-2.5-flash",
        provider="gemini",
        temperature=0.3
    )

    print(f"Issue filler agent LLM response: data {llm_response.model_dump_json()}")
    logger.info(f"Issue filler agent LLM response: {llm_response}")
    
    # Update state with issues from LLM response - merge with existing issues
    existing_issues = state.get("current_issues") or []
    
    if llm_response.issues:
        # Merge: Update existing issues with new data from LLM
        # For simplicity, we'll work with the latest issue (index 0) or create new one
        if existing_issues and len(existing_issues) > 0:
            # Update the first issue with new data from LLM response
            existing_issue_dict = existing_issues[0]
            if hasattr(existing_issue_dict, 'model_dump'):
                existing_issue_dict = existing_issue_dict.model_dump()
            elif hasattr(existing_issue_dict, 'dict'):
                existing_issue_dict = existing_issue_dict.dict()
            
            # Get new issue data from LLM
            new_issue = llm_response.issues[0]
            if hasattr(new_issue, 'model_dump'):
                new_issue_dict = new_issue.model_dump()
            else:
                new_issue_dict = new_issue
            
            # Merge: new data overrides existing, but preserve existing if new is None/empty
            merged_issue = {}
            for field in ["issue_type", "issue_description", "issue_location", "issue_date", "issue_time", "issue_severity"]:
                new_value = new_issue_dict.get(field)
                existing_value = existing_issue_dict.get(field)
                # Use new value if provided and not None/empty, otherwise keep existing
                if new_value is not None and (not isinstance(new_value, str) or new_value.strip() != ""):
                    merged_issue[field] = new_value
                elif existing_value is not None:
                    merged_issue[field] = existing_value
            
            # Update state with merged issue
            from app.models.najua_models import IssueFillerResponse
            state["current_issues"] = [IssueFillerResponse(**merged_issue)]
        else:
            # No existing issues, use LLM response directly
            state["current_issues"] = llm_response.issues
    # If LLM returns None for issues, preserve existing state (don't clear it)
    
    # Validate mandatory fields
    all_complete, missing_info = validate_issues(llm_response.issues)
    
    # Determine handoff based on validation + LLM suggestion
    suggested_handoff = llm_response.suggested_handoff or "continue_filling"
    
    # Validation override: If LLM suggests issue_reporting_agent but fields are incomplete, override to continue_filling
    if suggested_handoff == "issue_reporting_agent" and not all_complete:
        logger.warning(f"LLM suggested handoff to issue_reporting_agent but fields incomplete: {missing_info}. Overriding to continue_filling.")
        suggested_handoff = "continue_filling"
        # Update message to inform user we need more info
        if llm_response.message_to_user:
            missing_fields_str = "; ".join(missing_info)
            llm_response.message_to_user = f"{llm_response.message_to_user}\n\nI still need some information: {missing_fields_str}. Could you please provide these details?"
    
    # Create handoff response programmatically
    if suggested_handoff == "issue_reporting_agent":
        # All fields complete - handoff to issue_reporting_agent
        handoff = IssueFillerHandoffResponse(
            agent="issue_reporting_agent",
            reasoning=f"All mandatory fields are complete. Ready to save the issue(s). Missing info: {missing_info if missing_info else 'None'}",
            message_to_user=llm_response.message_to_user or "Thank you! I have all the information needed. I'll now save your issue.",
            agent_after_human_response="issue_reporting_agent"
        )
    elif suggested_handoff == "welcome_agent":
        # User wants to stop/change topic
        handoff = IssueFillerHandoffResponse(
            agent="welcome_agent",
            reasoning="User wants to stop filling or change topic",
            message_to_user=llm_response.message_to_user or "Understood. How else can I help you?",
            agent_after_human_response="welcome_agent"
        )
    elif suggested_handoff == "respond_to_user_agent":
        # Need clarification
        handoff = IssueFillerHandoffResponse(
            agent="respond_to_user_agent",
            reasoning="Need clarification from user",
            message_to_user=llm_response.message_to_user or "Could you please clarify?",
            agent_after_human_response="issue_filler_agent"
        )
    else:  # continue_filling (default)
        # Continue asking for more fields - handoff to respond_to_user_agent to send message and wait for user input
        handoff = IssueFillerHandoffResponse(
            agent="respond_to_user_agent",
            reasoning=f"Continuing to fill issue details. Missing fields: {missing_info if missing_info else 'None'}. Need to ask user for more information.",
            message_to_user=llm_response.message_to_user or "I need a bit more information to complete your report.",
            agent_after_human_response="issue_filler_agent"  # Come back to issue_filler_agent after user responds
        )
    
    logger.info(f"Issue filler agent handoff: {handoff.agent} - {handoff.reasoning}")
    return handoff