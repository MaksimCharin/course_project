import logging
import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
SHARES_API_KEY = os.getenv("SHARES_API_KEY")

# Создаем директорию для логов, если она не существует
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

currency_rate_logger = logging.getLogger("get_currency_rates")
stock_info_logger = logging.getLogger("get_stock_info")
stock_prices_logger = logging.getLogger("get_stock_prices")
currency_rate_logger.propagate = False
stock_info_logger.propagate = False
stock_prices_logger.propagate = False
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "utils.log"), mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
currency_rate_logger.addHandler(file_handler)
stock_info_logger.addHandler(file_handler)
stock_prices_logger.addHandler(file_handler)


def get_currency_rates(currencies: list) -> dict:
    """Функция для получения курса валют"""
    currency_rate_logger.info("Функция get_currency_rates начала работу.")
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/RUB"

    try:
        response = requests.get(url)
        response.raise_for_status()
        currency_rate_logger.info("Запрос к API выполнен успешно.")
    except requests.RequestException as e:
        currency_rate_logger.error(f"Ошибка при запросе к API: {e}")
        return {}

    # Получение данных о курсах
    rates = response.json().get("conversion_rates", {})

    # Преобразование курсов в формат "1 валюта = X RUB"
    currency_rates: Dict[str, Optional[float]] = {}
    for currency in currencies:
        rate = rates.get(currency)
        if rate is not None:
            currency_rates[currency] = round(1 / rate, 2)
        else:
            currency_rates[currency] = None

    currency_rate_logger.info("Функция get_currency_rates завершила работу.")
    return currency_rates


def get_stock_info(symbol: str) -> dict | None:
    """Функция для получения информации об акциях"""
    stock_info_logger.info("Функция get_stock_info начала работу.")
    search_url = f"https://financialmodelingprep.com/api/v3/search?query={symbol}&apikey={SHARES_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        stock_info_logger.info("Запрос к API выполнен успешно.")
        return data[0] if data else None
    else:
        stock_info_logger.error(f"Ошибка при запросе к API: {response.status_code}")
        return None


def get_stock_prices(stocks: list) -> dict:
    """Функция для получения стоимости акций"""
    stock_prices_logger.info("Функция get_stock_prices начала работу.")
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
                stock_prices_logger.error(f"Ошибка при запросе к API: {response.status_code}")
        else:
            stock_prices_logger.warning(f"Акция {stock} не найдена.")

    stock_prices_logger.info("Функция get_stock_prices завершила работу.")
    return stock_data
