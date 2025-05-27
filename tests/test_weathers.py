import pytest
from unittest.mock import patch, AsyncMock

from services.weather_service import geocode_city, get_weather, format_weather_data


@pytest.mark.asyncio
async def test_geocode_city_not_found():
    """Тест геокодирования несуществующего города."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"results": []}

    with patch("services.weather_service.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        result = await geocode_city("НесуществующийГород")

    assert result is None


def test_format_weather_data():
    """Тест форматирования данных о погоде."""
    weather_data = {
        "current": {
            "temperature_2m": 20.5,
            "weather_code": 0
        },
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [19.8, 19.2],
            "precipitation_probability": [0, 10],
            "weather_code": [0, 1]
        }
    }

    result = format_weather_data(weather_data, "Москва")

    assert result["city"] == "Москва"
    assert result["current"] == weather_data["current"]
    assert result["hourly"] == [
        ("2023-01-01T00:00", 19.8, 0, 0),
        ("2023-01-01T01:00", 19.2, 10, 1)
    ]
