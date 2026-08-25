import requests
import io
import os
import urllib.parse
import time
import re

try:
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
except ImportError:
    print("Library belum lengkap. Silakan jalankan:")
    print("pip install pygame requests groq")
    exit()

try:
    from groq import Groq
except ImportError:
    print("Library Groq belum ter-install. Silakan buka terminal baru dan jalankan:")
    print("pip install groq")
    exit()

# ==========================================
# PENGATURAN API AI (GROQ)
# ==========================================
GROQ_API_KEY = ""
client = Groq(api_key=GROQ_API_KEY)
# Menggunakan LLaMA 3 dari Groq (Sangat cepat dan gratis)
MODEL_NAME = "groq/compound"

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

# Menyimpan riwayat chat (Memory)
chat_history = [
    {"role": "system", "content": system_instruction}
]

# ==========================================
# KONFIGURASI GPT-SoVITS
# ==========================================
API_BASE = "http://127.0.0.1:9880"
API_URL = f"{API_BASE}/tts"

# Path dinamis yang selalu mengikuti lokasi folder Amadeus
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GPT_WEIGHT = os.path.join(BASE_DIR, "models", "Shiroko-e15.ckpt")
SOVITS_WEIGHT = os.path.join(BASE_DIR, "models", "Shiroko_e8_s280.pth")

REF_AUDIO = os.path.join(BASE_DIR, "tts", "piper_dataset", "wavs", "02_Shiroko_Gachaget.wav")
REF_TEXT = "アビドス対策委員会２年生砂狼シロコ。よろしく。"
REF_LANG = "ja"


def init_models():
    print("[Memuat Model Suara Shiroko ke API...]")
    try:
        req_gpt = requests.get(f"{API_BASE}/set_gpt_weights?weights_path={GPT_WEIGHT}")
        req_sovits = requests.get(f"{API_BASE}/set_sovits_weights?weights_path={SOVITS_WEIGHT}")
        if req_gpt.status_code == 200 and req_sovits.status_code == 200:
            print("[Model Suara Berhasil Dimuat!]")
            return True
        else:
            print(f"Error memuat model: {req_gpt.text} | {req_sovits.text}")
            return False
    except Exception as e:
        print(f"Gagal konek ke GPT-SoVITS API. Pastikan start_api.bat berjalan. Error: {e}")
        return False

def get_shiroko_voice(text):
    params = {
        "text": urllib.parse.unquote(text),
        "text_lang": "ja", 
        "ref_audio_path": REF_AUDIO,
        "prompt_text": REF_TEXT,
        "prompt_lang": REF_LANG
    }
    
    try:
        response = requests.get(API_URL, params=params)
        if response.status_code == 200:
            return response.content
        else:
            return None
    except Exception as e:
        return None

def play_audio(audio_bytes):
    pygame.mixer.init()
    audio_stream = io.BytesIO(audio_bytes)
    pygame.mixer.music.load(audio_stream)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def main():
    print("="*50)
    print("  Chatbot Shiroko AI (Groq LLaMA) + Suara TTS  ")
    print("="*50)
    
    time.sleep(1)
    if not init_models():
        return
        
    print("\n[AI Ready] Ketik 'keluar' untuk berhenti.\n")
    
    while True:
        user_input = input("Sensei: ")
        if user_input.lower() in ['keluar', 'exit', 'quit']:
            break

        try:
            # Tambahkan ke riwayat chat
            chat_history.append({"role": "user", "content": user_input})
            
            # Memanggil API Groq
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=chat_history,
                temperature=0.6,
                max_tokens=150,
                top_p=0.9,
            )
            
            bot_reply = completion.choices[0].message.content.strip()
            
            # Simpan balasan AI ke riwayat
            chat_history.append({"role": "assistant", "content": bot_reply})
            
            jp_text = ""
            id_text = ""
            
            # Parse Regex Sederhana
            match_jp = re.search(r'JEPANG:\s*(.+)', bot_reply, re.IGNORECASE)
            if match_jp:
                jp_text = match_jp.group(1).strip()
            
            match_id = re.search(r'INDONESIA:\s*(.+)', bot_reply, re.IGNORECASE)
            if match_id:
                id_text = match_id.group(1).strip()
                
            if not jp_text or not id_text:
                jp_text = "ん、わかった。"
                id_text = "(Parse Gagal) " + bot_reply
                
            jp_text = jp_text.replace('*', '').replace('`', '')
            id_text = id_text.replace('*', '').replace('`', '')

            print(f"Shiroko: {id_text}")
            
            # Panggil API TTS dengan teks Jepang
            audio = get_shiroko_voice(jp_text)
            if audio:
                play_audio(audio)
                
        except Exception as e:
            print(f"Terjadi kesalahan pada AI Groq: {e}")

if __name__ == "__main__":
    main()
