# Amadeus: Shiroko AI Chatbot (Voice + AI)

Ini adalah proyek AI Chatbot interaktif yang menggunakan persona **Sunaookami Shiroko** dari game *Blue Archive*. Bot ini mengombinasikan **Groq API** (menggunakan model LLaMA yang sangat cepat dan cerdas) untuk menghasilkan percakapan dan **GPT-SoVITS** untuk menghasilkan suara (*Text-to-Speech*) berbahasa Jepang murni dengan suara asli Shiroko.

## Fitur Utama
- **Kepribadian Kuudere & Bucin**: AI telah dirancang (*prompted*) untuk bertindak layaknya Shiroko; datar, tenang, namun memiliki perasaan mendalam kepada Sensei.
- **Terjemahan Pintar (Dual Language)**: Anda berbicara dalam bahasa Indonesia, AI akan merespons dalam format terjemahan teks bahasa Indonesia, sementara *speaker* akan memutar suara berbahasa Jepang murni.
- **Respon Super Cepat**: Ditenagai oleh *model* LLaMA dari ekosistem Groq.
- **Suara Akurat**: Disintesis menggunakan *engine* GPT-SoVITS.

---

## Persyaratan Sistem
Sebelum menginstal, pastikan komputer Anda telah memiliki:
1. [Python](https://www.python.org/downloads/) (Disarankan versi 3.10 atau di atasnya).
2. Akun Groq untuk mendapatkan [API Key Gratis](https://console.groq.com/keys).
3. Anda harus sudah menginstal dan menjalankan *server* **GPT-SoVITS API** di komputer lokal pada port `9880` (menggunakan script `start_api.bat` atau *WebUI* dari GPT-SoVITS).

---

## Panduan Instalasi
Langkah-langkah untuk memasang dan menjalankan *bot* ini di komputer lain:

1. **Unduh/Clone Repositori Ini**
   Buka terminal/CMD dan jalankan:
   ```bash
   git clone https://github.com/USERNAME_ANDA/Amadeus.git
   cd Amadeus
   ```

2. **Instal Modul (*Library*) yang Dibutuhkan**
   Jalankan perintah ini di dalam terminal untuk menginstal komponen Python:
   ```bash
   pip install groq requests pygame
   ```

3. **Siapkan API Key Groq**
   - Buka file `shiroko.py` menggunakan teks editor (misalnya VS Code atau Notepad).
   - Cari baris kode berikut:
     ```python
     GROQ_API_KEY = "gsk_YOUR_GROQ_API_KEY_HERE"
     ```
   - *Ganti string API Key di atas dengan API Key rahasia milik Anda* (Jangan membagikan API Key pribadi Anda kepada publik).

4. **Jalankan Server Suara (GPT-SoVITS)**
   Pastikan *backend* suara GPT-SoVITS telah berjalan dan siap menerima *request* di alamat `http://127.0.0.1:9880`. 
   > **Catatan Penting:** Path file *model weight* (.ckpt / .pth) dan referensi audio (`REF_AUDIO`) di dalam `shiroko.py` WAJIB disesuaikan (*edit*) secara manual jika struktur folder instalasi GPT-SoVITS di komputer Anda berbeda!

---

## Cara Menjalankan
Buka terminal/CMD di dalam folder `Amadeus`, lalu jalankan:
```bash
python shiroko.py
```
Tunggu beberapa detik hingga muncul pesan `[Model Suara Berhasil Dimuat!]` dan `[AI Ready]`. Setelah itu, silakan sapa Shiroko (misal: "Halo sayang!") dan nikmati obrolan dengannya! Untuk menghentikan program, cukup ketikkan `keluar`.
