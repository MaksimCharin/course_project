import json
from typing import Iterator
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.reports import report_decorator, spending_by_category


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


# Тест функции spending_by_category
@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category(
    mock_file: MagicMock, mock_read_excel: MagicMock, mock_transactions_data: MagicMock
) -> None:
    """Тест функции spending_by_category."""
    # Настройка мока
    mock_read_excel.return_value = mock_transactions_data

    # Вызов функции
    result = spending_by_category("dummy_path.xlsx", "Переводы", "31.10.2023")

    # Ожидаемый результат
    expected_data = pd.DataFrame(
        {
            "Дата операции": pd.to_datetime(
                ["01.10.2023 12:00:00", "15.10.2023 14:00:00"],
                format="%d.%m.%Y %H:%M:%S",  # Указываем правильный формат
            ),
            "Категория": ["Переводы", "Переводы"],
            "Сумма": [100, 200],
        }
    )

    # Проверка результата
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_data.reset_index(drop=True))


# Тест функции spending_by_category, когда транзакции не найдены
@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_no_transactions(
    mock_file: MagicMock, mock_read_excel: MagicMock, mock_no_transactions_data: MagicMock
) -> None:
    """Тест функции spending_by_category, когда транзакции не найдены."""
    # Настройка мока
    mock_read_excel.return_value = mock_no_transactions_data

    # Вызов функции
    result = spending_by_category("dummy_path.xlsx", "Переводы", "31.10.2023")

    # Проверка результата (пустой DataFrame)
    assert result.empty


def test_report_decorator() -> None:
    mock_func = MagicMock()
    mock_func.__name__ = "mock_func"
    mock_func.return_value = pd.DataFrame({"date": [pd.Timestamp("2023-01-01")], "value": [42]})

    decorated_func = report_decorator("test_report")(mock_func)

    with patch("builtins.open", new_callable=mock_open) as mock_open_file:
        with patch("logging.Logger.info") as mock_logger_info:
            # Вызываем декорированную функцию
            result = decorated_func()

            mock_open_file.assert_called_once_with("../logs/mock_func_report.json", "w", encoding="utf-8")

            mock_logger_info.assert_called_once_with("Отчет сохранен в файл: ../logs/mock_func_report.json")

            pd.testing.assert_frame_equal(result, mock_func.return_value)

            expected_json = json.dumps(
                [{"date": "2023-01-01T00:00:00", "value": 42}],
                ensure_ascii=False,
                indent=4,
            )
            actual_writes = "".join([call.args[0] for call in mock_open_file().write.call_args_list])
            assert actual_writes == expected_json
