import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests
import time
from pathlib import Path

load_dotenv()

# UI Setup
st.set_page_config(page_title="Master Knowledge Bot", page_icon="🤖", layout="centered")

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    # FIXED: Changed from 'rag_app' to 'rag_prod_app' to match backend
    return inngest.Inngest(app_id="rag_prod_app", is_production=False)

def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")

def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
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
        
        # Inngest Dev Server status check
        if status in ("Completed", "Succeeded"):
            return run.get("output") or {}
        if status in ("Failed", "Cancelled"):
            error_msg = run.get("error", "Unknown error")
            raise RuntimeError(f"Inngest Function failed: {status} - {error_msg}")
            
        time.sleep(1)
    raise TimeoutError("Timeout: Is your FastAPI server (Tab 1) and Inngest Dev (Tab 2) running?")

# --- MAIN UI ---
st.title("🤖 Master Knowledge Chatbot")
st.markdown("Ask anything about the company's master PDF records.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                client = get_inngest_client()
                # Sending event to 'rag_prod_app'
                ids = client.send_sync(
                    inngest.Event(
                        name="rag/query_pdf_ai",
                        data={
                            "question": prompt,
                            "top_k": 5, 
                        },
                    )
                )
                
                # Wait for the background result from Qdrant/OpenAI
                output = wait_for_run_output(ids[0])
                answer = output.get("answer", "I couldn't find an answer in the records.")
                
                # Display Answer
                st.markdown(answer)
                
                # Show Sources
                if output.get("sources"):
                    with st.expander("View Sources"):
                        st.caption(f"Sources: {', '.join(output['sources'])}")
                
                # Save assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")