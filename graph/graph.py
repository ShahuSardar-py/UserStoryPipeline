"""
Main LangGraph Workflow - Email Parser to User Story Generator

This module defines the complete LangGraph workflow with:
- Email Parser Agent (Node 1)
- Content Generator Agent (Node 2)
- User Story Generator Agent (Node 3)
- Backlog Checker (for change requests)
- Excel Writer Tool
"""

from langgraph.graph import StateGraph, END
from graph.state import GraphState, EmailType
from graph.edges import (
    route_after_email_parser,
    route_after_content_generator,
    route_after_backlog_checker,
    route_after_user_story_generator
)
from agents.emailparser import parse_email
from agents.contentgen import content_generator_node
from agents.user_story_gen import user_story_generator_node
from tools.backlogcheck import backlog_checker_node
from tools.excelwriter import excel_writer_node


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow
    
    Returns:
        Compiled StateGraph workflow
    """
    # Create the workflow
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("email_parser", parse_email)
    workflow.add_node("content_generator", content_generator_node)
    workflow.add_node("backlog_checker", backlog_checker_node)
    workflow.add_node("user_story_generator", user_story_generator_node)
    workflow.add_node("excel_writer", excel_writer_node)
    workflow.add_node("handle_error", handle_error_node)
    workflow.add_node("handle_duplicate", handle_duplicate_node)
    
    # Set entry point
    workflow.set_entry_point("email_parser")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "email_parser",
        route_after_email_parser,
        {
            "content_generator": "content_generator",
            "handle_error": "handle_error"
        }
    )
    
    workflow.add_conditional_edges(
        "content_generator",
        route_after_content_generator,
        {
            "user_story_generator": "user_story_generator",
            "backlog_checker": "backlog_checker",
            "handle_error": "handle_error"
        }
    )
    
    workflow.add_conditional_edges(
        "backlog_checker",
        route_after_backlog_checker,
        {
            "user_story_generator": "user_story_generator",
            "handle_duplicate": "handle_duplicate"
        }
    )
    
    workflow.add_conditional_edges(
        "user_story_generator",
        route_after_user_story_generator,
        {
            "excel_writer": "excel_writer",
            "handle_error": "handle_error"
        }
    )
    
    # Add edges from error and duplicate handlers to end
    workflow.add_edge("handle_error", END)
    workflow.add_edge("handle_duplicate", END)
    workflow.add_edge("excel_writer", END)
    
    # Compile the workflow
    return workflow.compile()


def handle_error_node(state: GraphState) -> GraphState:
    """
    Handle error state
    
    Args:
        state: Current graph state with error information
        
    Returns:
        Updated state with error message
    """
    return {
        **state,
        "status": "error",
        "message": state.get("message", "An unknown error occurred")
    }


def handle_duplicate_node(state: GraphState) -> GraphState:
    """
    Handle duplicate/existing stories state
    
    For change requests where stories already exist
    
    Args:
        state: Current graph state with existing_stories
        
    Returns:
        Updated state with duplicate information
    """
    existing_stories = state.get("existing_stories", [])
    
    return {
        **state,
        "status": "duplicate",
        "message": f"Found {len(existing_stories)} existing story(s) that match this change request"
    }


# Singleton workflow instance
_workflow = None


def get_workflow() -> StateGraph:
    """
    Get the compiled workflow instance (singleton)
    
    Returns:
        Compiled LangGraph workflow
    """
    global _workflow
    if _workflow is None:
        _workflow = create_workflow()
    return _workflow


def run_workflow(email_content: str, subject: str = "", sender: str = "") -> GraphState:
    """
    Run the complete workflow with an email
    
    Args:
        email_content: The raw email content
        subject: Email subject line
        sender: Email sender address
        
    Returns:
        Final state after workflow completion
    """
    workflow = get_workflow()
    
    # Create initial state
    initial_state: GraphState = {
        "raw_email": email_content,
        "email_subject": subject,
        "email_sender": sender,
        "email_type": None,
        "parsed_email": None,
        "parsing_error": None,
        "requirement_doc": None,
        "change_request_doc": None,
        "generated_content": None,
        "content_error": None,
        "existing_stories": [],
        "is_duplicate": False,
        "generated_stories": [],
        "stories_error": None,
        "status": "pending",
        "message": None
    }
    
    # Run the workflow
    result = workflow.invoke(initial_state)
    
    return result


# For testing purposes
if __name__ == "__main__":
    # Test the workflow
    test_email = """
    Hello,
    
    I would like to request a new feature for our inventory management system.
    We need to add a supplier management module with the following requirements:
    
    1. Add new suppliers with contact information
    2. Edit existing supplier information
    3. View supplier list with search functionality
    4. Delete suppliers (soft delete)
    5. Track supplier performance ratings
    
    Please provide a quote for this development.
    
    Best regards,
    John from ABC Corp
    """
    
    result = run_workflow(
        email_content=test_email,
        subject="New Feature Request - Supplier Management",
        sender="john@abccorp.com"
    )
    
    print("Status:", result.get("status"))
    print("Message:", result.get("message"))
    print("Email Type:", result.get("email_type"))
    print("Generated Stories:", len(result.get("generated_stories", [])))

