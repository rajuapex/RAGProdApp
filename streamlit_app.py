import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests
import time
from pathlib import Path

load_dotenv()

# UI Setup: Simplified for a clean chatbot look
st.set_page_config(page_title="Master Knowledge Bot", page_icon="🤖", layout="centered")

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        # Note: Some versions of Inngest Dev Server return 'data' as a list
        return resp.json().get("data", [])
    except Exception:
        return []

def wait_for_run_output(event_id: str, timeout_s: float = 60.0):
    start = time.time()
    while time.time() - start < timeout_s:
        runs = fetch_runs(event_id)
        if not runs:
            time.sleep(1)
            continue
            
        run = runs[0]
        status = run.get("status")
        
        # Inngest Dev Server usually uses "Completed" or "Succeeded"
        if status in ("Completed", "Succeeded"):
            return run.get("output") or {}
        if status in ("Failed", "Cancelled"):
            error_msg = run.get("error", "Unknown error")
            raise RuntimeError(f"Inngest Function failed: {status} - {error_msg}")
            
        time.sleep(1)
    raise TimeoutError("Timeout: Is your FastAPI server (Tab 2) and Inngest Dev (Tab 3) running?")

# --- MAIN UI ---
st.title("🤖 Master Knowledge Chatbot")
st.markdown("Ask anything about the company's master PDF records.")

# Initialize chat history for a true "Chatbot" feel
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Trigger the Inngest query event
                client = get_inngest_client()
                ids = client.send_sync(
                    inngest.Event(
                        name="rag/query_pdf_ai",
                        data={
                            "question": prompt,
                            "top_k": 5, # You can hardcode this or make it a sidebar setting
                        },
                    )
                )
                
                # Wait for the background result
                output = wait_for_run_output(ids[0])
                answer = output.get("answer", "I couldn't find an answer in the records.")
                
                # Display Answer
                st.markdown(answer)
                
                # Show Sources if available
                if output.get("sources"):
                    with st.expander("View Sources"):
                        st.caption(f"Sources: {', '.join(output['sources'])}")
                
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")