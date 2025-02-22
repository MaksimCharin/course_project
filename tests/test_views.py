import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd

from src.views import generate_report, get_greeting, get_spending_data


def test_get_greeting() -> None:
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


def test_get_spending_data(transactions: pd.DataFrame) -> None:
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


@patch("pandas.read_excel")
@patch("builtins.open")
@patch("src.views.get_spending_data")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.get_greeting")
def test_generate_report_success(
    mock_greeting: MagicMock,
    mock_stock_prices: MagicMock,
    mock_currency_rates: MagicMock,
    mock_spending_data: MagicMock,
    mock_open: MagicMock,
    mock_read_excel: MagicMock,
) -> None:

    mock_greeting.return_value = "Hello!"
    mock_spending_data.return_value = {
        "card1": {"top_transactions": [{"Дата операции": pd.to_datetime("2022-01-01 10:00:00"), "amount": 100}]}
    }
    mock_currency_rates.return_value = {"USD": 75.0}
    mock_stock_prices.return_value = {"AAPL": 150.0}

    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
        }
    )

    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )

    result = generate_report("2022-01-01 10:00:00")

    result_json = json.loads(result)

    assert "spending_data" in result_json
    assert "currency_rates" in result_json
    assert "stock_prices" in result_json
    assert result_json["currency_rates"] == {"USD": 75.0}
    assert result_json["stock_prices"] == {"AAPL": 150.0}


@patch("pandas.read_excel")
@patch("builtins.open")
def test_generate_report_file_not_found_error(mock_open: MagicMock, mock_read_excel: MagicMock) -> None:

    mock_read_excel.side_effect = FileNotFoundError

    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )

    result = generate_report("2022-01-01 10:00:00")

    result_json = json.loads(result)
    assert result_json == {"error": "Файл с данными не найден"}


@patch("pandas.read_excel")
@patch("builtins.open")
def test_generate_report_user_settings_not_found(mock_open: MagicMock, mock_read_excel: MagicMock) -> None:

    mock_open.side_effect = FileNotFoundError

    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
            "Номер карты": ["1234567890123456"],
            "Сумма платежа": [100],
            "Категория": ["Супермаркеты"],
        }
    )

    result = generate_report("2022-01-01 10:00:00")

    result_json = json.loads(result)

    assert result_json == {"error": "Файл настроек не найден"}


@patch("pandas.read_excel")
@patch("builtins.open")
@patch("src.views.get_spending_data")
@patch("src.views.get_currency_rates")
@patch("src.views.get_stock_prices")
@patch("src.views.get_greeting")
def test_generate_report_invalid_date_format(
    mock_greeting: MagicMock,
    mock_stock_prices: MagicMock,
    mock_currency_rates: MagicMock,
    mock_spending_data: MagicMock,
    mock_open: MagicMock,
    mock_read_excel: MagicMock,
) -> None:

    mock_greeting.return_value = "Hello!"
    mock_spending_data.return_value = {
        "card1": {"top_transactions": [{"Дата операции": pd.to_datetime("2022-01-01 10:00:00"), "amount": 100}]}
    }
    mock_currency_rates.return_value = {"USD": 75.0}
    mock_stock_prices.return_value = {"AAPL": 150.0}

    mock_read_excel.return_value = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(["01.01.2022 10:00:00"], format="%d.%m.%Y %H:%M:%S"),
            "Дата платежа": pd.to_datetime(["01.01.2022"], format="%d.%m.%Y"),
            "Номер карты": ["1234567890123456"],
            "Сумма платежа": [100],  # Добавляем нужный столбец
        }
    )

    mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(
        {"user_currencies": ["USD"], "user_stocks": ["AAPL"]}
    )
