import os
import json
from datetime import datetime, timedelta

from fake_useragent import UserAgent
import requests


ua = UserAgent(browsers=['Edge', 'Chrome'])

class Vacancy:
    def __init__(self):
        self._vacancies = {"list": []}
        self._data = {}
        self._domain = "https://career.habr.com"
        self._url = ""
        self._filename = f"data/vacancies.json"

    def get_file_data(self) -> None:
        with open(f"{self._filename}", "r", encoding="utf-8") as file:
            self._data = json.load(file)

    def get_request(self, save_in_file: bool = False) -> None:
        self._url = "/api/frontend/vacancies"
        headers = {"User-Agent": ua.random}
        params = {
            "sort": "relevance", # обязательно
            "type": "all", # обязательно
            "currency": "RUR", # обязательно
            "qid": 4, # квалификация (4 - мидл)
            "skills[]": 446, # навыки (446 - python)
            "s[]": 2 # id специализации (2- разработка-бекенд)
        }
        try:
            response = requests.get(url=f"{self._domain}{self._url}", params=params, headers=headers)
            response.encoding = "utf-8"
            self._data = response.json()

            if save_in_file:
                filename = f"{self._filename}"
                if os.path.exists(filename):
                    os.remove(filename)
                with open(f"{filename}", "w", encoding="utf-8") as file:
                    json.dump(self._data, file, indent=4)
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Connection error occurred: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            print(f'Timeout error occurred: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            print(f'An unexpected error occurred: {req_err}')

    def get_data(self) -> None:
        if os.path.isfile(self._filename) is False:
            self._data = self.get_request(save_in_file=True)
        else:
            today_date = datetime.now()
            timestamp_ctime = os.path.getctime(self._filename)
            creation_date_time = datetime.fromtimestamp(timestamp_ctime)
            time_difference = today_date - creation_date_time
            
            if time_difference > timedelta(hours=1):
                print("файл не свежий")
                self.get_request(save_in_file=True)
            else:
                print("файл свежий")
                self.get_file_data()

    def process(self) -> None:
        self.get_data()
        for line in self._data["list"]:
            self._vacancies["list"].append({
                "href": f"https://career.habr.com{line["href"]}",
                "title": line["title"],
                "remoteWork": line["remoteWork"],
                "salaryQualification": line["salaryQualification"]["title"],
                "publishedDate": line["publishedDate"]["title"],
                "company_title": line["company"]["title"],
                "employment": line["employment"],
                "salary": {
                    "from": line["salary"]["from"],
                    "to": line["salary"]["to"],
                    "currency": line["salary"]["currency"],
                },
                "predictedSalary": line["predictedSalary"],
                "skills": [item["title"] for item in line["skills"]] if line["skills"] else []
            })   
    
    def show(self) -> None:
        result = ""
        count = 1

        for line in self._vacancies["list"]:
            result += f"{count}) {line['title']} - {line['salaryQualification']} ({line['href']})\n"
            
            if line['salary']['from'] and line['salary']['to']:
                result += f"от {line['salary']['from']} " 
                result += f"до {line['salary']['to']} "
                result += f"({ "руб." if line['salary']['currency'] == "rur" else line['salary']['currency'] })\n"            
            elif line['predictedSalary'] is not None:
                result += f"Примерная зарплата от {line['predictedSalary']['from']} "
                result += f"до {line['predictedSalary']['to']} "
                result += f"({line['predictedSalary']['currency']})\n"

            result += f"Удаленка: "
            result += "да" if line['remoteWork'] else "нет" 
            result += f"\nДата публикации: {line['publishedDate']}"
            result += f"\nКомпания: {line['company_title']}"
            result += f"\nЗанятость: {line['employment'] if line['employment'] else "не указано"}"
            
            result += f"\nНавыки: "
            result += ' | '.join(line['skills'])
            result += "\n====================================================\n"
            count += 1
        result += f"Всего вакансий: {count}\n"
        print(result)


if __name__ == '__main__':
    vacancies = Vacancy()
    vacancies.process()
    vacancies.show()

    