# api_db.py
from flask import Flask, request, jsonify
import sqlite3
import json

app = Flask(__name__)
DB_PATH = 'database.db'

@app.route('/query', methods=['POST'])
def execute_query():
    try:
        data = request.get_json()
        query = data['query']
        params = data.get('params', [])
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        
        if query.strip().upper().startswith('SELECT'):
            result = [dict(row) for row in cursor.fetchall()]
        else:
            conn.commit()
            result = {'affected_rows': cursor.rowcount}
            
        conn.close()
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='10.0.1.30', port=5001)