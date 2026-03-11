"""
Backlog Checker Tool - Check Excel backlog for existing user stories

This tool is used for change_request emails to check if:
- Similar requests already exist in the backlog
- New stories need to be generated or existing ones modified
"""

import os
from typing import List, Dict, Any, Optional
import pandas as pd
from graph.state import GraphState, UserStory


def read_excel_backlog(file_path: str, sheet_name: str = "UserStories") -> pd.DataFrame:
    """
    Read the Excel backlog file
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to read
        
    Returns:
        DataFrame containing the backlog
    """
    if not os.path.exists(file_path):
        # Return empty DataFrame if file doesn't exist
        return pd.DataFrame(columns=[
            "Story ID", "Title", "Description", "Acceptance Criteria",
            "Priority", "Status", "Related Requirement", "Related CR"
        ])
    
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return pd.DataFrame()


def check_existing_stories(
    change_request_doc: Dict[str, Any],
    backlog_df: pd.DataFrame
) -> tuple[List[UserStory], bool]:
    """
    Check if similar stories already exist in the backlog
    
    Args:
        change_request_doc: The change request document
        backlog_df: DataFrame of existing stories
        
    Returns:
        Tuple of (existing_stories, is_duplicate)
    """
    if backlog_df.empty:
        return [], False
    
    # Extract keywords from change request
    cr_title = change_request_doc.get("title", "").lower()
    cr_description = change_request_doc.get("description", "").lower()
    cr_changes = " ".join(change_request_doc.get("changes", [])).lower()
    
    search_text = f"{cr_title} {cr_description} {cr_changes}"
    search_keywords = [word for word in search_text.split() if len(word) > 3]
    
    existing_stories: List[UserStory] = []
    
    for _, row in backlog_df.iterrows():
        title = str(row.get("Title", "")).lower()
        description = str(row.get("Description", "")).lower()
        
        # Check for keyword matches
        matches = sum(1 for kw in search_keywords if kw in title or kw in description)
        
        if matches >= 2:  # At least 2 keyword matches
            story: UserStory = {
                "story_id": str(row.get("Story ID", "")),
                "title": str(row.get("Title", "")),
                "description": str(row.get("Description", "")),
                "acceptance_criteria": str(row.get("Acceptance Criteria", "")).split("|"),
                "priority": str(row.get("Priority", "Medium")),
                "status": str(row.get("Status", "To Do")),
                "related_requirement": str(row.get("Related Requirement", "")),
                "related_cr": str(row.get("Related CR", ""))
            }
            existing_stories.append(story)
    
    # Consider it a duplicate if we found closely matching stories
    is_duplicate = len(existing_stories) > 0
    
    return existing_stories, is_duplicate


def backlog_checker_node(state: GraphState) -> GraphState:
    """
    Backlog Checker Node
    
    For change_request emails, checks if similar stories exist
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with existing_stories and is_duplicate
    """
    from config import BACKLOG_FILE_PATH, BACKLOG_SHEET_NAME
    
    email_type = state.get("email_type")
    change_request_doc = state.get("change_request_doc")
    
    # Only run for change requests
    if email_type != "change_request":
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False
        }
    
    if not change_request_doc:
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False,
            "content_error": "No change request document available for backlog check"
        }
    
    try:
        # Read the backlog
        backlog_df = read_excel_backlog(BACKLOG_FILE_PATH, BACKLOG_SHEET_NAME)
        
        # Check for existing stories
        existing_stories, is_duplicate = check_existing_stories(change_request_doc, backlog_df)
        
        return {
            **state,
            "existing_stories": existing_stories,
            "is_duplicate": is_duplicate,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False,
            "content_error": f"Failed to check backlog: {str(e)}"
        }


# For testing purposes
if __name__ == "__main__":
    # Test the backlog checker
    test_state: GraphState = {
        "email_type": "change_request",
        "change_request_doc": {
            "cr_id": "CR-20240101-001",
            "title": "Update Supplier Management",
            "description": "Add new fields to supplier management",
            "changes": ["Add supplier rating", "Add supplier category"],
            "affected_stories": [],
            "priority": "Medium"
        }
    }
    
    result = backlog_checker_node(test_state)
    print("Existing Stories:", len(result.get("existing_stories", [])))
    print("Is Duplicate:", result.get("is_duplicate"))

