import json
from datetime import datetime

import pandas as pd

from src.utils import get_currency_rates, get_stock_prices


def get_greeting():
    current_time = datetime.now().time()
    if 5 <= current_time.hour < 12:
        return "Доброе утро"
    elif 12 <= current_time.hour < 18:
        return "Добрый день"
    elif 18 <= current_time.hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


# Функция для получения данных о расходах по каждой карте
def get_spending_data(transactions, end_date):
    start_date = end_date.replace(day=1)
    print(f"Filtering transactions from {start_date} to {end_date}")

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    card_data = {}

    filtered_transactions.loc[:, "Номер карты"] = filtered_transactions[
        "Номер карты"
    ].astype(str)

    for card_number in filtered_transactions["Номер карты"].unique():
        card_transactions = filtered_transactions[
            filtered_transactions["Номер карты"] == card_number
        ]

        total_spent = card_transactions["Сумма платежа"].sum()
        cashback = total_spent // 100  # 1 рубль на каждые 100 рублей

        top_transactions = card_transactions.nlargest(5, "Сумма платежа")

        card_data[card_number] = {
            "last_4_digits": card_number[-4:],
            "total_spent": total_spent,
            "cashback": cashback,
            "top_transactions": top_transactions[
                ["Дата операции", "Категория", "Сумма платежа"]
            ].to_dict(orient="records"),
        }

    return card_data


# Главная функция для генерации JSON-ответа
def generate_report(date_str):
    end_date = pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")

    # Загрузка данных транзакций из Excel
    try:
        transactions = pd.read_excel("../data/operations.xlsx")
        transactions["Дата операции"] = pd.to_datetime(
            transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", dayfirst=True
        )
        transactions["Дата платежа"] = pd.to_datetime(
            transactions["Дата платежа"], format="%d.%m.%Y", dayfirst=True
        )
    except FileNotFoundError:
        return json.dumps(
            {"error": "Файл с данными не найден"}, ensure_ascii=False, indent=4
        )

    spending_data = get_spending_data(transactions, end_date)

    # Чтение пользовательских настроек
    try:
        with open("../user_settings.json", "r", encoding="utf-8") as file:
            user_settings = json.load(file)
    except FileNotFoundError:
        return json.dumps(
            {"error": "Файл настроек не найден"}, ensure_ascii=False, indent=4
        )

    # Получаем курсы валют и стоимость акций
    currency_rates = get_currency_rates(user_settings.get("user_currencies", []))
    stock_prices = get_stock_prices(user_settings.get("user_stocks", []))

    for card in spending_data:
        for transaction in spending_data[card]["top_transactions"]:
            transaction["Дата операции"] = transaction["Дата операции"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    response = {
        "greeting": get_greeting(),
        "spending_data": spending_data,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    return json.dumps(response, ensure_ascii=False, indent=4)


date_str = "2021-12-31 16:44:00"
response = generate_report(date_str)
print(response)
