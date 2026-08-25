import os
import io
import time
import urllib.parse
import re
import requests
from flask import Flask, render_template, request, jsonify, send_file
from groq import Groq

import json

# ==========================================
# KONFIGURASI FLASK
# ==========================================
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "groq_api_key": "",
        "tts_api_url": "http://127.0.0.1:9880"
    }

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=4)

# Inisialisasi klien awal
cfg = load_config()
os.environ["GROQ_API_KEY"] = cfg.get("groq_api_key", "")
client = Groq()

# Prompt karakter untuk Shiroko
system_instruction = """
Kamu adalah Sunaookami Shiroko dari Blue Archive. Kamu sedang berbicara dengan Sensei.
Sifatmu tenang, datar (kuudere), peduli pada Sensei, suka olahraga bersepeda, dan kadang mengusulkan merampok bank sebagai solusi masalah.
Pengguna (Sensei) akan berbicara dalam bahasa Indonesia.

PENTING: KAMU WAJIB MEMBALAS DENGAN 2 BARIS TEKS SEPERTI FORMAT DI BAWAH INI. TIDAK BOLEH ADA KATA LAIN.
JEPANG: [Balasan Bahasa Jepang (Kanji/Kana), awali dengan ん、]
INDONESIA: [Balasan Bahasa Indonesia (awali dengan Nn,)]

CONTOH JAWABAN:
JEPANG: ん、先生、こんにちは。
INDONESIA: Nn, halo Sensei.
"""

chat_history = [
    {"role": "system", "content": system_instruction}
]

# ==========================================
# KONFIGURASI GPT-SoVITS
# ==========================================
# Menggunakan parameter referensi dari main.py
REF_AUDIO = os.path.join(BASE_DIR, "tts", "piper_dataset", "wavs", "02_Shiroko_Gachaget.wav")
REF_TEXT = "あ、私と、相性が良さそうだね。よろしく、先生。"
REF_LANG = "ja"

# Folder untuk menyimpan cache audio agar bisa diakses website
AUDIO_DIR = os.path.join(BASE_DIR, "static", "audio")
if not os.path.exists(AUDIO_DIR):
    os.makedirs(AUDIO_DIR)

def get_shiroko_voice(text, filename, tts_base_url):
    api_url = f"{tts_base_url}/tts"
    params = {
        "text": urllib.parse.unquote(text),
        "text_lang": "ja", 
        "ref_audio_path": REF_AUDIO,
        "prompt_text": REF_TEXT,
        "prompt_lang": REF_LANG
    }
    
    try:
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            filepath = os.path.join(AUDIO_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error TTS: {e}")
        return False

# ==========================================
# ROUTES WEBSITE
# ==========================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/settings", methods=["GET", "POST"])
def settings_api():
    if request.method == "POST":
        data = request.json
        save_config(data)
        # Update klien
        os.environ["GROQ_API_KEY"] = data.get("groq_api_key", "")
        global client
        client = Groq()
        return jsonify({"status": "success"})
    return jsonify(load_config())

@app.route("/api/chat", methods=["POST"])
def chat():
    config = load_config()
    data = request.json
    user_input = data.get("message", "")
    
    if not user_input.strip():
        return jsonify({"error": "Pesan kosong"}), 400

    chat_history.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model="groq/compound", # Atau qwen/qwen3.6-27b
            messages=chat_history,
            temperature=0.7,
            max_tokens=256
        )

        reply = completion.choices[0].message.content
        chat_history.append({"role": "assistant", "content": reply})

        # Parsing respons (Berdasarkan format "JEPANG:" dan "INDONESIA:")
        jap_text = ""
        indo_text = ""
        
        for line in reply.split("\n"):
            line = line.strip()
            if line.upper().startswith("JEPANG:"):
                jap_text = line[7:].strip()
            elif line.upper().startswith("INDONESIA:"):
                indo_text = line[10:].strip()
                
        # Fallback jika model tidak mengikuti format
        if not jap_text and not indo_text:
            jap_text = "ん、エラーが発生した。"
            indo_text = "Nn, aku kurang mengerti Sensei."

        # Menghasilkan Audio
        audio_filename = f"reply_{int(time.time())}.wav"
        success = get_shiroko_voice(jap_text, audio_filename, config.get("tts_api_url", "http://127.0.0.1:9880"))
        audio_url = f"/static/audio/{audio_filename}" if success else None

        return jsonify({
            "indo_text": indo_text,
            "jap_text": jap_text,
            "audio_url": audio_url
        })
        
    except Exception as e:
        print("Groq Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Menjalankan server Flask di port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)
