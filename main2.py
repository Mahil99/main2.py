import tkinter as tk
import threading
from datetime import datetime
from chatbot import GeminiChat  

from gtts import gTTS
from playsound import playsound
import speech_recognition as sr
import os

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("temp_response.mp3")
        playsound("temp_response.mp3")
        os.remove("temp_response.mp3")
    except Exception as e:
        print(f"Voice output error: {e}")

def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand that."
    except sr.RequestError:
        return "Speech recognition service is unavailable."

class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatbot Project")
        self.root.geometry("400x600")
        self.root.configure(bg="#1e1e1e")

        self.chat = GeminiChat("AIzaSyBjrTaTQpDALRS8EaLJwFGw76Z6MH01wkM") 
        self.typing = False
        self.typing_dots = 0

        self.build_ui()

    def build_ui(self):
        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(fill="both", expand=True)

        self.chat_display = tk.Text(
            frame,
            bg="#1e1e1e",
            fg="white",
            font=("Segoe UI", 11),
            state="disabled",
            wrap="word",
            padx=10,
            pady=10,
            relief="flat",
            cursor="arrow"
        )
        self.chat_display.pack(side="left", fill="both", expand=True)

        scrollbar = tk.Scrollbar(frame, command=self.chat_display.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_display.config(yscrollcommand=scrollbar.set)

        self.chat_display.bind("<Button-1>", lambda e: "break")

        bottom_frame = tk.Frame(self.root, bg="#1e1e1e")
        bottom_frame.pack(fill="x", padx=6, pady=(0, 6))

        self.entry = tk.Entry(
            bottom_frame, font=("Segoe UI", 12),
            bg="#2c2c2c", fg="white", insertbackground="white"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(
            bottom_frame, text="Send", command=self.send_message,
            bg="#00c853", fg="white", font=("Segoe UI", 10, "bold")
        )
        send_btn.pack(side="right", padx=(6, 0))

        voice_btn = tk.Button(
            bottom_frame, text="🎤", command=self.voice_input,
            bg="#2c2c2c", fg="white", font=("Segoe UI", 12)
        )
        voice_btn.pack(side="right", padx=(6, 0))

        self.display_message("Bot", "Hi! I'm your Gemini chatbot. How can I help you?")

    def display_message(self, sender, message):
        self.chat_display.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M")
        formatted = f"{sender} ({timestamp}): {message}\n\n"
        self.chat_display.insert(tk.END, formatted)
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def send_message(self):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, tk.END)
        self.display_message("You", user_input)
        self.show_typing()

        def bot_reply():
            try:
                response = self.chat.send_message(user_input)
            except Exception as e:
                response = f"Error: {e}"
            self.hide_typing()
            self.display_message("Bot", response)
            speak(response) 

        threading.Thread(target=bot_reply, daemon=True).start()

    def show_typing(self):
        self.typing = True
        self.typing_dots = 0

        def animate():
            if not self.typing:
                return
            self.chat_display.configure(state="normal")
            self.chat_display.delete("end-2l", "end-1l")
            dots = "." * (self.typing_dots % 4)
            self.chat_display.insert(tk.END, f"Bot is typing{dots}\n")
            self.chat_display.configure(state="disabled")
            self.chat_display.see(tk.END)
            self.typing_dots += 1
            self.root.after(500, animate)

        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, "Bot is typing\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)
        animate()

    def hide_typing(self):
        self.typing = False
        self.chat_display.configure(state="normal")
        self.chat_display.delete("end-2l", "end-1l")
        self.chat_display.configure(state="disabled")

    def voice_input(self):
        def record_and_send():
            user_input = listen_voice()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, user_input)
            self.send_message()

        threading.Thread(target=record_and_send, daemon=True).start()

def main():
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
