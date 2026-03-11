"""
Backlog Checker Tool - Check Excel backlog for existing user stories

This tool is used for change_request emails to check if:
- Similar requests already exist in the backlog
- NEW requirements that don't match existing stories
- Returns both existing (duplicate) and new requirements separately
"""

import os
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from graph.state import GraphState, UserStory, EmailType


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
) -> Tuple[List[UserStory], List[str]]:
    """
    Check which changes already exist and which are new
    
    Args:
        change_request_doc: The change request document
        backlog_df: DataFrame of existing stories
        
    Returns:
        Tuple of (existing_stories, new_requirements not in backlog)
    """
    if backlog_df.empty:
        return [], change_request_doc.get("changes", [])
    
    changes = change_request_doc.get("changes", [])
    existing_stories: List[UserStory] = []
    new_requirements: List[str] = []
    
    for change in changes:
        change_lower = change.lower()
        change_keywords = [word for word in change_lower.split() if len(word) > 3]
        
        matched_story = None
        max_matches = 0
        
        for _, row in backlog_df.iterrows():
            title = str(row.get("Title", "")).lower()
            description = str(row.get("Description", "")).lower()
            
            matches = sum(1 for kw in change_keywords if kw in title or kw in description)
            
            if matches > max_matches:
                max_matches = matches
                matched_story = {
                    "story_id": str(row.get("Story ID", "")),
                    "title": str(row.get("Title", "")),
                    "description": str(row.get("Description", "")),
                    "acceptance_criteria": str(row.get("Acceptance Criteria", "")).split("|"),
                    "priority": str(row.get("Priority", "Medium")),
                    "status": str(row.get("Status", "To Do")),
                    "related_requirement": str(row.get("Related Requirement", "")),
                    "related_cr": str(row.get("Related CR", ""))
                }
        
        if max_matches >= 2 and matched_story:
            existing_stories.append(matched_story)
        else:
            new_requirements.append(change)
    
    return existing_stories, new_requirements


def backlog_checker_node(state: GraphState) -> GraphState:
    """
    Backlog Checker Node
    
    For change_request emails, checks:
    - Which changes already exist (duplicates)
    - Which changes are NEW and need new stories
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with existing_stories and new_requirements
    """
    from config import BACKLOG_FILE_PATH, BACKLOG_SHEET_NAME
    
    email_type = state.get("email_type")
    change_request_doc = state.get("change_request_doc")
    
    if email_type != EmailType.CHANGE_REQUEST:
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False,
            "new_requirements": []
        }
    
    if not change_request_doc:
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False,
            "new_requirements": [],
            "content_error": "No change request document available for backlog check"
        }
    
    try:
        backlog_df = read_excel_backlog(BACKLOG_FILE_PATH, BACKLOG_SHEET_NAME)
        
        existing_stories, new_requirements = check_existing_stories(change_request_doc, backlog_df)
        
        updated_cr_doc = change_request_doc.copy()
        updated_cr_doc["changes"] = new_requirements
        updated_cr_doc["new_requirements"] = new_requirements
        
        has_new_requirements = len(new_requirements) > 0
        
        return {
            **state,
            "existing_stories": existing_stories,
            "is_duplicate": not has_new_requirements,
            "new_requirements": new_requirements,
            "change_request_doc": updated_cr_doc,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "existing_stories": [],
            "is_duplicate": False,
            "new_requirements": change_request_doc.get("changes", []) if change_request_doc else [],
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

