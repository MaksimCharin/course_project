import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
SHARES_API_KEY = os.getenv("SHARES_API_KEY")


def get_currency_rates(currencies: list) -> dict:
    """Функция для получения курса валют"""
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/RUB"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на ошибки HTTP
    except requests.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return {}

    # Получение данных о курсах
    rates = response.json().get("conversion_rates", {})

    # Преобразование курсов в формат "1 валюта = X RUB"
    currency_rates: Dict[str, Optional[float]] = {}
    for currency in currencies:
        rate = rates.get(currency)
        if rate is not None:
            currency_rates[currency] = round(1 / rate, 2)  # Преобразуем курс
        else:
            currency_rates[currency] = None  # Если курс не найден

    return currency_rates


def get_stock_info(symbol: str) -> dict | None:
    """Функция для получения информации об акциях"""
    search_url = f"https://financialmodelingprep.com/api/v3/search?query={symbol}&apikey={SHARES_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    return None


def get_stock_prices(stocks: list) -> dict:
    """Функция для получения стоимости акций"""
    stock_data = {}
    for stock in stocks:
        stock_info = get_stock_info(stock)
        if stock_info:
            symbol = stock_info["symbol"]
            url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={SHARES_API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                stock_data[symbol] = data[0]["price"] if data else None
            else:
                stock_data[symbol] = None
    return stock_data
