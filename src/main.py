import time

from src.reports import spending_by_category
from src.services import find_transactions_with_phone_numbers
from src.views import generate_report, get_greeting

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "..", "data", "operations.xlsx")

def main() -> None:
    """
    Запуск приложения для анализа транзакций.

    Пользователь может выбрать одну из команд:
    1. main_page — генерация отчета по дате.
    2. filtered_by_phone — поиск транзакций с номерами телефонов.
    3. report — получение списка трат по категории за три месяца.

    Обрабатывает ошибки ввода и выводит соответствующие сообщения.
    """
    try:
        print(get_greeting())
        print("Доступные команды: 1 - main_page, 2 - filtered_by_phone, 3 - report")
        user_input = input("Введите цифру или название интересующей команды: ").strip().lower()

        if user_input in ("main_page", "1"):
            print("Необходимо ввести дату для формирования отчета.")
            print("Введите дату и время в формате: ГГГГ-ММ-ДД ЧЧ:ММ:СС")
            print("Значение по умолчанию: 2021-12-31 00:00:00")
            user_date = input("Для продолжения введите свою дату или нажмите Enter: ").strip()
            if user_date == "":
                user_date = "2021-12-31 00:00:00"
            try:
                print(generate_report(user_date))
            except ValueError as ve:
                print(f"Ошибка в формате даты: {ve}")

        elif user_input in ("filtered_by_phone", "2"):
            print("Обращение к файлу с данными: data/operations.xlsx")
            time.sleep(2)
            print("Подготовка вывода отфильтрованных данных (операция содержит в описании номер телефона)")
            time.sleep(2)
            try:
                result = find_transactions_with_phone_numbers(FILE_PATH)
                print(result)
            except FileNotFoundError:
                print("Ошибка: Файл с данными не найден.")

        elif user_input in ("report", "3"):
            print("Введите категорию и дату для получения списка трат за три месяца до указанной даты.")
            category = input("Категория: ").strip()
            print("Введите дату в формате 'ДД.ММ.ГГГГ'. Значение по умолчанию: 31.12.2021")
            user_date = input("Для продолжения введите свою дату или нажмите Enter: ").strip()
            if user_date == "":
                user_date = "31.12.2021"
            try:
                time.strptime(user_date, "%d.%m.%Y")
                result = spending_by_category(FILE_PATH, category, user_date)
            except ValueError:
                print("Ошибка: Некорректный формат даты. Пожалуйста, используйте формат 'ДД.ММ.ГГГГ'.")

        else:
            print("Ошибка: Неверная команда. Пожалуйста, введите 1, 2 или 3.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
