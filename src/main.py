from src.views import generate_report, get_greeting


def main() -> None:
    """Запуск приложения"""
    print(get_greeting())
    print(generate_report(date_str))


if __name__ == "__main__":
    date_str = "2021-12-31 16:44:00"
    main()
