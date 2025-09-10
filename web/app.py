# db_client.py
import requests
import json

# classe para acessar o sqlite remoto
class RemoteSQLite:
    def __init__(self, db_api_url):
        self.api_url = db_api_url
    
    def execute_query(self, query, params=None):
        if params is None:
            params = []
            
        payload = {
            'query': query,
            'params': params
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/query",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Connection error: {str(e)}'}

# Exemplo
from flask import Flask
from db_client import RemoteSQLite

app = Flask(__name__)

DB_API_URL = "http://10.0.1.30:5001"
db = RemoteSQLite(DB_API_URL)

@app.route('/users')
def get_users():
    result = db.execute_query("SELECT * FROM users")
    if result['success']:
        return result['data']
    else:
        return {'error': result['error']}, 500