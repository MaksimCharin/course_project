import re
from typing import Any

import pandas as pd


def find_transactions_with_phone_numbers(file_path: str) -> Any:
    """Поиск и фильтрация транзакций, содержащих в описании мобильные номера"""
    df = pd.read_excel(file_path)

    phone_pattern = re.compile(r"\+7\s?\d{3}\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}")

    filtered_transactions = df[df["Описание"].astype(str).str.contains(phone_pattern, na=False)]

    result_json = filtered_transactions.to_json(orient="records", force_ascii=False, indent=4)

    return result_json


if __name__ == "__main__":
    file_path = "../data/operations.xlsx"
    result = find_transactions_with_phone_numbers(file_path)
    print(result)
