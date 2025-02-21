import requests

CURRENCY_API_KEY = 'fd11eced8340189135fadf71'
SHARES_API_KEY = "KnZqR7BPQ9kJcat46VTLyuamz1xCGNvW"

# Функция для получения курса валют
def get_currency_rates(currencies):
    url = f"https://v6.exchangerate-api.com/v6/{CURRENCY_API_KEY}/latest/USD"
    response = requests.get(url)
    if response.status_code == 200:
        rates = response.json().get('conversion_rates', {})
        return {currency: rates.get(currency) for currency in currencies}
    else:
        return {}

# Функция для получения информации об акциях
def get_stock_info(symbol):
    search_url = f"https://financialmodelingprep.com/api/v3/search?query={symbol}&apikey={SHARES_API_KEY}"
    response = requests.get(search_url)
    if response.status_code == 200:
        data = response.json()
        return data[0] if data else None
    return None

# Функция для получения стоимости акций
def get_stock_prices(stocks):
    stock_data = {}
    for stock in stocks:
        stock_info = get_stock_info(stock)
        if stock_info:
            symbol = stock_info['symbol']
            url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={SHARES_API_KEY}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                stock_data[symbol] = data[0]['price'] if data else None
            else:
                stock_data[symbol] = None
    return stock_data