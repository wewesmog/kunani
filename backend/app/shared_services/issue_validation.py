"""
Validation utilities for issue filling.
Ensures data quality before allowing handoff to issue_reporting_agent.
"""

from typing import List, Optional
from app.models.najua_models import IssueFillerResponse


def get_mandatory_fields() -> List[str]:
    """Returns list of mandatory field names for an issue"""
    # Priority removed, severity is optional (can be inferred or left blank)
    return ["issue_type", "issue_description", "issue_location"]


def is_issue_complete(issue: IssueFillerResponse) -> bool:
    """
    Check if an issue has all mandatory fields filled.
    
    Args:
        issue: IssueFillerResponse object to validate
    
    Returns:
        True if all mandatory fields are filled, False otherwise
    """
    mandatory_fields = get_mandatory_fields()
    
    for field_name in mandatory_fields:
        field_value = getattr(issue, field_name, None)
        if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
            return False
    
    return True


def get_missing_fields(issue: IssueFillerResponse) -> List[str]:
    """
    Get list of missing mandatory fields for an issue.
    
    Args:
        issue: IssueFillerResponse object to check
    
    Returns:
        List of missing mandatory field names
    """
    mandatory_fields = get_mandatory_fields()
    missing = []
    
    for field_name in mandatory_fields:
        field_value = getattr(issue, field_name, None)
        if field_value is None or (isinstance(field_value, str) and field_value.strip() == ""):
            missing.append(field_name)
    
    return missing


def validate_issues(issues: Optional[List[IssueFillerResponse]]) -> tuple:
    """
    Validate all issues in a list.
    
    Args:
        issues: List of IssueFillerResponse objects
    
    Returns:
        Tuple of (all_complete: bool, missing_fields_by_issue: List[str])
        missing_fields_by_issue contains comma-separated field names per issue
    """
    if not issues:
        return False, ["No issues provided"]
    
    all_complete = True
    missing_info = []
    
    for idx, issue in enumerate(issues):
        if not is_issue_complete(issue):
            all_complete = False
            missing = get_missing_fields(issue)
            missing_info.append(f"Issue {idx + 1}: {', '.join(missing)}")
    
    return all_complete, missing_info

