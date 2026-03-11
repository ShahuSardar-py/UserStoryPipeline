"""
Main Entry Point - Email Parser to User Story Generator

This is the main application file that runs the LangGraph workflow.
"""

import sys
from graph.graph import run_workflow, get_workflow
from graph.state import GraphState
import config


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("  Email Parser to User Story Generator")
    print("  LangGraph Multi-Agent System")
    print("=" * 60)
    print()


def print_result(result: GraphState):
    """Print the workflow result in a formatted way"""
    print("\n" + "=" * 60)
    print("WORKFLOW RESULT")
    print("=" * 60)
    
    print(f"\nStatus: {result.get('status', 'unknown')}")
    print(f"Message: {result.get('message', 'No message')}")
    
    if result.get('email_type'):
        print(f"\nEmail Type: {result.get('email_type')}")
    
    if result.get('generated_stories'):
        print(f"\nGenerated {len(result.get('generated_stories', []))} User Stories:")
        for story in result.get('generated_stories', []):
            print(f"  - {story.get('story_id')}: {story.get('title')}")
    
    if result.get('existing_stories'):
        print(f"\nFound {len(result.get('existing_stories', []))} Existing Stories:")
        for story in result.get('existing_stories', []):
            print(f"  - {story.get('story_id')}: {story.get('title')}")
    
    print("\n" + "=" * 60)


def interactive_mode():
    """Run in interactive mode"""
    print_banner()
    print("Enter your email content (press Ctrl+D or Ctrl+Z on a new line to finish):")
    print("-" * 60)
    
    # Read multi-line input
    email_lines = []
    while True:
        try:
            line = input()
            email_lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nExiting...")
            sys.exit(0)
    
    email_content = "\n".join(email_lines)
    
    if not email_content.strip():
        print("Error: No email content provided")
        return
    
    # Get optional subject and sender
    subject = input("\nEmail Subject (optional): ").strip()
    sender = input("Email Sender (optional): ").strip()
    
    print("\nProcessing email...")
    result = run_workflow(email_content, subject, sender)
    print_result(result)


def demo_mode():
    """Run with demo email"""
    print_banner()
    print("Running in DEMO mode with sample email...\n")
    
    demo_email = """
    Hello,
    
    I would like to request a new feature for our inventory management system.
    We need to add a supplier management module with the following requirements:
    
    1. Add new suppliers with contact information (name, email, phone, address)
    2. Edit existing supplier information
    3. View supplier list with search and filter functionality
    4. Delete suppliers (soft delete)
    5. Track supplier performance ratings
    6. Export supplier data to CSV
    
    Please provide a quote for this development.
    
    Best regards,
    John from ABC Corp
    """
    
    result = run_workflow(
        email_content=demo_email,
        subject="New Feature Request - Supplier Management Module",
        sender="john@abccorp.com"
    )
    
    print_result(result)
    
    # Print generated content if available
    if result.get('generated_content'):
        print("\nGenerated Document Content:")
        print("-" * 60)
        print(result.get('generated_content')[:500])
        print("...")


def main():
    """Main entry point"""
    # Validate configuration
    if not config.validate_config():
        sys.exit(1)
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--demo", "-d"):
            demo_mode()
        elif sys.argv[1] in ("--help", "-h"):
            print("Usage: python main.py [OPTIONS]")
            print()
            print("Options:")
            print("  -d, --demo        Run with demo email")
            print("  -s, --streamlit   Launch Streamlit UI")
            print("  -h, --help        Show this help message")
            print()
            print("Without options, runs in interactive mode")
        elif sys.argv[1] in ("--streamlit", "-s"):
            # delegate to streamlit runtime
            try:
                import streamlit.web.cli as stcli  # type: ignore
            except ImportError:
                print("Streamlit is not installed. Please install with `pip install streamlit`.")
                sys.exit(1)

            # re-run the script under streamlit
            sys.argv = ["streamlit", "run", "streamlit_app.py"]
            sys.exit(stcli.main())
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        interactive_mode()


if __name__ == "__main__":
    main()

