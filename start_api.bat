@echo off
echo Memulai GPT-SoVITS API Server...
cd /d "D:\GPT-SoVITS\GPT-SoVITS-v3lora-20250228"
set HF_ENDPOINT=https://hf-mirror.com
runtime\python.exe api_v2.py
pause
