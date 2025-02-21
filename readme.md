# Курсовой проект: Приложение для анализа банковских операций

## Структура проекта:
```
├── src
│ ├── init.py
│ ├── utils.py
│ ├── views.py
│ ├── reports.py
│ └── services.py
├── logs
├── htmlcov
├── data
│ ├── operations.xlsx
├── tests
│ ├── init.py
│ ├── test_utils.py
│ ├── test_views.py
│ ├── test_reports.py
│ └── test_services.py
├── user_settings.json
├── .venv/
├── .env
├── .env.example
├── .git/
├── .idea/
├── .flake8
├── .gitignore
├── pyproject.toml
├── poetry.lock
└── README.md
```
============================
## Модуль *views.py*
Реализована основная и вспомогательные функции для ответа в формате JSON, следующего содержания:
1. Приветствие в формате "???", где ??? — «Доброе утро» / «Добрый день» / «Добрый вечер» / «Доброй ночи» 
в зависимости от текущего времени.
2. По каждой карте:
- последние 4 цифры карты;
- общая сумма расходов;
- кешбэк (1 рубль на каждые 100 рублей).
3. Топ-5 транзакций по сумме платежа.
4. Курс валют.
5. Стоимость акций из S&P500.

Функция *generate_report* возвращает данную информацию:
```
response = {
        "greeting": get_greeting(),
        "spending_data": spending_data,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }
```
============================
## Модуль *utils.py*
Содержит функции с запросами к API, которые получают данные о курсе валюты и Стоимость акций из S&P500
Данные, необходимые для сбора и обработки информации, берутся из подготовленного файла *user_settings.json*

В модуле присутствуют ключи, необходимые для запроса. С помощью библиотеки *os* и *dotenv* реализовано сокрытие
ключей и подготовлен файл *.env.example* с инструкцией по их получению
```
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY")
SHARES_API_KEY = os.getenv("SHARES_API_KEY")
```
============================
## Модуль *services.py*
В модуле реализована функция с поиском по телефонным номерам. Для этого было сформировано регулярное выражение,
используя библиотеку *re* 

Функция возвращает JSON со всеми транзакциями, содержащими в описании мобильные номера
```
# Регулярное выражение для поиска мобильных номеров
    phone_pattern = re.compile(r"\+7\s?\d{3}\s?\d{3}[\s-]?\d{2}[\s-]?\d{2}")
```
============================
## Модуль *services.py*
В модуле реализована функция, которая генерирует отчет с тратами по категориям.
Функция принимает на вход:
- датафрейм с транзакциями
- название категории
- опциональную дату

Функция возвращает траты по заданной категории за последние три месяца (от переданной даты).
Также реализован декоратор, который записывает в файл результат, формирующая отчет.
============================
## Тесты
Покрытие тестами 90%, что подтверждается отчетом, который размещен в директории *htmlcov\index.html* 
или можно выполнить команду в терминале:

```pytest --cov```

В тестах используются фикстуры и параметризация, а также используется Mock и patch для тестирования функций с API-запросами

============================

