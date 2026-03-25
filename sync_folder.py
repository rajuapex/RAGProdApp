import os
from pathlib import Path
import inngest

# Connect to your local Inngest
client = inngest.Inngest(app_id="rag_app")

def sync_all_pdfs(folder_path="./pdfs"):
    files = list(Path(folder_path).glob("*.pdf"))
    for file_path in files:
        print(f"Syncing: {file_path.name}")
        client.send_sync(
            inngest.Event(
                name="rag/ingest_pdf",
                data={
                    "pdf_path": str(file_path.resolve()),
                    "source_id": file_path.name,
                },
            )
        )
    print(f"Done! Triggered {len(files)} files.")

if __name__ == "__main__":
    sync_all_pdfs()