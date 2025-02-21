import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def report_decorator(filename):
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            report_filename = f"../logs/{func.__name__}_report.json"
            result_dict = result.to_dict(orient="records")
            for record in result_dict:
                for key, value in record.items():
                    if isinstance(value, pd.Timestamp):
                        record[key] = value.isoformat()
            with open(report_filename, "w", encoding="utf-8") as file:
                json.dump(result_dict, file, ensure_ascii=False, indent=4)
            logger.info(f"Отчет сохранен в файл: {report_filename}")
            return result

        return wrapper

    return decorator


@report_decorator("../data/operations.xlsx")
def spending_by_category(
    file_path: str, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    transactions = pd.read_excel(file_path)

    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S"
    )
    # Логи с проверкой нескольких первых строк Датафрейма
    logger.info(f"Первые несколько строк DataFrame:\n{transactions.head()}")

    if date is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date, "%d.%m.%Y")

    start_date = date - timedelta(days=90)

    # Логи даты начала и конца периода
    logger.info(f"Дата начала периода: {start_date}")
    logger.info(f"Дата конца периода: {date}")

    filtered_transactions = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= date)
    ]

    # Логи найденных транзакций
    logger.info(
        f"Найдено {len(filtered_transactions)} транзакций по категории '{category}' за последние три месяца."
    )

    # Если не найдено ни одной транзакции
    if filtered_transactions.empty:
        logger.warning(
            f"Не найдено транзакций по категории '{category}' за последние три месяца."
        )

    sorted_transactions = filtered_transactions.sort_values(by="Дата операции")

    return sorted_transactions


if __name__ == "__main__":
    file_path = "../data/operations.xlsx"
    result = spending_by_category(file_path, "Переводы", "31.12.2021")
    print(result)
