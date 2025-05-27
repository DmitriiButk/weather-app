import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app


@pytest.fixture
def client():
    """Фикстура для создания тестового клиента."""
    with TestClient(app) as client:
        yield client


@pytest.mark.asyncio
async def test_home_route(client):
    """Тест доступности главной страницы."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.fixture
def mock_get_cities():
    """Мок для функции получения списка городов."""
    with patch("routes.routes.get_cities_autocomplete", return_value=["Москва", "Санкт-Петербург", "Казань"]) as mock:
        yield mock


def test_cities_api(client, mock_get_cities):
    """Тест API для автокомплита городов."""
    response = client.get("/api/cities?q=моск")
    assert response.status_code == 200
    assert response.json() == ["Москва", "Санкт-Петербург", "Казань"]
    mock_get_cities.assert_called_once_with("моск")


@pytest.fixture
def mock_city_stats():
    """Мок для функции статистики городов."""
    stats = [{"city": "Москва", "count": 10}, {"city": "Санкт-Петербург", "count": 5}]
    with patch("routes.routes.get_cities_stats", return_value=stats) as mock:
        yield mock


def test_stats_api(client, mock_city_stats):
    """Тест API для статистики городов."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    assert response.json() == [{"city": "Москва", "count": 10}, {"city": "Санкт-Петербург", "count": 5}]
    mock_city_stats.assert_called_once()
