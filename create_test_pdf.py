from fpdf import FPDF

def create_sample_pdf(filename="./pdfs/apex_project_charter.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(200, 10, txt="Apex Develop: Project Charter 2026", ln=True, align='C')
    pdf.ln(10)
    
    # Body Content
    pdf.set_font("Arial", size=12)
    content = [
        "Project Name: Apex RAG Engine",
        "Lead Developer: Raju Krish",
        "Tech Stack: FastAPI, Inngest, Qdrant, OpenAI",
        "",
        "Project Goal:",
        "The goal of this project is to build a production-grade Retrieval-Augmented ",
        "Generation (RAG) system that allows users to query internal PDF documents ",
        "using semantic search. It uses a 3072-dimension vector space.",
        "",
        "Security Protocol:",
        "The system uses 'Secret Code 99' for all encrypted data transfers between ",
        "the FastAPI gateway and the Qdrant Docker container.",
        "",
        "Infrastructure:",
        "The database is hosted locally on port 6333 and uses Cosine Distance for ",
        "calculating vector similarity."
    ]
    
    for line in content:
        pdf.cell(200, 10, txt=line, ln=True)
    
    pdf.output(filename)
    print(f"✅ Success! Created {filename}")

if __name__ == "__main__":
    import os
    if not os.path.exists("./pdfs"):
        os.makedirs("./pdfs")
    create_sample_pdf()