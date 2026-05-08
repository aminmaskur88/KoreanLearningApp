# K-Study: Aplikasi Belajar Bahasa Korea Modern

Aplikasi belajar Bahasa Korea ringan, modern, dan mobile-friendly yang dirancang untuk dijalankan di Termux Android, Linux, atau Windows.

## Fitur Utama
- **Dashboard Interaktif:** Pantau XP, Level, dan Misi Harian.
- **Belajar Hangul:** Mengenal huruf vokal dan konsonan dengan audio TTS.
- **Kamus Kosakata:** 100+ kosakata dasar dengan kategori dan contoh kalimat.
- **Flashcards:** Latihan menghafal cepat dengan sistem balik kartu.
- **Sistem Quiz:** Uji kemampuan Anda dan dapatkan XP untuk naik level.
- **Dark Mode:** Nyaman di mata untuk belajar malam hari.
- **PWA Support:** Bisa di-install ke home screen HP seperti aplikasi native.

## Teknologi
- **Backend:** Python Flask
- **Frontend:** Vanilla HTML, CSS, JavaScript (Fetch API)
- **Database:** SQLite
- **Audio:** Web Speech API (Korean TTS)

## Cara Install & Menjalankan

### 1. Di Termux (Android)
```bash
pkg update && pkg upgrade
pkg install python
cd KoreanLearningApp
pip install -r requirements.txt
chmod +x run.sh
./run.sh
```

### 2. Di Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./run.sh
```

### 3. Di Windows
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Buka browser di alamat: `http://localhost:5000`

## Struktur Folder
- `app.py`: Entry point aplikasi.
- `init_db.py`: Inisialisasi & seeding database.
- `data/`: Data mentah JSON (Hangul & Vocab).
- `static/`: File CSS, JS, dan Manifest PWA.
- `templates/`: Template HTML Jinja2.
- `routes/`: Logika API dan View.
