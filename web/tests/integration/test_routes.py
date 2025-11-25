import sys
import os
import pytest

# Ajuste de path para importar main.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.dirname(os.path.dirname(BASE_DIR)) 
sys.path.insert(0, WEB_DIR)

from main import app


@pytest.fixture
def client():
    app.testing = True
    return app.test_client()


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200


def test_plants(client):
    response = client.get('/plantas')
    assert response.status_code == 200

    html = response.get_data(as_text=True)
    assert "<html" in html.lower() or "<div" in html.lower()


def test_rotine_redirect_without_login(client):
    response = client.get('/rotina')
    
    assert response.status_code == 302
    assert "/login" in response.location


def test_rotine_with_login(client):
    with client.session_transaction() as sess:
        sess['username'] = "vinicius"

    response = client.get('/rotina')
    assert response.status_code == 200

    html = response.get_data(as_text=True).lower()
    assert "rotina" in html
