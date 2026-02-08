from typing import List, Optional, Literal, Dict, Any, TypedDict, Union
from pydantic import BaseModel, Field, model_validator
from datetime import datetime


class WelcomeHandoffResponse(BaseModel):
    agent: Literal["issue_reporting_agent", "issue_filler_agent", "respond_to_user_agent", ] = Field(
        ..., description="The name of the agent to handoff to"
    )
    reasoning: str = Field(..., description="The reasoning for the choice of agent")
    message_to_agent: Optional[str] = Field(None, description="The message to the agent")
    message_to_user: Optional[str] = Field(None, description="The message to the user. Only provide this if agent is 'respond_to_user_agent'.")
    agent_after_human_response: Literal["issue_reporting_agent", "issue_filler_agent", "respond_to_user_agent", "welcome_agent"] = Field(
        default="welcome_agent",
        description="The agent to handle the user's response. Defaults to 'welcome_agent' if message_to_user is provided."
    )
    
    @model_validator(mode='after')
    def validate_message_to_user(self):
        """message_to_user should only be set if agent is respond_to_user_agent"""
        if self.message_to_user and self.agent != "respond_to_user_agent":
            # Clear message_to_user if agent is not respond_to_user_agent
            self.message_to_user = None
        return self


class WelcomeHandoffResponses(BaseModel):
    responses: List[WelcomeHandoffResponse] = Field(..., description="The list of handoff responses")


class IssueReportingHandoffResponse(BaseModel):
    """Handoff response for issue reporting agent - cannot handoff to itself"""
    agent: Literal["issue_filler_agent", "issue_enquiry_agent", "respond_to_user_agent", "welcome_agent"] = Field(
        ..., description="The name of the agent to handoff to (cannot be issue_reporting_agent). Can handoff back to issue_filler_agent if more details needed."
    )
    reasoning: str = Field(..., description="The reasoning for the choice of agent")
    message_to_agent: Optional[str] = Field(None, description="The message to the agent")
    message_to_user: Optional[str] = Field(None, description="The message to the user. Only provide this if agent is 'respond_to_user_agent'.")
    agent_after_human_response: Literal["issue_reporting_agent", "issue_enquiry_agent", "respond_to_user_agent", "welcome_agent"] = Field(
        default="welcome_agent",
        description="The agent to handle the user's response. Defaults to 'welcome_agent' if message_to_user is provided."
    )
    
    @model_validator(mode='after')
    def validate_message_to_user(self):
        """message_to_user should only be set if agent is respond_to_user_agent"""
        if self.message_to_user and self.agent != "respond_to_user_agent":
            # Clear message_to_user if agent is not respond_to_user_agent
            self.message_to_user = None
        return self


class IssueReportingHandoffResponses(BaseModel):
    responses: List[IssueReportingHandoffResponse] = Field(..., description="The list of handoff responses")

class IssueFillerResponse(BaseModel):
    
    issue_type: Optional[Literal["Infrastructure", "Education", "Health", "Agriculture", "Environment", "Transport", "Finance", "Social Welfare", "Other"]  ] = Field(None, description="The type of issue")
    issue_description: Optional[str] = Field(None, description="The description of the issue")
    issue_location: Optional[str] = Field(None, description="The location of the issue")
    issue_date: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="The date of the issue (YYYY-MM-DD)")
    issue_time: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%H:%M"), description="The time of the issue (HH:MM, 24-hour format)")
    issue_severity: Optional[Literal["low", "medium", "high", "critical"]] = Field(None, description="The severity of the issue - infer from context (e.g., depth, impact, damage), do NOT ask directly")

class IssuesFillerResponse(BaseModel): 
    message_to_user: Optional[str] = Field(None, description="The message to the user")
    issues: Optional[List[IssueFillerResponse]] = Field(None, description="The list of issues")
    suggested_handoff: Optional[Literal["continue_filling", "issue_reporting_agent", "welcome_agent", "respond_to_user_agent"]] = Field(
        default="continue_filling",
        description="Suggested handoff: 'continue_filling' to keep asking, 'issue_reporting_agent' if complete, 'welcome_agent' if user wants to stop, 'respond_to_user_agent' for clarifications"
    )


class IssueFillerHandoffResponse(BaseModel):
    """Handoff response for issue filler agent - validates completion before allowing handoff to issue_reporting_agent. Cannot handoff to itself."""
    agent: Literal["issue_reporting_agent", "welcome_agent", "respond_to_user_agent"] = Field(
        ..., description="The name of the agent to handoff to (cannot be issue_filler_agent)"
    )
    reasoning: str = Field(..., description="The reasoning for the choice of agent")
    message_to_agent: Optional[str] = Field(None, description="The message to the agent")
    message_to_user: Optional[str] = Field(None, description="The message to the user")
    agent_after_human_response: Literal["issue_filler_agent", "issue_reporting_agent", "welcome_agent", "respond_to_user_agent"] = Field(
        default="issue_filler_agent",
        description="The agent to handle the user's response. Defaults to 'issue_filler_agent' to continue filling."
    )

class Issue(BaseModel):
    issue_status: Literal["in-progress","completed", "saved", "not-saved"]
    issue_type: Literal["Infrastructure", "Education", "Health", "Agriculture", "Environment", "Transport", "Finance", "Social Welfare", "Other"]
    issue_description: str
    issue_location: str
    issue_date: Optional[str]
    issue_time: Optional[str]
    issue_severity: Optional[Literal["low", "medium", "high", "critical"]]  # Optional - can be inferred or left blank
class NajuaState(TypedDict, total=False):
    """
    State for Najua conversation - use this as your memory.
    Simple dict structure, easy to save/load.
    """
    conversation_history: List[Dict[str, str]]  # List of {"role": "user/assistant", "content": "..."}
    current_node: Optional[str]  # Current agent/node name
    handoff_decision: Optional[Union[WelcomeHandoffResponse, IssueReportingHandoffResponse]]  # Last handoff decision (can be any type - IssueFillerHandoffResponse added after definition)
    current_issues: Optional[List[Issue]]
    # Add more fields as needed:
    # user_id: Optional[str]
    # session_id: Optional[str]
    # metadata: Dict[str, Any]
   