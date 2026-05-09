from flask import Blueprint, jsonify, request, current_app
import sqlite3

import json
import os

import requests
import json
import os
import re

api_bp = Blueprint('api', __name__)

@api_bp.route('/report_mistake', methods=['POST'])
def report_mistake():
    data = request.json
    item_type = data.get('item_type') # 'vocab' or 'hangul'
    item_id = data.get('item_id')
    
    conn = get_db_connection()
    row = conn.execute('SELECT wrong_count FROM user_mistakes WHERE user_id = 1 AND item_type = ? AND item_id = ?', (item_type, item_id)).fetchone()
    
    if row:
        conn.execute('UPDATE user_mistakes SET wrong_count = wrong_count + 1, last_wrong = CURRENT_TIMESTAMP WHERE user_id = 1 AND item_type = ? AND item_id = ?', (item_type, item_id))
    else:
        conn.execute('INSERT INTO user_mistakes (user_id, item_type, item_id, wrong_count) VALUES (1, ?, ?, 1)', (item_type, item_id))
    
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

# Global model list for rotation
AVAILABLE_MODELS = [
    "gemini-3.1-pro-preview", 
    "gemini-3.1-flash-lite-preview", 
    "gemini-2.5-pro", 
    "gemini-2.5-flash", 
    "gemini-1.5-flash"
]

def call_gemini(prompt):
    global AVAILABLE_MODELS
    # Retrieve key from local file
    key_path = "gemini_key.txt"
    try:
        with open(key_path, 'r') as f:
            api_key = f.read().strip().split('\n')[0]
    except:
        return None

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    # Copy list to iterate without mutation issues during the loop
    current_attempt_list = list(AVAILABLE_MODELS)
    
    for model in current_attempt_list:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                text = re.sub(r"^\s*```json\s*|\s*```\s*$", "", text, flags=re.MULTILINE)
                return json.loads(text)
            else:
                print(f"Model {model} failed with status {resp.status_code}. Rotating to bottom.")
                # Rotate failed model to the end of the global list
                if model in AVAILABLE_MODELS:
                    AVAILABLE_MODELS.remove(model)
                    AVAILABLE_MODELS.append(model)
        except Exception as e:
            print(f"Error with model {model}: {e}")
            if model in AVAILABLE_MODELS:
                AVAILABLE_MODELS.remove(model)
                AVAILABLE_MODELS.append(model)
            
    return None

@api_bp.route('/generate_ai_exam')
def generate_ai_exam():
    section_id = request.args.get('section_id')
    
    conn = get_db_connection()
    # Get most frequent mistakes
    mistakes = conn.execute('''
        SELECT m.*, v.korean, v.meaning 
        FROM user_mistakes m 
        JOIN vocabulary v ON m.item_id = v.id 
        WHERE m.item_type = 'vocab' 
        ORDER BY m.wrong_count DESC LIMIT 15
    ''').fetchall()
    conn.close()

    if not mistakes:
        return jsonify({"error": "Belum ada data kesalahan yang cukup. Silakan berlatih lebih banyak dulu!"}), 404

    mistake_list = [{"korean": m['korean'], "meaning": m['meaning'], "errors": m['wrong_count']} for m in mistakes]
    
    prompt = f"""
    Kamu adalah pakar pendidik Bahasa Korea. Tugasmu adalah membuat 10 soal ujian personal untuk membantu murid memperbaiki kesalahannya.
    
    DAFTAR KATA YANG SERING SALAH (Prioritaskan ini):
    {json.dumps(mistake_list)}
    
    ATURAN PEMBUATAN SOAL:
    1. Tiap soal harus unik dan berkualitas tinggi.
    2. Tipe soal: 'choice' (pilihan ganda) atau 'typing' (mengetik jawaban).
    3. Untuk tipe 'choice':
       - WAJIB memiliki tepat 4 pilihan (options).
       - Pilihan TIDAK BOLEH ada yang duplikat/sama.
       - Hanya boleh ada 1 jawaban yang benar (answer).
       - Jawaban (answer) WAJIB ada di dalam daftar pilihan (options).
       - Distraktor (pilihan salah) harus masuk akal tapi jelas salah. Jangan gunakan variasi typo yang membingungkan seperti '감사합니', '감사함니'. Gunakan kata lain yang berbeda maknanya.
    4. Gunakan instruksi soal dalam Bahasa Indonesia yang alami.
    
    FORMAT JSON (Array of Objects):
    [
      {{
        "type": "choice",
        "question": "Apa arti dari kata '안녕하세요'?",
        "target": "안녕하세요",
        "options": ["Halo", "Sore", "Tidur", "Makan"],
        "answer": "Halo"
      }},
      {{
        "type": "typing",
        "question": "Bagaimana cara menulis 'Terima kasih' dalam Hangul?",
        "target": "Terima kasih",
        "options": [],
        "answer": "감사합니다"
      }}
    ]
    """
    
    ai_exam = call_gemini(prompt)
    if ai_exam:
        return jsonify(ai_exam)
    else:
        # Fallback to normal vocab if AI fails
        return jsonify({"error": "Gagal memanggil AI"}), 500

@api_bp.route('/curriculum')
def get_curriculum():
    with open('data/curriculum.json', 'r') as f:
        return jsonify(json.load(f))

def get_db_connection():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@api_bp.route('/user')
def get_user():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()
    return jsonify(dict(user))

@api_bp.route('/hangul')
def get_hangul():
    conn = get_db_connection()
    hangul = conn.execute('SELECT * FROM hangul').fetchall()
    conn.close()
    return jsonify([dict(row) for row in hangul])

@api_bp.route('/vocabulary')
def get_vocabulary():
    category = request.args.get('category')
    level = request.args.get('level')
    
    query = 'SELECT * FROM vocabulary'
    params = []
    
    if category or level:
        query += ' WHERE'
        if category:
            query += ' category = ?'
            params.append(category)
        if level:
            if category: query += ' AND'
            query += ' level = ?'
            params.append(level)
            
    conn = get_db_connection()
    vocab = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in vocab])

@api_bp.route('/categories')
def get_categories():
    conn = get_db_connection()
    categories = conn.execute('SELECT DISTINCT category FROM vocabulary').fetchall()
    conn.close()
    return jsonify([row['category'] for row in categories])

@api_bp.route('/update_xp', methods=['POST'])
def update_xp():
    data = request.json
    xp_to_add = data.get('xp', 0)
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    new_xp = user['xp'] + xp_to_add
    
    # Simple level logic
    new_level = (new_xp // 100) + 1
    
    conn.execute('UPDATE users SET xp = ?, level = ? WHERE id = 1', (new_xp, new_level))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'new_xp': new_xp, 'new_level': new_level})

@api_bp.route('/progress')
def get_progress():
    conn = get_db_connection()
    progress = conn.execute('SELECT category, pass_count FROM category_progress WHERE user_id = 1').fetchall()
    conn.close()
    return jsonify({row['category']: row['pass_count'] for row in progress})

@api_bp.route('/complete_category', methods=['POST'])
def complete_category():
    data = request.json
    category = data.get('category')
    
    conn = get_db_connection()
    # Check if exists
    row = conn.execute('SELECT pass_count FROM category_progress WHERE user_id = 1 AND category = ?', (category,)).fetchone()
    
    if row:
        new_count = row['pass_count'] + 1
        conn.execute('UPDATE category_progress SET pass_count = ? WHERE user_id = 1 AND category = ?', (new_count, category))
    else:
        new_count = 1
        conn.execute('INSERT INTO category_progress (user_id, category, pass_count) VALUES (1, ?, 1)', (category,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success', 'new_count': new_count})
