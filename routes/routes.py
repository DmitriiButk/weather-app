import os
from typing import Optional, List, Dict, Any, Union

from fastapi import APIRouter, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import quote, unquote

from services.weather_service import geocode_city, get_weather, format_weather_data
from database.database import save_search, get_user_history, get_cities_autocomplete, get_cities_stats


COOKIE_LAST_CITY_EXPIRES = 30 * 24 * 60 * 60
COOKIE_USER_ID_EXPIRES = 365 * 24 * 60 * 60
TEMPLATE_DIR = "templates"

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/", response_class=HTMLResponse)
async def index(
        request: Request,
        last_city: Optional[str] = Cookie(None)
) -> HTMLResponse:
    """
    Отображает главную страницу приложения.

    Args:
        request: Запрос FastAPI
        last_city: Cookie с последним искомым городом

    Returns:
        HTMLResponse: Отрендеренный шаблон главной страницы
    """
    decoded_city = unquote(last_city) if last_city else None
    return templates.TemplateResponse(
        request,
        "index.html",
        context={"request": request, "last_search": decoded_city}
    )


@router.post("/weather", response_class=HTMLResponse)
async def weather(
        request: Request,
        city: str = Form(...),
        user_id: Optional[str] = Cookie(None)
):
    """
    Обрабатывает запрос на получение прогноза погоды для указанного города.

    Args:
        request: Запрос FastAPI
        city: Название города
        user_id: Идентификатор пользователя из cookie

    Returns:
        HTMLResponse: Страница с прогнозом погоды или сообщение об ошибке
    """
    if not city:
        return RedirectResponse(url="/", status_code=303)

    location = await geocode_city(city)
    if not location:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": f"Город '{city}' не найден"}
        )

    weather_data = await get_weather(location['latitude'], location['longitude'])
    if not weather_data:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Не удалось получить данные о погоде"}
        )

    if not user_id:
        user_id = os.urandom(16).hex()

    save_search(city, location['latitude'], location['longitude'], user_id)
    formatted_data = format_weather_data(weather_data, city)

    response = templates.TemplateResponse(
        "weather.html",
        {"request": request, "weather": formatted_data}
    )

    response.set_cookie(key="last_city", value=quote(city), max_age=COOKIE_LAST_CITY_EXPIRES)
    response.set_cookie(key="user_id", value=user_id, max_age=COOKIE_USER_ID_EXPIRES)

    return response


@router.get("/history", response_class=HTMLResponse)
async def user_history(
        request: Request,
        user_id: Optional[str] = Cookie(None)
):
    """
    Отображает историю поисков пользователя.

    Args:
        request: Запрос FastAPI
        user_id: Идентификатор пользователя из cookie

    Returns:
        HTMLResponse: Страница с историей поисков или редирект на главную
    """
    if not user_id:
        return RedirectResponse(url="/", status_code=303)

    history = get_user_history(user_id)
    return templates.TemplateResponse(
        "history.html",
        {"request": request, "history": history}
    )


@router.get("/error", response_class=HTMLResponse)
async def error_page(
        request: Request,
        message: str = "Произошла ошибка"
) -> HTMLResponse:
    """
    Отображает страницу с сообщением об ошибке.

    Args:
        request: Запрос FastAPI
        message: Сообщение об ошибке для отображения

    Returns:
        HTMLResponse: Страница с сообщением об ошибке
    """
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": message}
    )


@router.get("/api/cities")
async def autocomplete_cities(q: str = "") -> List[str]:
    """
    API-эндпоинт для автозаполнения названий городов.

    Args:
        q: Строка запроса для поиска городов

    Returns:
        List[str]: Список названий городов, соответствующих запросу
    """
    return get_cities_autocomplete(q)


@router.get("/api/stats")
async def city_stats() -> List[Dict[str, Any]]:
    """
    API-эндпоинт для получения статистики поисков по городам.

    Returns:
        List[Dict[str, Any]]: Список словарей со статистикой по городам
    """
    return get_cities_stats()
