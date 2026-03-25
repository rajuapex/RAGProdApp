from fpdf import FPDF
import os

def generate_pdf(filename, title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Title
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    
    # Body
    pdf.set_font("Arial", size=12)
    for line in content:
        pdf.cell(200, 10, txt=line, ln=True)
    
    pdf.output(f"./pdfs/{filename}")
    print(f"✅ Created: {filename}")

if __name__ == "__main__":
    if not os.path.exists("./pdfs"):
        os.makedirs("./pdfs")

    # 1. LLM Engineering PDF
    generate_pdf(
        "llm_engineering_specs.pdf",
        "LLM Engineering Standards 2026",
        [
            "Standard Model: GPT-4o-mini",
            "Context Window: 128,000 tokens",
            "Temperature Setting: 0.1 for high-factuality tasks.",
            "",
            "Optimization Protocol:",
            "All prompts must include a 'System Role' definition.",
            "Token usage is monitored via the 'Apex Dashboard'.",
            "The maximum output limit is set to 4096 tokens."
        ]
    )

    # 2. AI Chatbot PDF
    generate_pdf(
        "chatbot_architecture.pdf",
        "Conversational AI: Architecture Overview",
        [
            "Persona: Technical Senior Architect",
            "State Management: Handled via Streamlit Session State.",
            "Latency Target: Under 1.5 seconds per response.",
            "",
            "User Interaction Rules:",
            "1. Do not answer questions outside the provided context.",
            "2. Always cite the document source at the end of the response.",
            "3. Use a polite but professional tone."
        ]
    )

    # 3. RAG PDF
    generate_pdf(
        "rag_strategy_master.pdf",
        "Retrieval-Augmented Generation (RAG) Strategy",
        [
            "Embedding Model: text-embedding-3-large",
            "Vector Dimensions: 3072",
            "Similarity Metric: Cosine Similarity",
            "",
            "Retrieval Logic:",
            "The system uses Top-K retrieval with K=5.",
            "Chunk Size: 1000 characters with 200 character overlap.",
            "The 'Master Records' collection in Qdrant is the primary source.",
            "Security: Uses Secret Code 99 for local API authentication."
        ]
    )