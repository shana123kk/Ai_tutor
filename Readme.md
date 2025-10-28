🎓 AI Tutor (RAG-Powered Chatbot)

A desktop-based AI Tutor that can read PDFs, answer questions, and talk to you — powered by LangChain, ChromaDB, and Flan-T5 Small.

🚀 Features
📘 Reads and understands your PDF study materials
💬 Ask questions via text or speech
🔊 Speaks the answers aloud
😊 Animated mascot shows emotions (happy, thinking, confused, neutral)
🖥️ Works fully offline (PyQt5 desktop app)

⚙️ Setup

1️⃣ Install backend requirements
cd backend
pip install -r requirements.txt

2️⃣ Install UI requirements
cd ../ui
pip install -r requirements.txt

📘 Add Your PDF
Place your study material in:
backend/data/
Then open backend/main.py and set:
PDF_PATH = "backend/data/my_study_material.pdf"

▶️ Run the App
Start the backend
cd backend
uvicorn main:app --reload
Start the UI
cd ../ui
python tutor_ui.py

🧠 How to Use

💬 Type your question and click Send
🎤 Click Speak Question to ask by voice
🛑 Click Stop Speech to stop TTS
🤖 Tutor replies with both text and voice

🧩 Tech Used

LangChain + ChromaDB
google/flan-t5-small
Sentence Transformers (MiniLM-L6-v2)
FastAPI
PyQt5
pyttsx3 + SpeechRecognition