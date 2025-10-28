# backend/main.py
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from rag_pipeline import RAGPipeline

# ----------------- SETTINGS -----------------
PDF_PATH = "D:\Shana\shana1\data\Introduction to Machine Learning with Python ( PDFDrive.com )-min.pdf"  # 👈 Put your PDF file here
DATA_DIR = Path("D:\Shana\shana1\data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ----------------- APP SETUP -----------------
app = FastAPI(title="RAG Tutor Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

rag = RAGPipeline(persist_dir=str(DATA_DIR / "chroma_db"))

# ----------------- AUTO-LOAD PDF -----------------
if Path(PDF_PATH).exists():
    print(f"📘 Loading PDF: {PDF_PATH}")
    try:
        chunks = rag.ingest_pdf(PDF_PATH)
        print(f"✅ Loaded and indexed {chunks} chunks.")
    except Exception as e:
        print(f"⚠️ Failed to load {PDF_PATH}: {e}")
else:
    print(f"⚠️ PDF not found at {PDF_PATH}. Please check the path.")

# ----------------- CHAT ENDPOINT -----------------
@app.post("/chat")
async def chat(message: str = Form(...)):
    answer = rag.ask(message)
    return {"answer": answer}
