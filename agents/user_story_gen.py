"""
User Story Generator Agent - Node 3 of the LangGraph workflow

This agent generates user stories from:
- Requirement Document (for new_rfq)
- Change Request Document + new_requirements (for change_request)
"""

from typing import List
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from graph.state import GraphState, UserStory, EmailType
import config


# Define structured output schema
class UserStoriesOutput(BaseModel):
    """Structured output for User Story Generator"""
    stories: List[UserStory] = Field(description="List of generated user stories")


def create_user_story_generator() -> ChatMistralAI:
    """Create LLM for user story generation"""
    llm = ChatMistralAI(
        model=config.MISTRAL_MODEL,
        api_key=config.MISTRAL_API_KEY,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    return llm.with_structured_output(UserStoriesOutput)


def generate_user_stories_from_requirement(state: GraphState) -> GraphState:
    """
    Generate user stories from Requirement Document
    
    Args:
        state: Current graph state with requirement_doc
        
    Returns:
        Updated state with generated_stories
    """
    requirement_doc = state.get("requirement_doc")
    
    if not requirement_doc:
        return {
            **state,
            "stories_error": "No requirement document available",
            "status": "error",
            "message": "Missing requirement document"
        }
    
    try:
        agent = create_user_story_generator()
        
        # Build context from requirement document
        doc_id = requirement_doc.get("doc_id", "Unknown")
        title = requirement_doc.get("title", "No Title")
        description = requirement_doc.get("description", "")
        requirements = requirement_doc.get("requirements", [])
        priority = requirement_doc.get("priority", "Medium")
        
        req_text = "\n".join([f"{i+1}. {req}" for i, req in enumerate(requirements)])
        
        prompt = f"""You are a User Story Generator Agent specialized in creating user stories from requirements.

Based on the following Requirement Document, generate user stories in a format ready for implementation.

Requirement Document:
- ID: {doc_id}
- Title: {title}
- Description: {description}
- Requirements:
{req_text}
- Priority: {priority}

Instructions:
1. Generate user stories following the format: "As a [user], I want to [action], so that [benefit]"
2. Each story should have:
   - Unique story ID (format: STORY-XXX)
   - Clear title
   - Detailed description
   - Acceptance criteria (list of conditions for completion)
   - Priority (from the document or derived)
   - Status: "To Do"
3. Break down requirements into manageable stories
4. Include acceptance criteria for each story
5. Link to the requirement document ID

Return a list of user stories."""

        result: UserStoriesOutput = agent.invoke(prompt)
        
        return {
            **state,
            "generated_stories": result.stories,
            "stories_error": None,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "stories_error": f"Failed to generate user stories: {str(e)}",
            "status": "error",
            "message": f"User story generation failed: {str(e)}"
        }


def generate_user_stories_from_change_request(state: GraphState) -> GraphState:
    """
    Generate user stories from Change Request Document
    
    Uses new_requirements (filtered by backlog checker) to generate only NEW stories
    
    Args:
        state: Current graph state with change_request_doc, existing_stories, new_requirements
        
    Returns:
        Updated state with generated_stories
    """
    change_request_doc = state.get("change_request_doc")
    existing_stories = state.get("existing_stories", [])
    new_requirements = state.get("new_requirements", [])
    
    if not change_request_doc:
        return {
            **state,
            "stories_error": "No change request document available",
            "status": "error",
            "message": "Missing change request document"
        }
    
    # If no new requirements, return existing stories info
    if not new_requirements:
        return {
            **state,
            "generated_stories": [],
            "stories_error": None,
            "status": "success",
            "message": "All requirements already exist in backlog"
        }
    
    try:
        agent = create_user_story_generator()
        
        # Build context from change request - use NEW requirements only
        cr_id = change_request_doc.get("cr_id", "Unknown")
        cr_title = change_request_doc.get("title", "No Title")
        cr_description = change_request_doc.get("description", "")
        priority = change_request_doc.get("priority", "Medium")
        
        # Use new_requirements (filtered by backlog checker) instead of all changes
        changes = new_requirements
        changes_text = "\n".join([f"{i+1}. {change}" for i, change in enumerate(changes)])
        
        if existing_stories:
            existing_text = "\n".join([f"- {s.get('story_id', 'Unknown')}: {s.get('title', 'No Title')}" 
                                        for s in existing_stories])
        else:
            existing_text = "No existing stories found"
        
        prompt = f"""You are a User Story Generator Agent specialized in creating user stories for change requests.

Based on the following NEW Change Request Requirements (only new requirements not in backlog), generate user stories.

Note: The following requirements ALREADY exist and should NOT be included:
{existing_text}

NEW Change Request Requirements to implement:
{changes_text}

Change Request:
- ID: {cr_id}
- Title: {cr_title}
- Description: {cr_description}
- Priority: {priority}

Instructions:
1. Generate ONLY for the NEW requirements listed above
2. Each story should have:
   - Unique story ID (format: CR-STORY-XXX for change request stories)
   - Clear title reflecting the change
   - Detailed description of what changed
   - Acceptance criteria for the change
   - Priority (from the document)
   - Status: "To Do"
   - Link to the change request ID
3. Do NOT generate stories for requirements that already exist

Return a list of user stories for the NEW requirements only."""

        result: UserStoriesOutput = agent.invoke(prompt)
        
        return {
            **state,
            "generated_stories": result.stories,
            "stories_error": None,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "stories_error": f"Failed to generate user stories from change request: {str(e)}",
            "status": "error",
            "message": f"User story generation failed: {str(e)}"
        }


def user_story_generator_node(state: GraphState) -> GraphState:
    """
    Main User Story Generator Node
    
    Routes to appropriate generator based on email type
    
    Args:
        state: Current graph state
        
    Returns:
        Updated state with generated_stories
    """
    email_type = state.get("email_type")
    
    if email_type == EmailType.NEW_RFQ:
        return generate_user_stories_from_requirement(state)
    elif email_type == EmailType.CHANGE_REQUEST:
        return generate_user_stories_from_change_request(state)
    else:
        return {
            **state,
            "stories_error": f"Unknown email type: {email_type}",
            "status": "error",
            "message": f"Cannot generate stories for unknown email type: {email_type}"
        }


# For testing purposes
if __name__ == "__main__":
    from graph.state import EmailType, RequirementDocument
    
    test_state: GraphState = {
        "email_type": EmailType.NEW_RFQ,
        "requirement_doc": {
            "doc_id": "REQ-20240101-001",
            "title": "Supplier Management Module",
            "description": "Create a supplier management module for inventory system",
            "requirements": ["Add new suppliers", "Edit supplier info", "View supplier list", "Delete suppliers"],
            "priority": "High",
            "generated_content": "# Supplier Management Module\n\nRequirements..."
        }
    }
    
    result = user_story_generator_node(test_state)
    print("Generated Stories:", len(result.get("generated_stories", [])))
    for story in result.get("generated_stories", []):
        print(f"- {story.get('story_id')}: {story.get('title')}")

