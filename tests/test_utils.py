from unittest.mock import patch

import pytest

from src.utils import ApiConnect, Vacancy


@pytest.mark.parametrize
def vacancies():
    return {
        "items": [
            {"title": "Адвокат", "salary": 120000, "description": "Юриспруденция"},
            {"title": "Няня", "salary": 40000, "description": "Уход за ребёнком"},
        ]
    }


@pytest.mark.parametrize
def no_salary_vacancies():
    return {
        "items": [
            {"title": "Адвокат", "salary": None, "description": "Юриспруденция"},
            {"title": "Няня", "salary": None, "description": "Уход за ребёнком"},
        ]
    }


@pytest.mark.parametrize
def vacancy_1():
    vacancy_1 = Vacancy(
        "Менеджер по развитию бизнеса",
        "https://api.hh.ru/vacancies/102753188?host=hh.ru",
        180000,
        None,
        "Москва",
        "2024-06-26",
        "Поиск и привлечение потенциальных клиентов. Презентация наших услуг."
        " Формирование воронки продаж. Подготовка коммерческих предложений и заключение договоров."
        " Укрепление и развитие...",
    )
    return vacancy_1


@pytest.mark.parametrize
def vacancy_2():
    vacancy_2 = Vacancy(
        "Менеджер по развитию малюсенького бизнеса",
        "https://api.hh.ru/vacancies/102753188?host=hh.ru",
        1000,
        None,
        "Москва",
        "2024-06-26",
        "Поиск и привлечение потенциальных клиентов. Презентация наших услуг."
        " Формирование воронки продаж. Подготовка коммерческих предложений и заключение договоров."
        " Укрепление и развитие...",
    )
    return vacancy_2


@patch("requests.get")
def test_api_connect(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = vacancies()
    api_obj = ApiConnect()
    assert api_obj.parsing(0) == [
        {"description": "Юриспруденция", "salary": 120000, "title": "Адвокат"},
        {"description": "Уход за ребёнком", "salary": 40000, "title": "Няня"},
    ]


@patch("requests.get")
def test_api_connect_empty_list(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = no_salary_vacancies()
    api_obj = ApiConnect()
    assert api_obj.parsing(0) == []


@patch("requests.get")
def test_api_connection_error(mock_get):
    mock_get.return_value.status_code = 400
    api_obj = ApiConnect()
    assert api_obj.parsing(5) == []


def test_vacancy():
    assert vacancy_1().title == "Менеджер по развитию бизнеса"
    assert vacancy_1().description == (
        "Поиск и привлечение потенциальных клиентов. Презентация наших услуг. "
        "Формирование воронки продаж. Подготовка коммерческих предложений"
        " и заключение договоров. Укрепление и развитие..."
    )
    assert vacancy_1().url == "https://api.hh.ru/vacancies/102753188?host=hh.ru"
    assert vacancy_1().salary_from == 180000
    assert vacancy_1().salary_to is None
    assert vacancy_1().area == "Москва"
    assert vacancy_1().date == "2024-06-26"

    assert str(vacancy_1()) == (
        "Название - Менеджер по развитию бизнеса,\n"
        'Описание - "Поиск и привлечение потенциальных клиентов. Презентация наших '
        "услуг. Формирование воронки продаж. Подготовка коммерческих предложений и "
        'заключение договоров. Укрепление и развитие...",\n'
        "Зарплата от 180000,\n"
        "Регион - Москва,\n"
        "Дата публикации - 2024-06-26,\n"
        'Ссылка: "https://api.hh.ru/vacancies/102753188?host=hh.ru".\n'
    )


def test_compare_vacancies():
    assert vacancy_1().compare_to(vacancy_2()) == (
        'Вакансия "Менеджер по развитию бизнеса" более оплачиваемая чем'
        ' "Менеджер по развитию малюсенького бизнеса".'
    )
