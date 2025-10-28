import sys
import requests
import threading
import pyttsx3
import speech_recognition as sr
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel,
    QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, pyqtSignal, QObject

BACKEND_URL = "http://localhost:8000"


class TutorUI(QWidget):
    # define signals that the worker threads can emit
    append_text_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎓 AI Tutor - RAG Chatbot")
        self.setGeometry(200, 100, 850, 700)

        self.engine = pyttsx3.init()
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

        self.init_ui()

        # connect signal to UI slot
        self.append_text_signal.connect(self.safe_append_text)

    # ------------------- UI Layout -------------------
    def init_ui(self):
        layout = QVBoxLayout()

        # Mascot avatar
        self.mascot_label = QLabel()
        self.mascot_movie = QMovie("ui/assets/neutral.gif")
        self.mascot_label.setMovie(self.mascot_movie)
        self.mascot_movie.start()
        layout.addWidget(self.mascot_label, alignment=Qt.AlignCenter)

        # Chat display
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        layout.addWidget(self.chat_area)

        # Input field
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("💬 Type your question here...")
        input_layout.addWidget(self.input_box)

        self.send_btn = QPushButton("📨 Send")
        self.send_btn.clicked.connect(self.ask_text_query)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        # Action buttons
        btn_layout = QHBoxLayout()

        self.listen_btn = QPushButton("🎤 Speak Question")
        self.listen_btn.clicked.connect(self.toggle_listening)
        btn_layout.addWidget(self.listen_btn)

        self.stop_btn = QPushButton("🛑 Stop Speech")
        self.stop_btn.clicked.connect(lambda: self.engine.stop())
        btn_layout.addWidget(self.stop_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # ------------------- Thread-safe append -------------------
    def safe_append_text(self, text):
        """Executed in main thread via signal"""
        self.chat_area.append(text)

    # ------------------- Text Query -------------------
    def ask_text_query(self):
        text = self.input_box.text().strip()
        if not text:
            return
        self.append_text_signal.emit(f"\n🧑 You: {text}")
        self.input_box.clear()
        self.set_emotion("thinking")
        threading.Thread(target=self._fetch_answer, args=(text,)).start()

    def _fetch_answer(self, text):
        try:
            res = requests.post(f"{BACKEND_URL}/chat", data={"message": text})
            ans = res.json().get("answer", "No response.")
            self.append_text_signal.emit(f"\n🤖 Tutor: {ans}")
            self.set_emotion("happy")
            self.speak(ans)
        except Exception as e:
            self.append_text_signal.emit(f"\n⚠️ Error: {e}")
            self.set_emotion("confused")

    # ------------------- Speak/Listen Toggle -------------------
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_btn.setText("🎧 Listening... (Click to stop)")
            self.set_emotion("thinking")
            threading.Thread(target=self.listen_question).start()
        else:
            self.is_listening = False
            self.listen_btn.setText("🎤 Speak Question")
            self.set_emotion("neutral")
            self.append_text_signal.emit("\n🛑 Listening stopped by user.")

    def listen_question(self):
        try:
            with self.mic as source:
                self.append_text_signal.emit("\n🎤 Listening... please speak now.")
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source, timeout=8, phrase_time_limit=8)
            if not self.is_listening:
                return
            self.listen_btn.setText("🎤 Speak Question")
            self.is_listening = False
            text = self.recognizer.recognize_google(audio)
            self.append_text_signal.emit(f"\n🧑 You said: {text}")
            self.set_emotion("thinking")
            threading.Thread(target=self._fetch_answer, args=(text,)).start()
        except sr.WaitTimeoutError:
            self.append_text_signal.emit("\n⌛ Listening timed out (no speech detected).")
        except sr.UnknownValueError:
            self.append_text_signal.emit("\n❌ Could not understand speech.")
            self.set_emotion("confused")
        except Exception as e:
            self.append_text_signal.emit(f"\n⚠️ Speech recognition error: {e}")
            self.set_emotion("neutral")
        finally:
            self.listen_btn.setText("🎤 Speak Question")
            self.is_listening = False

    # ------------------- Text-to-Speech -------------------
    def speak(self, text):
        threading.Thread(target=lambda: self._tts(text)).start()

    def _tts(self, text):
        self.engine.stop()
        self.engine.say(text)
        self.engine.runAndWait()

    # ------------------- Mascot Emotions -------------------
    def set_emotion(self, emotion):
        gif_map = {
            "happy": "shana1/assets/explaining.gif",
            "thinking": "Shana1/assets/thinking.gif",
            "neutral": "Shana1/assets/neutral.gif",
            "confused": "Shana1/assets/confused.gif"
        }
        gif_path = gif_map.get(emotion, "Shana1/assets/neutral.gif")
        self.mascot_movie.stop()
        self.mascot_movie = QMovie(gif_path)
        self.mascot_label.setMovie(self.mascot_movie)
        self.mascot_movie.start()

    def closeEvent(self, event):
        self.engine.stop()
        event.accept()


# ------------------- Run -------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TutorUI()
    window.show()
    sys.exit(app.exec_())
