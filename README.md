# Email Parser to User Story Generator

This project uses LangGraph agents to parse feature request emails and generate user stories. It supports a command-line interface and a Streamlit-based web UI.

## Setup

1. Create a virtual environment and install requirements:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your Mistral API key:
   ```ini
   MISTRAL_API_KEY=your-api-key-here
   ```

## Usage

### Command line

- Interactive mode (default):
  ```bash
  python main.py
  ```
- Demo email:
  ```bash
  python main.py --demo
  ```
- Streamlit UI:
  ```bash
  python main.py --streamlit
  # or
  streamlit run streamlit_app.py
  ```

### Streamlit Web Interface

After launching the Streamlit app (`python main.py --streamlit` or `streamlit run streamlit_app.py`), open the browser at `http://localhost:8501`.

- Paste or type your email content.
- Optionally provide subject and sender.
- Click **Process Email** to run the workflow.
- Results, generated stories, and any messages will be shown on the page.


## Project Structure

(unchanged; see workspace tree)
