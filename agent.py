import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from deep_translator import GoogleTranslator
from gtts import gTTS
import pygame

# Initialize sound mixer for pronunciation safely
try:
    pygame.mixer.init()
except Exception:
    pass  # Fallback for systems with missing or busy audio devices

# Popular languages supporting both translation and TTS
LANGUAGES = {
    "english": "en",
    "french": "fr",
    "latin": "la",
    "japanese": "ja",
    "chinese": "zh-CN",
    "arabic": "ar",
    "hindi": "hi",
    "spanish": "es",
    "german": "de",
    "italian": "it",
    "portuguese": "pt",
    "russian": "ru",
    "korean": "ko"
}

# AI Agent natural command parse logic
def parse_agent_command(text):
    text_lower = text.lower().strip()
    target_lang_code = "en"  # default
    target_lang_name = "english"
    phrase = text

    # Handle Natural Language Inputs (e.g., "Translate Hello to Japanese" or "To French: Good morning")
    for lang, code in LANGUAGES.items():
        patterns = [
            f"translate to {lang}", 
            f"to {lang}", 
            f"in {lang}", 
            f"translate {lang}"
        ]
        for pattern in patterns:
            if pattern in text_lower:
                target_lang_code = code
                target_lang_name = lang
                
                # Strip command patterns to isolate target phrase
                extracted = text_lower.replace(pattern, "").strip()
                extracted = extracted.strip(":").strip(",").strip()
                if extracted:
                    phrase = extracted
                break
    
    return phrase, target_lang_code, target_lang_name

class TranslationAgent:
    def __init__(self):
        pass

    def translate(self, text, target_lang):
        try:
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translated
        except Exception as e:
            return f"Translation Error: {e}"

    def get_meaning(self, text):
        # Using free dictionary API for single-word contextual analysis
        word = text.strip().split()[0] if text else ""
        if not word:
            return "No text detected to check meaning."
        try:
            response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                meanings = data[0].get('meanings', [])
                if meanings:
                    definition = meanings[0]['definitions'][0]['definition']
                    part_of_speech = meanings[0].get('partOfSpeech', 'noun')
                    return f"[{part_of_speech}] Definition: {definition}"
            return "Definition check works best on single target words. Try analyzing individual words."
        except Exception:
            return "Unable to connect to dictionary databases. Check your internet."

    def play_pronunciation(self, text, lang):
        def play_sound():
            try:
                tts = gTTS(text=text, lang=lang)
                filename = "agent_audio.mp3"
                tts.save(filename)
                
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.music.unload()
                os.remove(filename)
            except Exception as e:
                print(f"Audio error: {e}")
                
        threading.Thread(target=play_sound, daemon=True).start()

# Visual graphical Desktop Interface
class AgentGUI:
    def __init__(self, root):
        self.agent = TranslationAgent()
        self.root = root
        self.root.title("Universal Translate AI Agent")
        self.root.geometry("650x550")
        
        # Grid Configuration & Styling
        style = ttk.Style()
        style.theme_use("clam")

        main_frame = ttk.Frame(root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Label(main_frame, text="🤖 UNIVERSAL TRANSLATE AI AGENT", font=("Arial", 16, "bold"), foreground="#2980b9")
        header.pack(anchor="w", pady=(0, 10))

        instruction = ttk.Label(main_frame, text="AI Natural Command Box (e.g. 'Translate welcome to Hindi' OR choose manually below):", font=("Arial", 10, "italic"))
        instruction.pack(anchor="w", pady=(0, 5))

        self.input_box = tk.Text(main_frame, height=5, font=("Arial", 11), wrap="word")
        self.input_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.input_box.insert(tk.END, "Hello, how are you to French")

        controls = ttk.Frame(main_frame)
        controls.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(controls, text="Or Choose Lang: ", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.lang_var = tk.StringVar(value="french")
        self.lang_dropdown = ttk.Combobox(controls, textvariable=self.lang_var, values=list(LANGUAGES.keys()), state="readonly", width=12)
        self.lang_dropdown.pack(side=tk.LEFT, padx=(0, 15))

        self.btn_run = ttk.Button(controls, text="⚡ Execute AI Agent", command=self.run_agent)
        self.btn_run.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_mean = ttk.Button(controls, text="📖 Show Definition", command=self.show_meaning)
        self.btn_mean.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_play = ttk.Button(controls, text="🔊 Speak Pronunciation", command=self.speak_target)
        self.btn_play.pack(side=tk.LEFT)

        ttk.Label(main_frame, text="Agent Diagnostics & Outputs:", font=("Arial", 11, "bold")).pack(anchor="w", pady=(5, 5))

        self.output_box = tk.Text(main_frame, height=8, bg="#f5f6fa", fg="#2f3640", font=("Arial", 11), wrap="word")
        self.output_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.last_translated_text = ""
        self.last_lang_code = "en"

    def run_agent(self):
        raw_input = self.input_box.get("1.0", tk.END).strip()
        if not raw_input:
            messagebox.showwarning("Warning", "Please input a word, sentence, or natural command!")
            return

        phrase, code, name = parse_agent_command(raw_input)
        
        # If no targeted phrasing was mentioned, fall back manually
        if code == "en" and self.lang_dropdown.get():
            name = self.lang_dropdown.get()
            code = LANGUAGES[name]
            phrase = raw_input

        translated = self.agent.translate(phrase, code)
        self.last_translated_text = translated
        self.last_lang_code = code

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, f"🎯 Focus Text: '{phrase}'\n"
                                      f"🌐 Agent Target: Translating to {name.capitalize()} ({code.upper()})\n\n"
                                      f"📝 Translated Result:\n{translated}\n")

    def show_meaning(self):
        raw_input = self.input_box.get("1.0", tk.END).strip()
        phrase, _, _ = parse_agent_command(raw_input)
        
        meaning = self.agent.get_meaning(phrase)
        self.output_box.insert(tk.END, f"\n📙 Explanation / Contextual meaning:\n{meaning}\n")

    def speak_target(self):
        if not self.last_translated_text:
            messagebox.showwarning("No Output", "Translate a phrase first to hear pronunciation!")
            return
        self.agent.play_pronunciation(self.last_translated_text, self.last_lang_code)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentGUI(root)
    root.mainloop()