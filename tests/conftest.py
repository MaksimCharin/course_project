from typing import Iterator
import pytest
from unittest.mock import patch

import pandas as pd

# Фикстура для мока pd.read_excel
@pytest.fixture
def mock_read_excel() -> Iterator:
    with patch("pandas.read_excel") as mock:
        yield mock


# Фикстура для мока данных транзакций
@pytest.fixture
def mock_transactions_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата операции": [
                "01.10.2023 12:00:00",
                "15.10.2023 14:00:00",
                "30.10.2023 16:00:00",
            ],
            "Категория": ["Переводы", "Переводы", "Покупки"],
            "Сумма": [100, 200, 300],
        }
    )

@pytest.fixture
def transactions() -> pd.DataFrame:
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
def user_settings() -> dict:
    return {"user_currencies": ["EUR", "JPY"], "user_stocks": ["AAPL"]}
# Фикстура для мока данных без транзакций
@pytest.fixture
def mock_no_transactions_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Дата операции": ["01.10.2023 12:00:00", "15.10.2023 14:00:00"],
            "Категория": ["Покупки", "Покупки"],
            "Сумма": [100, 200],
        }
    )