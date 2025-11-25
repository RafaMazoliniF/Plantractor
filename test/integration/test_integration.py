import pytest
import requests

# URLs dos serviços (localhost pois rodará na VM do GitHub Actions ou na sua máquina)
URL_WEB = "http://localhost:5000"
URL_DB = "http://localhost:5001"
URL_PROXY = "http://localhost:80"

def test_web_service_status_code():
    """Verifica se o container WEB (Flask) está rodando e responde na porta 5000."""
    try:
        response = requests.get(f"{URL_WEB}/")
        assert response.status_code == 200
        assert "PlanTractor" in response.text
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container WEB (porta 5000)")

def test_database_api_query():
    """Verifica se o container DATABASE (API Flask+SQLite) responde a queries JSON."""
    payload = {
        "query": "SELECT 1"
    }
    try:
        response = requests.post(f"{URL_DB}/query", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container DATABASE (porta 5001)")

def test_proxy_nginx_routing():
    """Verifica se o NGINX está roteando corretamente para o WEB (porta 80 -> 5000)."""
    try:
        response = requests.get(f"{URL_PROXY}/")
        assert response.status_code == 200
        # Se o Nginx estiver funcionando, ele deve entregar o mesmo conteúdo do Web
        assert "PlanTractor" in response.text
        # Confirma que é o Nginx respondendo (header Server geralmente indica)
        assert "nginx" in response.headers.get("Server", "").lower() or response.ok
    except requests.exceptions.ConnectionError:
        pytest.fail("Falha ao conectar no container PROXY (porta 80)")