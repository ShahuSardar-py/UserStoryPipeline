"""
LangGraph State Schema for Email Parser to User Story Generator
"""

from typing import TypedDict, Optional, List, Dict, Any
from enum import Enum


class EmailType(str, Enum):
    """Types of emails processed by the system"""
    NEW_RFQ = "new_rfq"
    CHANGE_REQUEST = "change_request"
    UNKNOWN = "unknown"


class ParsedEmail(TypedDict):
    """Parsed email content"""
    email_type: EmailType
    sender: str
    subject: str
    raw_content: str
    extracted_info: Dict[str, Any]


class RequirementDocument(TypedDict):
    """Requirement Document structure"""
    doc_id: str
    title: str
    description: str
    requirements: List[str]
    priority: str
    generated_content: str


class ChangeRequestDocument(TypedDict):
    """Change Request Document structure"""
    cr_id: str
    title: str
    description: str
    changes: List[str]
    affected_stories: List[str]
    priority: str
    generated_content: str


class UserStory(TypedDict):
    """User Story structure"""
    story_id: str
    title: str
    description: str
    acceptance_criteria: List[str]
    priority: str
    status: str
    related_requirement: Optional[str]
    related_cr: Optional[str]


class GraphState(TypedDict):
    """
    Main state schema for the LangGraph workflow
    
    This state is passed between nodes in the graph
    """
    # Input
    raw_email: str
    email_subject: Optional[str]
    email_sender: Optional[str]
    
    # After Email Parser Agent
    email_type: Optional[EmailType]
    parsed_email: Optional[ParsedEmail]
    parsing_error: Optional[str]
    
    # After Content Generator Agent
    requirement_doc: Optional[RequirementDocument]
    change_request_doc: Optional[ChangeRequestDocument]
    generated_content: Optional[str]
    content_error: Optional[str]
    
    # After Backlog Checker (for change requests)
    existing_stories: List[UserStory]
    is_duplicate: bool
    
    # After User Story Generator
    generated_stories: List[UserStory]
    stories_error: Optional[str]
    
    # Final output
    status: str  # "success", "error", "duplicate"
    message: Optional[str]

