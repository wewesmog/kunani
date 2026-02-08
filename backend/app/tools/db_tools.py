"""
LangGraph tools for database operations
"""
from typing import List, Optional, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.shared_services.db import save_issue, get_issue, get_all_issues, update_issue_status


class SaveIssueInput(BaseModel):
    """Input for saving an issue"""
    title: str = Field(..., description="Title of the issue")
    description: str = Field(..., description="Detailed description of the issue")
    status: str = Field(default="open", description="Status: open, in_progress, resolved, closed")
    priority: str = Field(default="medium", description="Priority: low, medium, high, critical")
    category: Optional[str] = Field(None, description="Category of the issue")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class GetIssueInput(BaseModel):
    """Input for getting an issue"""
    issue_id: str = Field(..., description="The issue ID to retrieve")


class GetIssuesInput(BaseModel):
    """Input for getting multiple issues"""
    limit: int = Field(default=50, description="Maximum number of issues to return")
    status: Optional[str] = Field(None, description="Filter by status: open, in_progress, resolved, closed")


class UpdateIssueStatusInput(BaseModel):
    """Input for updating issue status"""
    issue_id: str = Field(..., description="The issue ID to update")
    status: str = Field(..., description="New status: open, in_progress, resolved, closed")


@tool(args_schema=SaveIssueInput)
def save_issue_tool(title: str, description: str, status: str = "open", 
                    priority: str = "medium", category: Optional[str] = None,
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Save a new issue to the database.
    
    Args:
        title: Title of the issue
        description: Detailed description
        status: Status (default: open)
        priority: Priority level (default: medium)
        category: Optional category
        tags: Optional list of tags
        metadata: Optional metadata dictionary
    
    Returns:
        The saved issue as a dictionary
    """
    if tags is None:
        tags = []
    if metadata is None:
        metadata = {}
    
    # Generate unique issue ID
    issue_id = f"ISS-{uuid.uuid4().hex[:8].upper()}"
    
    issue_data = {
        "issue_id": issue_id,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "category": category,
        "tags": tags,
        "metadata": metadata
    }
    
    try:
        saved_issue = save_issue(issue_data)
        return {
            "success": True,
            "issue": dict(saved_issue),
            "message": f"Issue {issue_id} saved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to save issue: {e}"
        }


@tool(args_schema=GetIssueInput)
def get_issue_tool(issue_id: str) -> Dict[str, Any]:
    """
    Get an issue by its ID.
    
    Args:
        issue_id: The issue ID to retrieve
    
    Returns:
        The issue as a dictionary, or None if not found
    """
    try:
        issue = get_issue(issue_id)
        if issue:
            return {
                "success": True,
                "issue": dict(issue),
                "message": f"Issue {issue_id} retrieved successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Issue {issue_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get issue: {e}"
        }


@tool(args_schema=GetIssuesInput)
def get_all_issues_tool(limit: int = 50, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all issues with optional filtering.
    
    Args:
        limit: Maximum number of issues to return (default: 50)
        status: Optional status filter (open, in_progress, resolved, closed)
    
    Returns:
        List of issues
    """
    try:
        issues = get_all_issues(limit=limit, status=status)
        return {
            "success": True,
            "issues": [dict(issue) for issue in issues],
            "count": len(issues),
            "message": f"Retrieved {len(issues)} issue(s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get issues: {e}"
        }


@tool(args_schema=UpdateIssueStatusInput)
def update_issue_status_tool(issue_id: str, status: str) -> Dict[str, Any]:
    """
    Update the status of an issue.
    
    Args:
        issue_id: The issue ID to update
        status: New status (open, in_progress, resolved, closed)
    
    Returns:
        The updated issue
    """
    try:
        updated = update_issue_status(issue_id, status)
        if updated:
            return {
                "success": True,
                "issue": dict(updated),
                "message": f"Issue {issue_id} status updated to {status}"
            }
        else:
            return {
                "success": False,
                "message": f"Issue {issue_id} not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to update issue: {e}"
        }


def get_db_tools():
    """Get all database tools"""
    return [
        save_issue_tool,
        get_issue_tool,
        get_all_issues_tool,
        update_issue_status_tool
    ]

