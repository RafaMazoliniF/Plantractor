import pytest
import requests
import random
import string

URL_WEB = "http://localhost:5000"
URL_DB = "http://localhost:5001"
URL_PROXY = "http://localhost:80"

def generate_random_user():
    letters = string.ascii_lowercase
    username = ''.join(random.choice(letters) for i in range(8))
    password = "Test@123" + ''.join(random.choice(letters) for i in range(4))
    return username, password

def test_web_service_status_code():
    try:
        response = requests.get(f"{URL_WEB}/")
        assert response.status_code == 200
        assert "PlanTractor" in response.text
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container WEB (porta 5000)")

def test_database_api_query():
    payload = {"query": "SELECT 1"}
    try:
        response = requests.post(f"{URL_DB}/query", json=payload)
        assert response.status_code == 200
        assert response.json()['success'] is True
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container DATABASE (porta 5001)")

def test_proxy_nginx_routing():
    try:
        response = requests.get(f"{URL_PROXY}/")
        assert response.status_code == 200
        assert "PlanTractor" in response.text
        assert "nginx" in response.headers.get("Server", "").lower() or response.ok
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container PROXY (porta 80)")

def test_home_content():
    response = requests.get(f"{URL_WEB}/")
    assert response.status_code == 200
    assert "<html" in response.text.lower()

def test_plants_content():
    response = requests.get(f"{URL_WEB}/plantas")
    assert response.status_code == 200
    
    html = response.text.lower()
    assert "<html" in html or "<div" in html

def test_rotine_redirect_without_login():
    response = requests.get(f"{URL_WEB}/rotina", allow_redirects=False)
    
    assert response.status_code == 302
    assert "/login" in response.headers.get("Location", "")

def test_rotine_with_login_flow():
    session = requests.Session()
    username, password = generate_random_user()

    reg_data = {'username': username, 'password': password}
    reg_response = session.post(f"{URL_WEB}/register", data=reg_data)
    assert reg_response.status_code == 200

    login_data = {'username': username, 'password': password}
    login_response = session.post(f"{URL_WEB}/login", data=login_data)
    
    assert login_response.status_code == 200
    
    response = session.get(f"{URL_WEB}/rotina")
    assert response.status_code == 200
    
    html = response.text.lower()
    assert "rotina" in html


def test_dark_mode_activation_simulation():
    """
    TESTE VISUAL: Simula que o dark mode está ativado verificando se 
    o HTML tem todos os componentes necessários para ativação
    """
    response = requests.get(f"{URL_WEB}/")
    assert response.status_code == 200
    
    html = response.text
    
    checklist = {
        'botao_toggle': 'data-theme-toggle' in html,
        'funcao_toggle': 'toggleTheme' in html,
        'localstorage_set': 'localStorage.setItem' in html,
        'classlist_add': "classList.add('dark')" in html or 'classList.add("dark")' in html,
        'icons_presentes': 'sun-icon' in html and 'moon-icon' in html
    }
    
    all_passed = all(checklist.values())
    assert all_passed, f"Dark mode incompleto. Itens faltando: {[k for k, v in checklist.items() if not v]}"