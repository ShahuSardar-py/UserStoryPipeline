"""
LangGraph Edge Functions for conditional routing
"""

from typing import Literal
from graph.state import GraphState, EmailType


def route_after_email_parser(state: GraphState) -> Literal["content_generator", "handle_error"]:
    """
    Route to Content Generator based on email type
    
    Args:
        state: Current graph state
        
    Returns:
        Next node to route to
    """
    email_type = state.get("email_type")
    parsing_error = state.get("parsing_error")
    
    # Check for parsing errors
    if parsing_error:
        return "handle_error"
    
    # Route based on email type
    if email_type in [EmailType.NEW_RFQ, EmailType.CHANGE_REQUEST]:
        return "content_generator"
    else:
        state["status"] = "error"
        state["message"] = f"Unknown email type: {email_type}"
        return "handle_error"


def route_after_content_generator(state: GraphState) -> Literal["user_story_generator", "backlog_checker", "handle_error"]:
    """
    Route after Content Generator based on email type
    
    Args:
        state: Current graph state
        
    Returns:
        Next node to route to
    """
    email_type = state.get("email_type")
    content_error = state.get("content_error")
    
    # Check for content generation errors
    if content_error:
        return "handle_error"
    
    # Route based on email type
    if email_type == EmailType.NEW_RFQ:
        return "user_story_generator"
    elif email_type == EmailType.CHANGE_REQUEST:
        return "backlog_checker"
    else:
        state["status"] = "error"
        state["message"] = f"Unknown email type for content generation: {email_type}"
        return "handle_error"


def route_after_backlog_checker(state: GraphState) -> Literal["user_story_generator", "handle_duplicate"]:
    """
    Route after Backlog Checker
    
    Args:
        state: Current graph state
        
    Returns:
        Next node to route to
    """
    is_duplicate = state.get("is_duplicate", False)
    new_requirements = state.get("new_requirements", [])
    
    # If all requirements are duplicates, handle as duplicate
    if is_duplicate and not new_requirements:
        return "handle_duplicate"
    # If there are new requirements, generate stories for them
    else:
        return "user_story_generator"


def route_after_user_story_generator(state: GraphState) -> Literal["excel_writer", "handle_error", "handle_duplicate"]:
    """
    Route after User Story Generator
    
    Args:
        state: Current graph state
        
    Returns:
        Next node to route to
    """
    stories_error = state.get("stories_error")
    generated_stories = state.get("generated_stories", [])
    
    if stories_error:
        return "handle_error"
    elif len(generated_stories) == 0:
        # No new stories were generated (all requirements already exist)
        return "handle_duplicate"
    else:
        return "excel_writer"

