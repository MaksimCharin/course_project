import logging
import os
import re
from typing import Any

import pandas as pd

# Создаем директорию для логов, если она не существует
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Настройка логирования
logger = logging.getLogger("find_transactions_with_phone_numbers")
logger.propagate = False  # Отключаем передачу сообщений корневому логгеру

file_handler = logging.FileHandler(os.path.join(LOG_DIR, "services.log"), mode="w", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


def find_transactions_with_phone_numbers(file_path: str) -> Any:
    """Поиск и фильтрация транзакций, содержащих в описании мобильные номера"""
    logger.info("Функция find_transactions_with_phone_numbers начала работу.")
    logger.info(f"Чтение файла: {file_path}")

    try:
        df = pd.read_excel(file_path)
        logger.info("Файл успешно прочитан.")
    except Exception as e:
        logger.error(f"Ошибка при чтении файла: {e}")
        return None

    phone_pattern = re.compile(r"\+7\s?\d{3}\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}")

    logger.info("Поиск транзакций с номерами телефонов...")
    filtered_transactions = df[df["Описание"].astype(str).str.contains(phone_pattern, na=False)]

    if filtered_transactions.empty:
        logger.warning("Транзакции с номерами телефонов не найдены.")
    else:
        logger.info(f"Найдено {len(filtered_transactions)} транзакций с номерами телефонов.")

    result_json = filtered_transactions.to_json(orient="records", force_ascii=False, indent=4)
    logger.info("Функция find_transactions_with_phone_numbers завершила работу.")

    return result_json


if __name__ == "__main__":
    file_path = "../data/operations.xlsx"
    result = find_transactions_with_phone_numbers(file_path)
    print(result)
