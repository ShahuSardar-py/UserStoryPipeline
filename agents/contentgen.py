"""
Content Generator Agent - Node 2 of the LangGraph workflow

This agent generates:
- Requirement Document (for new_rfq emails)
- Change Request Document (for change_request emails)
"""

from typing import Union, List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from graph.state import GraphState, EmailType, RequirementDocument, ChangeRequestDocument
import config
import uuid
from datetime import datetime


# Define structured output schemas
class RequirementDocOutput(BaseModel):
    """Structured output for Requirement Document"""
    doc_id: str = Field(description="Unique document ID")
    title: str = Field(description="Document title")
    description: str = Field(description="Overall description of requirements")
    requirements: List[str] = Field(description="List of individual requirements")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    generated_content: str = Field(description="Full generated document content in markdown")


class ChangeRequestDocOutput(BaseModel):
    """Structured output for Change Request Document"""
    cr_id: str = Field(description="Unique change request ID")
    title: str = Field(description="Change request title")
    description: str = Field(description="Description of the change")
    changes: List[str] = Field(description="List of specific changes requested")
    affected_stories: List[str] = Field(description="List of existing story IDs that might be affected")
    priority: str = Field(description="Priority level: High, Medium, or Low")
    generated_content: str = Field(description="Full generated document content in markdown")


def create_requirement_generator() -> ChatMistralAI:
    """Create LLM for requirement document generation"""
    llm = ChatMistralAI(
        model=config.MISTRAL_MODEL,
        api_key=config.MISTRAL_API_KEY,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    return llm.with_structured_output(RequirementDocOutput)


def create_change_request_generator() -> ChatMistralAI:
    """Create LLM for change request document generation"""
    llm = ChatMistralAI(
        model=config.MISTRAL_MODEL,
        api_key=config.MISTRAL_API_KEY,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    return llm.with_structured_output(ChangeRequestDocOutput)


def generate_requirement_doc(state: GraphState) -> GraphState:
    """
    Generate Requirement Document for new_rfq emails
    
    Args:
        state: Current graph state with parsed_email
        
    Returns:
        Updated state with requirement_doc
    """
    parsed_email = state.get("parsed_email")
    
    if not parsed_email:
        return {
            **state,
            "content_error": "No parsed email available",
            "status": "error",
            "message": "Missing parsed email data"
        }
    
    try:
        agent = create_requirement_generator()
        
        # Build context from parsed email
        sender = parsed_email.get("sender", "Unknown")
        subject = parsed_email.get("subject", "No Subject")
        extracted_info = parsed_email.get("extracted_info", {})
        
        info_text = "\n".join([f"- {k}: {v}" for k, v in extracted_info.items()])
        
        prompt = f"""You are a Content Generator Agent specialized in creating Requirement Documents.

Based on the following parsed email information, generate a comprehensive Requirement Document.

Email Details:
- Sender: {sender}
- Subject: {subject}
- Extracted Information:
{info_text}

Instructions:
1. Generate a unique document ID (use format: REQ-YYYYMMDD-XXX)
2. Create a clear, descriptive title based on the subject
3. Write a comprehensive description of the requirements
4. Extract and list individual requirements as bullet points
5. Determine priority (High/Medium/Low) based on urgency indicators in the email
6. Generate full document content in markdown format

Return the structured requirement document."""

        result: RequirementDocOutput = agent.invoke(prompt)
        
        # Build requirement document
        requirement_doc: RequirementDocument = {
            "doc_id": result.doc_id,
            "title": result.title,
            "description": result.description,
            "requirements": result.requirements,
            "priority": result.priority,
            "generated_content": result.generated_content
        }
        
        return {
            **state,
            "requirement_doc": requirement_doc,
            "generated_content": result.generated_content,
            "content_error": None,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "content_error": f"Failed to generate requirement document: {str(e)}",
            "status": "error",
            "message": f"Content generation failed: {str(e)}"
        }


def generate_change_request_doc(state: GraphState) -> GraphState:
    """
    Generate Change Request Document for change_request emails
    
    Args:
        state: Current graph state with parsed_email
        
    Returns:
        Updated state with change_request_doc
    """
    parsed_email = state.get("parsed_email")
    
    if not parsed_email:
        return {
            **state,
            "content_error": "No parsed email available",
            "status": "error",
            "message": "Missing parsed email data"
        }
    
    try:
        agent = create_change_request_generator()
        
        # Build context from parsed email
        sender = parsed_email.get("sender", "Unknown")
        subject = parsed_email.get("subject", "No Subject")
        extracted_info = parsed_email.get("extracted_info", {})
        
        info_text = "\n".join([f"- {k}: {v}" for k, v in extracted_info.items()])
        
        prompt = f"""You are a Content Generator Agent specialized in creating Change Request Documents.

Based on the following parsed email information, generate a comprehensive Change Request Document.

Email Details:
- Sender: {sender}
- Subject: {subject}
- Extracted Information:
{info_text}

Instructions:
1. Generate a unique change request ID (use format: CR-YYYYMMDD-XXX)
2. Create a clear title for the change request
3. Write a detailed description of what needs to be changed
4. List specific changes as bullet points
5. List potential affected stories (you can use placeholder IDs if not specified)
6. Determine priority (High/Medium/Low) based on urgency indicators
7. Generate full document content in markdown format

Return the structured change request document."""

        result: ChangeRequestDocOutput = agent.invoke(prompt)
        
        # Build change request document
        change_request_doc: ChangeRequestDocument = {
            "cr_id": result.cr_id,
            "title": result.title,
            "description": result.description,
            "changes": result.changes,
            "affected_stories": result.affected_stories,
            "priority": result.priority,
            "generated_content": result.generated_content
        }
        
        return {
            **state,
            "change_request_doc": change_request_doc,
            "generated_content": result.generated_content,
            "content_error": None,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "content_error": f"Failed to generate change request document: {str(e)}",
            "status": "error",
            "message": f"Content generation failed: {str(e)}"
        }


def content_generator_node(state: GraphState) -> GraphState:
    """
    Main Content Generator Node
    
    Routes to appropriate generator based on email type
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with generated document
    """
    email_type = state.get("email_type")
    
    if email_type == EmailType.NEW_RFQ:
        return generate_requirement_doc(state)
    elif email_type == EmailType.CHANGE_REQUEST:
        return generate_change_request_doc(state)
    else:
        return {
            **state,
            "content_error": f"Unknown email type: {email_type}",
            "status": "error",
            "message": f"Cannot generate content for unknown email type: {email_type}"
        }


# For testing purposes
if __name__ == "__main__":
    from graph.state import EmailType, ParsedEmail
    
    test_state: GraphState = {
        "raw_email": "Test email",
        "email_subject": "New Feature Request",
        "email_sender": "test@example.com",
        "email_type": EmailType.NEW_RFQ,
        "parsed_email": {
            "email_type": EmailType.NEW_RFQ,
            "sender": "test@example.com",
            "subject": "New Feature Request",
            "raw_content": "Test email",
            "extracted_info": {"project": "Test Project", "features": "New module"}
        }
    }
    
    result = content_generator_node(test_state)
    print("Generated Content:", result.get("generated_content")[:200] if result.get("generated_content") else "None")

