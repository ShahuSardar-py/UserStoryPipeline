import streamlit as st
from graph.graph import run_workflow
import config

# Page configuration
st.set_page_config(page_title="Email to User Story Generator", layout="wide")
st.title("📩 Email to User Story Generator")
st.write("Use this interface to paste an email and have the system parse and create user stories.")

# Validate configuration first
if not config.validate_config():
    st.error("Configuration invalid. Please set `MISTRAL_API_KEY` in .env and restart the app.")
    st.stop()

# A sample/demo email that can be loaded with a button
_DEMO_EMAIL = """
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

# Sidebar controls
with st.sidebar:
    st.header("Options")
    use_demo = st.button("Load demo email")
    clear = st.button("Clear fields")

# Email input area
if use_demo:
    email_content = st.text_area("Email Content", value=_DEMO_EMAIL, height=250)
else:
    email_content = st.text_area("Email Content", height=250)

subject_input = st.text_input("Subject (optional)")
sender_input = st.text_input("Sender (optional)")

if clear:
    # reset page by rerunning
    st.experimental_rerun()

# Run button
if st.button("Process Email"):
    if not email_content.strip():
        st.warning("Please enter some email content before processing.")
    else:
        with st.spinner("Running workflow..."):
            result = run_workflow(email_content, subject_input, sender_input)

        st.success("Workflow completed")
        st.subheader("Result")
        st.json(result)

        # Optional detailed sections
        if result.get("generated_stories"):
            st.subheader("Generated User Stories")
            for story in result.get("generated_stories", []):
                st.write(f"- **{story.get('story_id')}**: {story.get('title')}")

        if result.get("existing_stories"):
            st.subheader("Existing Stories (duplicates)")
            for story in result.get("existing_stories", []):
                st.write(f"- **{story.get('story_id')}**: {story.get('title')}")

        if result.get("generated_content"):
            st.subheader("Generated Content Preview")
            st.code(result.get("generated_content"), language="text")

        if result.get("message"):
            st.info(f"Message: {result.get('message')}")
