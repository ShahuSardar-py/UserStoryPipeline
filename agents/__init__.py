"""
Agents package - LLM agents for the workflow
"""

from agents.emailparser import parse_email, create_email_parser_agent, EmailParserOutput
from agents.contentgen import (
    content_generator_node, 
    generate_requirement_doc, 
    generate_change_request_doc,
    RequirementDocOutput,
    ChangeRequestDocOutput
)
from agents.user_story_gen import (
    user_story_generator_node,
    generate_user_stories_from_requirement,
    generate_user_stories_from_change_request,
    UserStoriesOutput
)

__all__ = [
    "parse_email",
    "create_email_parser_agent",
    "EmailParserOutput",
    "content_generator_node",
    "generate_requirement_doc",
    "generate_change_request_doc",
    "RequirementDocOutput",
    "ChangeRequestDocOutput",
    "user_story_generator_node",
    "generate_user_stories_from_requirement",
    "generate_user_stories_from_change_request",
    "UserStoriesOutput"
]

