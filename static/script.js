document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const audioPlayer = document.getElementById('tts-audio');

    // Menggulung ke bawah secara otomatis
    function scrollToBottom() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Mendapatkan waktu saat ini (HH:MM)
    function getCurrentTime() {
        const now = new Date();
        return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
    }

    // Menambahkan pesan pengguna ke UI
    function appendUserMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message sent';
        
        msgDiv.innerHTML = `
            <div class="message-content">
                <p>${text}</p>
            </div>
            <span class="timestamp">${getCurrentTime()}</span>
        `;
        
        chatBox.appendChild(msgDiv);
        scrollToBottom();
    }

    // Menambahkan indikator mengetik (loading)
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message received typing-msg';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        `;
        
        chatBox.appendChild(typingDiv);
        scrollToBottom();
    }

    // Menghapus indikator mengetik
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Menambahkan balasan Shiroko ke UI
    function appendBotMessage(indoText, japText, audioUrl) {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message received';
        
        msgDiv.innerHTML = `
            <div class="message-content">
                <p>${indoText}</p>
                ${japText ? `<span class="jap-text">${japText}</span>` : ''}
            </div>
            <span class="timestamp">${getCurrentTime()}</span>
        `;
        
        chatBox.appendChild(msgDiv);
        scrollToBottom();

        // Memutar audio jika ada
        if (audioUrl) {
            audioPlayer.src = audioUrl;
            // Tambahkan parameter acak agar browser tidak menggunakan cache lama
            audioPlayer.src = audioUrl + "?t=" + new Date().getTime();
            audioPlayer.play().catch(e => console.error("Auto-play terblokir browser:", e));
        }
    }

    // Event saat form disubmit
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const text = userInput.value.trim();
        if (!text) return;

        // Kosongkan input dan tampilkan pesan pengguna
        userInput.value = '';
        appendUserMessage(text);
        
        // Tampilkan loading
        showTypingIndicator();

        try {
            // Kirim ke backend Flask
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();
            
            // Hapus loading dan tampilkan hasil
            hideTypingIndicator();
            
            if (response.ok) {
                appendBotMessage(data.indo_text, data.jap_text, data.audio_url);
            } else {
                appendBotMessage("Nn, sepertinya koneksiku terputus...", `Error: ${data.error}`, null);
            }
            
        } catch (error) {
            hideTypingIndicator();
            appendBotMessage("Nn, sistem Amadeus gagal terhubung.", "Koneksi ke server terputus.", null);
            console.error("Error:", error);
        }
    });
});

    // --- Settings Modal Logic ---
    const settingsBtn = document.querySelector('.icon-btn');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettings = document.getElementById('close-settings');
    const settingsForm = document.getElementById('settings-form');
    const groqKeyInput = document.getElementById('groq-key');
    const ttsUrlInput = document.getElementById('tts-url');

    // Load settings from backend
    async function loadSettings() {
        try {
            const res = await fetch('/api/settings');
            const data = await res.json();
            if (data.groq_api_key) groqKeyInput.value = data.groq_api_key;
            if (data.tts_api_url) ttsUrlInput.value = data.tts_api_url;
        } catch (err) {
            console.error("Gagal memuat pengaturan", err);
        }
    }

    settingsBtn.addEventListener('click', () => {
        loadSettings();
        settingsModal.classList.add('active');
    });

    closeSettings.addEventListener('click', () => {
        settingsModal.classList.remove('active');
    });

    settingsForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const saveBtn = document.getElementById('save-settings-btn');
        saveBtn.innerText = 'Menyimpan...';
        
        try {
            const res = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    groq_api_key: groqKeyInput.value.trim(),
                    tts_api_url: ttsUrlInput.value.trim()
                })
            });
            if (res.ok) {
                saveBtn.innerText = 'Tersimpan!';
                setTimeout(() => {
                    settingsModal.classList.remove('active');
                    saveBtn.innerText = 'Simpan Pengaturan';
                }, 1000);
            }
        } catch (err) {
            saveBtn.innerText = 'Gagal menyimpan!';
            console.error("Gagal menyimpan", err);
            setTimeout(() => saveBtn.innerText = 'Simpan Pengaturan', 2000);
        }
    });
