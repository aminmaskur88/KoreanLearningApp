from flask import Blueprint, jsonify, request, current_app
import sqlite3

api_bp = Blueprint('api', __name__)

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
