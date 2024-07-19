import os

from src.utils import VacanciesDataBase, Vacancy


def main():
    print(
        "Здравствуйте! Введите критерии для поиска вакансии. Чтобы пропустить критерий, нажмите ENTER"
    )
    title = input("Название вакансии или желаемая должность:\n")
    if title == "":
        title = None
    salary = input("Размер желаемой зарплаты:\n")
    if salary == "":
        salary = None
    else:
        salary = int(salary)
    area = input("Регион:\n")
    if area == "":
        area = None
    keyword = input("Поиск по определённому слову в описании:\n")
    if keyword == "":
        keyword = None
    top = input("Топ вакансий для просмотра (кол-во):\n")
    if top == "":
        top = 10
    else:
        top = int(top)

    vacancies = Vacancy.json_format(pages_quantity=5, keyword=title)

    writer = VacanciesDataBase("vacancies.json")

    for vacancy in vacancies:
        writer.write(vacancy)

    writer.write(
        {
            "title": "Самая крутая вакансия",
            "description": "нифига не делать",
            "salary_from": 10000000000000000,
            "salary_to": None,
            "area": "Рай",
            "date": "2100-01-09",
            "url": "https://www.friv.com",
        }
    )

    filtered_vacancies = writer.get(keyword=keyword, salary=salary, area=area)

    filtered_writer = VacanciesDataBase("filtered_vacancies.json")

    if len(filtered_vacancies) > 0:
        for vacancy in filtered_vacancies:
            filtered_writer.write(vacancy)
    else:
        print("По Вашему запросу не найдено ни одной вакансии")

    result = filtered_writer.top_vacancies(top)

    for vacancy in result:
        vacancy = Vacancy.new_vacancy_from_json(vacancy)
        print(vacancy)

    os.remove("../data/filtered_vacancies.json")
