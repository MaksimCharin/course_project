import json
from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest

from src.views import generate_report, get_greeting, get_spending_data


@pytest.fixture
def transactions():
    # Фикстура для создания DataFrame с транзакциями
    data = {
        "Дата операции": [
            "2023-10-01 10:00:00",
            "2023-10-02 12:00:00",
            "2023-10-03 14:00:00",
        ],
        "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654"],
        "Категория": ["Еда", "Транспорт", "Еда"],
        "Сумма платежа": [1500, 2000, 3000],
    }
    df = pd.DataFrame(data)
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], format="%Y-%m-%d %H:%M:%S")
    return df


@pytest.fixture
def user_settings():
    # Фикстура для создания пользовательских настроек
    return {"user_currencies": ["EUR", "JPY"], "user_stocks": ["AAPL"]}


# @pytest.mark.parametrize("expected_greeting", [
#     ("Доброе утро", lambda t: 5 <= t.hour < 12),
#     ("Добрый день", lambda t: 12 <= t.hour < 18),
#     ("Добрый вечер", lambda t: 18 <= t.hour < 23),
#     ("Доброй ночи", lambda t: t.hour < 5 or t.hour >= 23)
# ])
# def test_get_greeting(expected_greeting):
#     greeting, condition = expected_greeting
#     current_time = datetime.now().time()
#     if condition(current_time):
#         assert get_greeting() == greeting


def test_get_greeting():
    current_time = datetime.now().time()
    greeting = get_greeting()

    if 5 <= current_time.hour < 12:
        expected_greeting = "Доброе утро"
    elif 12 <= current_time.hour < 18:
        expected_greeting = "Добрый день"
    elif 18 <= current_time.hour < 23:
        expected_greeting = "Добрый вечер"
    else:
        expected_greeting = "Доброй ночи"

    assert greeting == expected_greeting, f"Expected greeting to be '{expected_greeting}', but got '{greeting}'"


def test_get_spending_data(transactions):
    end_date = datetime(2023, 10, 31)
    expected_data = {
        "1234567890123456": {
            "last_4_digits": "3456",
            "total_spent": 3500,
            "cashback": 35,
            "top_transactions": [
                {
                    "Дата операции": "2023-10-02 12:00:00",
                    "Категория": "Транспорт",
                    "Сумма платежа": 2000,
                },
                {
                    "Дата операции": "2023-10-01 10:00:00",
                    "Категория": "Еда",
                    "Сумма платежа": 1500,
                },
            ],
        },
        "9876543210987654": {
            "last_4_digits": "7654",
            "total_spent": 3000,
            "cashback": 30,
            "top_transactions": [
                {
                    "Дата операции": "2023-10-03 14:00:00",
                    "Категория": "Еда",
                    "Сумма платежа": 3000,
                }
            ],
        },
    }

    result = get_spending_data(transactions, end_date)

    for card in expected_data:
        assert result[card]["last_4_digits"] == expected_data[card]["last_4_digits"]
        assert result[card]["total_spent"] == expected_data[card]["total_spent"]
        assert result[card]["cashback"] == expected_data[card]["cashback"]
        assert len(result[card]["top_transactions"]) == len(expected_data[card]["top_transactions"])


# Тест успешного выполнения функции
@patch("pandas.read_excel")
@patch("builtins.open")
@patch("src.views.get_spending_data")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.get_greeting")
def test_generate_report_success(
    mock_greeting,
    mock_stock_prices,
    mock_currency_rates,
    mock_spending_data,
    mock_open,
    mock_read_excel,
):
    # Пример возвращаемых значений
    mock_greeting.return_value = "Hello!"
    mock_spending_data.return_value = {
        "card1": {"top_transactions": [{"Дата операции": pd.to_datetime("2022-01-01 10:00:00"), "amount": 100}]}
    }
    mock_currency_rates.return_value = {"USD": 75.0}
    mock_stock_prices.return_value = {"AAPL": 150.0}

    # Мокаем чтение Excel файла
    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
        }
    )

    # Мокаем открытие пользовательских настроек
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )

    # Вызов функции
    result = generate_report("2022-01-01 10:00:00")

    # Проверка правильности результата
    result_json = json.loads(result)

    assert result_json["greeting"] == "Hello!"
    assert "spending_data" in result_json
    assert "currency_rates" in result_json
    assert "stock_prices" in result_json
    assert result_json["currency_rates"] == {"USD": 75.0}
    assert result_json["stock_prices"] == {"AAPL": 150.0}


# Тест на ошибку, если не найден файл с данными
@patch("pandas.read_excel")
@patch("builtins.open")
def test_generate_report_file_not_found_error(mock_open, mock_read_excel):
    # Мокаем ошибку при загрузке файла Excel
    mock_read_excel.side_effect = FileNotFoundError

    # Мокаем открытие пользовательских настроек
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )

    # Вызов функции
    result = generate_report("2022-01-01 10:00:00")

    # Проверка ошибки
    result_json = json.loads(result)
    assert result_json == {"error": "Файл с данными не найден"}


# Тест на ошибку, если не найден файл настроек
@patch("pandas.read_excel")
@patch("builtins.open")
def test_generate_report_user_settings_not_found(mock_open, mock_read_excel):
    # Мокаем ошибку при загрузке файла настроек
    mock_open.side_effect = FileNotFoundError

    # Мокаем загрузку данных из Excel с добавлением нужных столбцов
    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
            "Номер карты": ["1234567890123456"],
            "Сумма платежа": [100],  # Добавляем нужный столбец
            "Категория": ["Супермаркеты"],  # Добавляем столбец 'Категория'
        }
    )

    # Вызов функции
    result = generate_report("2022-01-01 10:00:00")

    # Проверка результата
    result_json = json.loads(result)

    # Ожидаем, что результат будет содержать ошибку о файле настроек
    assert result_json == {"error": "Файл настроек не найден"}


@patch("pandas.read_excel")
@patch("builtins.open")
@patch("src.views.get_spending_data")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.get_greeting")
def test_generate_report_invalid_date_format(
    mock_greeting,
    mock_stock_prices,
    mock_currency_rates,
    mock_spending_data,
    mock_open,
    mock_read_excel,
):
    # Мокаем успешную работу всех функций
    mock_greeting.return_value = "Hello!"
    mock_spending_data.return_value = {
        "card1": {"top_transactions": [{"Дата операции": pd.to_datetime("2022-01-01 10:00:00"), "amount": 100}]}
    }
    mock_currency_rates.return_value = {"USD": 75.0}
    mock_stock_prices.return_value = {"AAPL": 150.0}

    # Мокаем чтение Excel файла
    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
            "Номер карты": ["1234567890123456"],
            "Сумма платежа": [100],  # Добавляем нужный столбец
        }
    )

    # Мокаем открытие пользовательских настроек
    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )
