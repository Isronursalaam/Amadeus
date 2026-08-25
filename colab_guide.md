# Panduan Menjalankan API Shiroko di Google Colab

Dengan cara ini, Anda bisa menyalakan mesin suara Shiroko di server milik Google (lengkap dengan kartu grafis super cepat) dan menyambungkannya ke laptop Anda atau laptop teman Anda.

## Persiapan Awal
1. **Buat Akun Ngrok (Gratis):**
   - Buka [ngrok.com](https://ngrok.com/) dan buat akun.
   - Masuk ke dashboard, cari menu **"Your Authtoken"**, lalu *copy* token unik Anda (kita akan membutuhkannya nanti untuk membuka "terowongan" internet dari Colab ke laptop Anda).
2. **Siapkan File Model Shiroko:**
   - Anda membutuhkan dua file yang sudah Anda *training* sebelumnya:
     1. File `.ckpt` (dari folder `GPT_weights`)
     2. File `.pth` (dari folder `SoVITS_weights`)
   - **Upload kedua file ini** ke dalam akun Google Drive Anda (buat folder bernama `Shiroko_Models` agar rapi).

---

## Langkah-langkah di Google Colab

1. **Buka Google Colab** ([colab.research.google.com](https://colab.research.google.com/)) dan buat *Notebook* baru.
2. **Aktifkan GPU:**
   - Di menu atas, klik `Runtime` > `Change runtime type` (Ubah jenis runtime).
   - Pada opsi *Hardware accelerator*, pilih **T4 GPU** lalu *Save*.
3. **Masukkan & Jalankan Kode Instalasi**
   - *Copy-paste* kode di bawah ini ke dalam kotak *cell* Colab, lalu tekan tombol ▶️ (*Play*):

```bash
# 1. Mengunduh GPT-SoVITS
!git clone https://github.com/RVC-Boss/GPT-SoVITS.git
%cd GPT-SoVITS

# 2. Menginstal Library yang dibutuhkan
!pip install -r requirements.txt
!pip install pyngrok

# 3. Mengunduh Model Dasar (Pre-trained)
!mkdir -p GPT_SoVITS/pretrained_models
!wget -O GPT_SoVITS/pretrained_models/chinese-hubert-base.zip https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/chinese-hubert-base.zip
!unzip -q GPT_SoVITS/pretrained_models/chinese-hubert-base.zip -d GPT_SoVITS/pretrained_models/
!wget -O GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large.zip https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/chinese-roberta-wwm-ext-large.zip
!unzip -q GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large.zip -d GPT_SoVITS/pretrained_models/
```

4. **Sambungkan Google Drive Anda**
   - Buat kotak *cell* baru dan jalankan kode ini untuk mengambil model Shiroko dari Google Drive Anda:

```python
from google.colab import drive
drive.mount('/content/drive')

# Meng-copy model Shiroko ke dalam mesin Colab
!cp "/content/drive/MyDrive/Shiroko_Models/Shiroko_GPT_Final.ckpt" /content/GPT-SoVITS/GPT_weights_v2/Shiroko-e5.ckpt
!cp "/content/drive/MyDrive/Shiroko_Models/Shiroko_SoVITS_Final.pth" /content/GPT-SoVITS/SoVITS_weights_v2/Shiroko_e4_s140.pth
```
*(Ganti nama file .ckpt dan .pth di atas dengan nama asli file milik Anda).*

5. **Jalankan Server dan Buka Terowongan Ngrok**
   - Buat *cell* baru, lalu jalankan kode pamungkas ini. 
   - **GANTI** tulisan `TOKEN_NGROK_ANDA_DISINI` dengan token asli yang Anda dapatkan dari *website* ngrok di langkah persiapan tadi!

```python
import os
from pyngrok import ngrok

# Mengganti Token Ngrok
NGROK_TOKEN = "TOKEN_NGROK_ANDA_DISINI"
ngrok.set_auth_token(NGROK_TOKEN)

# Membuka Terowongan (Tunneling) Port 9880
public_url = ngrok.connect(9880).public_url
print("==================================================")
print(f"✅ URL API SHIROKO ANDA: {public_url}")
print("Ganti URL pada file shiroko.py / shiroko_tts.py Anda dengan URL di atas!")
print("==================================================")

# Menyalakan API GPT-SoVITS V2
!python api_v2.py -a 127.0.0.1 -p 9880 -c GPT_SoVITS/configs/tts_infer.yaml
```

---

## Langkah Terakhir (Di Komputer Anda)

Setelah Anda menjalankan langkah ke-5 di atas, Colab akan memberikan sebuah URL unik seperti:
`https://a1b2c3d4.ngrok-free.app`

Buka file **`shiroko_tts.py`** atau **`shiroko.py`** Anda di komputer lokal, lalu ganti bagian:
```python
self.api_url = "http://127.0.0.1:9880"
```
menjadi:
```python
self.api_url = "https://a1b2c3d4.ngrok-free.app"
```

**Selesai!** 🎉 
Sekarang selama Google Colab di *browser* Anda tetap menyala (jangan di-*close* halamannya), Anda bisa menjalankan program Amadeus di laptop mana pun secara instan!
