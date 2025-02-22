from unittest.mock import patch, MagicMock

def test_main_page_default_date() -> None:
    with patch("builtins.input", side_effect=["1", ""]):  # Пользователь выбирает команду 1 и использует дату по умолчанию
        with patch("src.views.generate_report", return_value="{}") as mock_generate_report:
            from src.main import main  # Замените `your_module` на имя вашего модуля
            main()
            mock_generate_report.assert_called_once_with("2021-12-31 00:00:00")  # Проверка вызова с датой по умолчанию


def test_report_invalid_date() -> None:
    with patch("builtins.input", side_effect=["3", "Переводы", "31-12-2021"]):  # Пользователь вводит некорректную дату
        with patch("builtins.print") as mock_print:
            from src.main import main
            main()
            mock_print.assert_any_call("Ошибка: Некорректный формат даты. Пожалуйста, используйте формат 'ДД.ММ.ГГГГ'.")

def test_invalid_command() -> None:
    with patch("builtins.input", side_effect=["invalid_command"]):  # Пользователь вводит неверную команду
        with patch("builtins.print") as mock_print:
            from src.main import main
            main()
            mock_print.assert_any_call("Ошибка: Неверная команда. Пожалуйста, введите 1, 2 или 3.")
