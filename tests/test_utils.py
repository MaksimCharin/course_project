from unittest.mock import patch, Mock

from src.utils import get_currency_rates, get_stock_info, get_stock_prices

def test_get_currency_rates():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'conversion_rates': {
                'EUR': 0.85,
                'JPY': 110.0,
                'GBP': 0.75
            }
        }
        mock_get.return_value = mock_response

        currencies = ['EUR', 'JPY', 'GBP']
        expected_rates = {'EUR': 0.85, 'JPY': 110.0, 'GBP': 0.75}
        assert get_currency_rates(currencies) == expected_rates

def test_get_stock_info():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.0}
        ]
        mock_get.return_value = mock_response

        symbol = 'AAPL'
        expected_info = {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.0}
        assert get_stock_info(symbol) == expected_info

def test_get_stock_prices():
    with patch('requests.get') as mock_get:
        mock_response_search = Mock()
        mock_response_search.status_code = 200
        mock_response_search.json.return_value = [
            {'symbol': 'AAPL'}
        ]

        mock_response_price = Mock()
        mock_response_price.status_code = 200
        mock_response_price.json.return_value = [
            {'price': 150.0}
        ]

        mock_get.side_effect = [mock_response_search, mock_response_price]

        stocks = ['AAPL']
        expected_prices = {'AAPL': 150.0}
        assert get_stock_prices(stocks) == expected_prices

if __name__ == '__main__':
    test_get_currency_rates()
    test_get_stock_info()
    test_get_stock_prices()
    print("Все тесты пройдены успешно!")
