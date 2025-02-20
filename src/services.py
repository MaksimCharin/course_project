import pandas as pd
import re

def find_transactions_with_phone_numbers(file_path):
    # Чтение данных из Excel файла с указанием движка
    df = pd.read_excel(file_path)

    # Регулярное выражение для поиска мобильных номеров
    phone_pattern = re.compile(r'\+7\s?\d{3}\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}')

    # Фильтрация транзакций, содержащих мобильные номера в колонке 'Описание'
    filtered_transactions = df[df['Описание'].astype(str).str.contains(phone_pattern, na=False)]

    # Преобразование результата в JSON
    result_json = filtered_transactions.to_json(orient='records', force_ascii=False, indent=4)

    return result_json

if __name__ == '__main__':
    file_path = '../data/operations.xlsx'
    result = find_transactions_with_phone_numbers(file_path)
    print(result)




