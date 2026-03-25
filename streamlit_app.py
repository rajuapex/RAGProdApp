import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests
import time
from pathlib import Path

load_dotenv()

st.set_page_config(page_title="RAG Ingest PDF", page_icon="📄", layout="centered")

@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    # Use the standard Inngest client
    return inngest.Inngest(app_id="rag_app", is_production=False)

def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path

# CHANGED: Removed 'async' and used 'send_sync'
def send_rag_ingest_event(pdf_path: Path) -> None:
    client = get_inngest_client()
    client.send_sync(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )

st.title("Upload a PDF to Ingest")
uploaded = st.file_uploader("Choose a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded is not None:
    with st.spinner("Uploading and triggering ingestion..."):
        path = save_uploaded_pdf(uploaded)
        # CHANGED: No more asyncio.run()
        send_rag_ingest_event(path)
        time.sleep(0.3)
    st.success(f"Triggered ingestion for: {path.name}")

st.divider()
st.title("Ask a question about your PDFs")

# CHANGED: Removed 'async' and used 'send_sync'
def send_rag_query_event(question: str, top_k: int) -> str:
    client = get_inngest_client()
    # .send_sync returns a list of event IDs
    ids = client.send_sync(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={
                "question": question,
                "top_k": top_k,
            },
        )
    )
    return ids[0]

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
        
        if status in ("Completed", "Succeeded"):
            return run.get("output") or {}
        if status in ("Failed", "Cancelled"):
            raise RuntimeError(f"Inngest Function failed: {status}")
            
        time.sleep(1)
    raise TimeoutError("Check if your FastAPI server is running and synced.")

with st.form("rag_query_form"):
    question = st.text_input("Your question")
    top_k = st.number_input("Chunks", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Ask")

    if submitted and question.strip():
        with st.spinner("Generating answer..."):
            # CHANGED: Direct call, no asyncio.run()
            event_id = send_rag_query_event(question.strip(), int(top_k))
            output = wait_for_run_output(event_id)
            
            st.subheader("Answer")
            st.write(output.get("answer", "No answer found."))
            if output.get("sources"):
                st.caption(f"Sources: {', '.join(output['sources'])}")