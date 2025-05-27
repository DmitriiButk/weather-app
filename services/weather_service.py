import httpx
from typing import Dict, List, Tuple, Optional, Any, Union
from urllib.parse import quote


async def geocode_city(city: str) -> Optional[Dict[str, Any]]:
    """
    Получает географические координаты города по его названию.

    Args:
        city: Название города для геокодирования

    Returns:
        Dict[str, Any]: Словарь с данными о местоположении города (широта, долгота и др.)
        или None, если город не найден или произошла ошибка
    """
    encoded_city = quote(city)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1&language=ru"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    return data["results"][0]
                else:
                    print(f"Город '{city}' не найден в API. Ответ: {data}")
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
        print(f"Ошибка при подключении к API геокодирования: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при геокодировании: {e}")

    return None


async def get_weather(lat: float, lon: float) -> Optional[Dict[str, Any]]:
    """
    Получает данные о погоде по географическим координатам.

    Args:
        lat: Широта местоположения
        lon: Долгота местоположения

    Returns:
        Dict[str, Any]: Словарь с данными о погоде или None в случае ошибки
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code&hourly=temperature_2m,precipitation_probability,weather_code&forecast_days=1"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
    except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as e:
        print(f"Ошибка при подключении к API погоды: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при получении погоды: {e}")

    return None


def format_weather_data(weather_data: Dict[str, Any], city: str) -> Dict[str, Any]:
    """
    Форматирует данные о погоде для отображения в интерфейсе.

    Args:
        weather_data: Оригинальные данные о погоде, полученные от API
        city: Название города, для которого получены данные

    Returns:
        Dict[str, Any]: Словарь с форматированными данными, содержащий:
            - city: название города
            - current: текущие погодные условия
            - hourly: почасовой прогноз в формате списка кортежей
              (время, температура, вероятность осадков, код погоды)
    """
    return {
        'city': city,
        'current': weather_data['current'],
        'hourly': list(zip(
            weather_data['hourly']['time'][:24],
            weather_data['hourly']['temperature_2m'][:24],
            weather_data['hourly']['precipitation_probability'][:24],
            weather_data['hourly']['weather_code'][:24]
        ))
    }
