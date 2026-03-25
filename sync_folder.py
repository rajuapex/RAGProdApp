import os
from pathlib import Path
import inngest
from dotenv import load_dotenv

load_dotenv()

# THE FIX: We set the environment variable BEFORE initializing the client.
# We use 127.0.0.1 instead of 'localhost' to bypass macOS DNS lag.
os.environ["INNGEST_BASE_URL"] = "http://127.0.0.1:8288"

# Initialize client
client = inngest.Inngest(app_id="rag_prod_app")

def sync_all_pdfs():
    pdf_dir = Path("./pdfs")
    
    # Check if directory exists to avoid silent failure
    if not pdf_dir.exists():
        print(f"❌ Error: Directory {pdf_dir.resolve()} does not exist.")
        return

    files = list(pdf_dir.glob("*.pdf"))
    if not files:
        print("No PDFs found in ./pdfs")
        return

    print(f"Connecting to Inngest at: {os.environ['INNGEST_BASE_URL']}")

    for f in files:
        print(f"Syncing: {f.name}...")
        try:
            # We use send_sync to dispatch the event
            client.send_sync(
                inngest.Event(
                    name="rag/ingest_pdf",
                    data={
                        "pdf_path": str(f.resolve()),
                        "source_id": f.name
                    }
                )
            )
            print(f"  ✅ Queued successfully.")
        except Exception as e:
            print(f"  ❌ Dispatch Failed: {e}")

if __name__ == "__main__":
    sync_all_pdfs()