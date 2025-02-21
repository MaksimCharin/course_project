from unittest.mock import Mock, patch

from src.utils import get_currency_rates, get_stock_info, get_stock_prices


def test_get_currency_rates() -> None:
    with patch("requests.get") as mock_get:
        # Мок ответа от API
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"conversion_rates": {"EUR": 0.85, "JPY": 110.0, "GBP": 0.75}}
        mock_get.return_value = mock_response

        # Входные данные
        currencies = ["EUR", "JPY", "GBP"]

        # Ожидаемые значения с учетом преобразования и округления
        expected_rates = {
            "EUR": round(1 / 0.85, 2),  # 1.18
            "JPY": round(1 / 110.0, 2),  # 0.01
            "GBP": round(1 / 0.75, 2),  # 1.33
        }

        # Вызов функции и проверка результата
        result = get_currency_rates(currencies)
        assert result == expected_rates


def test_get_stock_info() -> None:
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"symbol": "AAPL", "name": "Apple Inc.", "price": 150.0}]
        mock_get.return_value = mock_response

        symbol = "AAPL"
        expected_info = {"symbol": "AAPL", "name": "Apple Inc.", "price": 150.0}
        assert get_stock_info(symbol) == expected_info


def test_get_stock_prices() -> None:
    with patch("requests.get") as mock_get:
        mock_response_search = Mock()
        mock_response_search.status_code = 200
        mock_response_search.json.return_value = [{"symbol": "AAPL"}]

        mock_response_price = Mock()
        mock_response_price.status_code = 200
        mock_response_price.json.return_value = [{"price": 150.0}]

        mock_get.side_effect = [mock_response_search, mock_response_price]

        stocks = ["AAPL"]
        expected_prices = {"AAPL": 150.0}
        assert get_stock_prices(stocks) == expected_prices
