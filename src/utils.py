import json
import os
from abc import ABC, abstractmethod

import requests


class Parser(ABC):
    """Абстрактынй класс определеяющий методы класса ApiConnect"""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def parsing(self, keyword, pages):
        pass


class ApiConnect(Parser):
    """Класс осуществляющий подключение к стороннему API сайта HH.ru
    и получающий от API информацию о вакансиях"""

    def __init__(self):
        self.url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies_list = []
        self.filtered_vacancies = []

    def parsing(self, pages, keyword=""):
        """Метод для получения информаици о вакансиях при помощи API HH.ru"""
        self.params["text"] = keyword
        while self.params.get("page") != pages + 1:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            if response.status_code != 200:
                print(
                    f"Проблема с подключением к стороннему API. Код: {response.status_code}"
                )
                return []
            vacancies = response.json()["items"]
            self.vacancies_list.extend(vacancies)
            self.params["page"] += 1
        for vacancy in self.vacancies_list:
            if vacancy["salary"] is not None:
                self.filtered_vacancies.append(vacancy)
        return self.filtered_vacancies


class Vacancy:
    """Класс определяющий информацию о вакансии"""

    title: str
    url: str
    salary_from: (bool, float)
    salary_to: (bool, float)
    currency: str
    area: str
    date: str
    description: str

    def __init__(self, title, url, salary_from, salary_to, area, date, description):
        self.title = title
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.area = area
        self.date = date
        self.description = description

    def __str__(self):
        """Метод для отображения информации о вакансии"""

        if self.salary_from is None:
            return (
                f"Название - {self.title},\n"
                f'Описание - "{self.description}",\n'
                f"Зарплата до {self.salary_to},\n"
                f"Регион - {self.area},\n"
                f"Дата публикации - {self.date},\n"
                f'Ссылка: "{self.url}".\n'
            )

        elif self.salary_to is None:
            return (
                f"Название - {self.title},\n"
                f'Описание - "{self.description}",\n'
                f"Зарплата от {self.salary_from},\n"
                f"Регион - {self.area},\n"
                f"Дата публикации - {self.date},\n"
                f'Ссылка: "{self.url}".\n'
            )
        else:
            return (
                f"Название - {self.title},\n"
                f'Описание - "{self.description}",\n'
                f"Зарплата от {self.salary_from} - до {self.salary_to},\n"
                f"Регион - {self.area},\n"
                f"Дата публикации - {self.date},\n"
                f'Ссылка: "{self.url}".\n'
            )

    @staticmethod
    def new_vacancy(vacancy):
        """Метод для создания объекта формата класса Vacancy с указанной зарплатой"""

        if vacancy["salary"] is not None:
            vacancy_obj = Vacancy(
                vacancy["name"],
                vacancy["url"],
                vacancy["salary"]["from"],
                vacancy["salary"]["to"],
                vacancy["area"]["name"],
                vacancy["created_at"][0:10],
                vacancy["snippet"]["responsibility"],
            )
            return vacancy_obj

    @staticmethod
    def new_vacancy_from_json(vacancy):
        vacancy_obj = Vacancy(
            vacancy["title"],
            vacancy["url"],
            vacancy["salary_from"],
            vacancy["salary_to"],
            vacancy["area"],
            vacancy["date"],
            vacancy["description"],
        )
        return vacancy_obj

    def __repr__(self):
        """Метод для отладки информации о вакансии в JSON формате"""

        return {
            "title": self.title,
            "description": self.description,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to,
            "area": self.area,
            "date": self.date,
            "url": self.url,
        }

    @staticmethod
    def json_format(pages_quantity, keyword):
        vacancies_response = ApiConnect()
        vacancies_list = vacancies_response.parsing(
            pages=pages_quantity, keyword=keyword
        )
        objects = []
        for i in vacancies_list:
            vacancy_obj = Vacancy.new_vacancy(i)
            objects.append(vacancy_obj.__repr__())
        return objects

    def compare_to(self, other):
        if isinstance(other, Vacancy):
            if self.salary_from is not None:
                if other.salary_from is not None:
                    if self.salary_from > other.salary_from:
                        return f'Вакансия "{self.title}" более оплачиваемая чем "{other.title}".'
                    elif self.salary_from < other.salary_from:
                        return f'Вакансия "{other.title}" более оплачиваемая чем "{self.title}".'
                    else:
                        return "Данные вакансии одинаково оплачиваемы."
                else:
                    if self.salary_from > other.salary_to:
                        return f'Вакансия "{self.title}" более оплачиваемая чем "{other.title}".'
                    elif self.salary_from < other.salary_to:
                        return f'Вакансия "{other.title}" более оплачиваемая чем "{self.title}".'
                    else:
                        return "Данные вакансии одинаково оплачиваемы."
            else:
                if other.salary_from is not None:
                    if self.salary_to > other.salary_from:
                        return f'Вакансия "{self.title}" более оплачиваемая чем "{other.title}".'
                    elif self.salary_to < other.salary_from:
                        return f'Вакансия "{other.title}" более оплачиваемая чем "{self.title}".'
                    else:
                        return "Данные вакансии одинаково оплачиваемы."
                else:
                    if self.salary_to > other.salary_to:
                        return f'Вакансия "{self.title}" более оплачиваемая чем "{other.title}".'
                    elif self.salary_to < other.salary_to:
                        return f'Вакансия "{other.title}" более оплачиваемая чем "{self.title}".'
                    else:
                        return "Данные вакансии одинаково оплачиваемы."


class FileWriting(ABC):
    """Абстрактный класс определяющий методы класса VacanciesDataBase"""

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def write(self, vacancy):
        pass

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def delete(self, vacancy):
        pass


class VacanciesDataBase(FileWriting):
    """Класс, позволяющий записывать данные о вакансиях в файл, читать данные из файла и удалять данные о вакансиях"""

    def __init__(self, filename):
        self.filename = filename

    def write(self, vacancy):
        """Метод для записи вакансий в JSON файл"""

        path = os.path.abspath(f"../data/{self.filename}")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if vacancy not in data:
                    data.append(vacancy)
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            with open(path, "w", encoding="utf-8") as file:
                some_list = []
                some_list.append(vacancy)
                json.dump(some_list, file, ensure_ascii=False, indent=4)

    def get(self, keyword=None, salary=None, area=None):
        """Метод для поиска вакансий в JSON файле по критериям"""

        filtered_list = []
        path = os.path.abspath(f"../data/{self.filename}")
        with open(path, "r") as file:
            datas = json.load(file)
            for data in datas:
                if data != "None":
                    if keyword:
                        if data["description"] is not None:
                            if (
                                keyword.lower() in data["title"].lower()
                                or keyword.lower() in data["description"].lower()
                            ):
                                if salary:
                                    if data["salary_from"] is not None:
                                        if salary <= data["salary_from"]:
                                            if area:
                                                if area.lower() in data["area"].lower():
                                                    filtered_list.append(data)
                                    else:
                                        if salary <= data["salary_to"]:
                                            if area:
                                                if area.lower() in data["area"].lower():
                                                    filtered_list.append(data)
                                else:
                                    if area:
                                        if area.lower() in data["area"].lower():
                                            filtered_list.append(data)
                                    else:
                                        filtered_list.append(data)
                    else:
                        if salary:
                            if data["salary_from"] is not None:
                                if salary <= data["salary_from"]:
                                    if area:
                                        if area.lower() in data["area"].lower():
                                            filtered_list.append(data)
                                    else:
                                        filtered_list.append(data)
                            else:
                                if salary <= data["salary_to"]:
                                    if area:
                                        if area.lower() in data["area"].lower():
                                            filtered_list.append(data)
                                    else:
                                        filtered_list.append(data)
                        else:
                            if area:
                                if area.lower() in data["area"].lower():
                                    filtered_list.append(data)
                            else:
                                filtered_list.append(data)
        return filtered_list

    def delete(self, vacancy):
        """Метод для удаления вакансии из JSON файла"""

        path = os.path.abspath(f"../data/{self.filename}")
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                data.remove(vacancy)
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            print(f"Файл {self.filename} не найден.")

    def top_vacancies(self, top_quantity):
        path = os.path.abspath(f"../data/{self.filename}")
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            # print(data)
            data = sorted(
                data,
                key=lambda x: (
                    x["salary_from"] if x["salary_from"] is not None else x["salary_to"]
                ),
                reverse=True,
            )
            return data[:top_quantity]


# vacancies_response = ApiConnect()
# vacancies_response.parsing(1)
# data_for_json_file = Vacancy.json_format(1)
# #
# writer = VacanciesDataBase("data.json")

# data = [
#     {
#         'title': 'mama'
#     },
#     {
#         'title': 'papa'
#     }
# ]
# for i in data_for_json_file:
#     writer.write(i)

# result = VacanciesDataBase.get(writer, area='Алматы')
# for i in result:
#     print(i)

# writer.delete({
#         "title": "Диспетчер чатов (в Яндекс)",
#         "description": "Работать с клиентами или партнерами для решения разнообразных ситуаций."
#                        " Совершать звонки по их обращениям и давать письменные ответы. ",
#         "salary_from": 30000,
#         "salary_to": 44000,
#         "area": "Россия",
#         "date": "2024-07-19",
#         "url": "https://api.hh.ru/vacancies/104236464?host=hh.ru"
#     })

# vacancy_1 = Vacancy("Менеджер по развитию бизнеса", "https://api.hh.ru/vacancies/102753188?host=hh.ru",
#                     180000, None, "Москва", "2024-06-26",
#                     "Поиск и привлечение потенциальных клиентов. Презентация наших услуг."
#                     " Формирование воронки продаж. Подготовка коммерческих предложений и заключение договоров."
#                     " Укрепление и развитие...")
# print(vacancy_1.__repr__())
#
# vacancy_2 = Vacancy("Менеджер по развитию малюсенького бизнеса", "https://api.hh.ru/vacancies/102753188?host=hh.ru",
#                     1000, None, "Москва", "2024-06-26",
#                     "Поиск и привлечение потенциальных клиентов. Презентация наших услуг."
#                     " Формирование воронки продаж. Подготовка коммерческих предложений и заключение договоров."
#                     " Укрепление и развитие...")
#
# print(vacancy_1.compare_to(vacancy_2))

# print(writer.top_vacancies(5))
