"""
Email Parser Agent - Node 1 of the LangGraph workflow

This agent parses incoming emails to identify if they are:
- New RFQ (Request for Quotation)
- Change Request
- Unknown type
"""

from typing import Union
from pydantic import BaseModel, Field
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage
from graph.state import GraphState, EmailType, ParsedEmail
import config


# Define structured output schema
class EmailParserOutput(BaseModel):
    """Structured output for Email Parser Agent"""
    email_type: EmailType = Field(
        description="Type of email: 'new_rfq' for new requests, 'change_request' for changes to existing"
    )
    sender: str = Field(description="Email sender address or name")
    subject: str = Field(description="Email subject line")
    extracted_info: dict = Field(
        description="Key information extracted from email (project name, dates, requirements, etc.)"
    )
    confidence: float = Field(
        description="Confidence score from 0-1 for the classification"
    )


def create_email_parser_agent() -> ChatMistralAI:
    """Create and return the Email Parser LLM agent with structured output"""
    llm = ChatMistralAI(
        model=config.MISTRAL_MODEL,
        api_key=config.MISTRAL_API_KEY,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    
    # Bind with structured output
    return llm.with_structured_output(EmailParserOutput)


def parse_email(state: GraphState) -> GraphState:
    """
    Email Parser Agent Node
    
    Parses the raw email and extracts:
    - Email type (new_rfq or change_request)
    - Sender information
    - Subject
    - Extracted requirements/info
    
    Args:
        state: Current graph state with raw_email
        
    Returns:
        Updated state with parsed information
    """
    raw_email = state.get("raw_email", "")
    email_subject = state.get("email_subject", "")
    email_sender = state.get("email_sender", "")
    
    if not raw_email:
        return {
            **state,
            "parsing_error": "No email content provided",
            "status": "error",
            "message": "Missing email content"
        }
    
    try:
        # Create the agent
        agent = create_email_parser_agent()
        
        # Create prompt for the agent
        prompt = f"""You are an Email Parser Agent specialized in analyzing requests for software development projects.

Your task is to classify the incoming email and extract relevant information.

Email Subject: {email_subject}
Email Sender: {email_sender}

Email Content:
{raw_email}

Instructions:
1. Classify the email as either:
   - "new_rfq" - if it's a new request for quotation or new project requirements
   - "change_request" - if it's requesting changes to existing stories/features
   
2. Extract key information such as:
   - Project name
   - Requirements/features requested
   - Priority or urgency
   - Deadlines or timelines
   - Any specific technical requirements
   
3. Provide your confidence level for the classification

Return the structured output with all extracted information."""

        # Invoke the agent
        result: EmailParserOutput = agent.invoke(prompt)
        
        # Build parsed email structure
        parsed_email: ParsedEmail = {
            "email_type": result.email_type,
            "sender": result.sender,
            "subject": result.subject,
            "raw_content": raw_email,
            "extracted_info": result.extracted_info
        }
        
        return {
            **state,
            "email_type": result.email_type,
            "parsed_email": parsed_email,
            "parsing_error": None,
            "status": "processing"
        }
        
    except Exception as e:
        return {
            **state,
            "parsing_error": f"Failed to parse email: {str(e)}",
            "status": "error",
            "message": f"Email parsing failed: {str(e)}"
        }


# For testing purposes
if __name__ == "__main__":
    test_state: GraphState = {
        "raw_email": "Hello, I would like to request a new feature for our inventory management system. We need to add a supplier management module with the following requirements:\n\n1. Add new suppliers\n2. Edit existing supplier information\n3. View supplier list\n4. Delete suppliers\n\nPlease provide a quote for this development.\n\nBest regards,\nJohn from ABC Corp",
        "email_subject": "New Feature Request - Supplier Management",
        "email_sender": "john@abccorp.com"
    }
    
    result = parse_email(test_state)
    print("Email Type:", result.get("email_type"))
    print("Parsed Email:", result.get("parsed_email"))

