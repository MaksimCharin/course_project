import pandas as pd
import json
from unittest.mock import patch

from src.services import find_transactions_with_phone_numbers


def test_find_transactions_with_phone_numbers():
    data = {
        'Описание': [
            'Transaction with phone number +7 123 456-78-90',
            'No phone number here',
            'Another transaction with +71234567890',
            None,
            'Invalid phone number +1 123 456-78-90'
        ]
    }
    df = pd.DataFrame(data)

    with patch('pandas.read_excel', return_value=df) as mock_read_excel:
        expected_result = [
            {'Описание': 'Transaction with phone number +7 123 456-78-90'},
            {'Описание': 'Another transaction with +71234567890'}
        ]

        result_json = find_transactions_with_phone_numbers('dummy_path.xlsx')

        result = json.loads(result_json)

        assert result == expected_result
        mock_read_excel.assert_called_once_with('dummy_path.xlsx')


def test_no_phone_numbers_found():
    data = {
        'Описание': [
            'No phone number here',
            'Another without phone number',
            None
        ]
    }
    df = pd.DataFrame(data)


    with patch('pandas.read_excel', return_value=df) as mock_read_excel:
        result_json = find_transactions_with_phone_numbers('dummy_path.xlsx')

        result = json.loads(result_json)

        assert result == []
        mock_read_excel.assert_called_once_with('dummy_path.xlsx')


def test_empty_dataframe():
    df = pd.DataFrame(columns=['Описание'])

    with patch('pandas.read_excel', return_value=df) as mock_read_excel:
        result_json = find_transactions_with_phone_numbers('dummy_path.xlsx')

        result = json.loads(result_json)

        assert result == []
        mock_read_excel.assert_called_once_with('dummy_path.xlsx')



