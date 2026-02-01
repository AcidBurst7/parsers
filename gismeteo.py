import sys
import os
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import lxml


ua = UserAgent(browsers=['Edge', 'Chrome'])


class WeatherForecast:
    def __init__(self, city):
        self.city = city
        self._forecast = {}
        self._domain = "https://www.gismeteo.ru"
        self._url = ""
        self._forecast_url = ""
        self._filename = ""

    def __str__(self):
        return f"Cейчас {self._forecast["weather_now"].lower()}\n" \
                f"Температура сейчас: {self._forecast["temperature_now"]}\n" \
                f"Ощущается как {self._forecast["temperature_feel_now"]}\n\n" \
                f"{self._forecast["astro"]["title"]}\n" \
                f"{'\n'.join(self._forecast["astro"]["sun"]["info"])}\n" \
                f"{self._forecast["astro"]["sun"]["about"]}\n\n" \
                f"{'\n'.join(self._forecast["astro"]["moon"]["info"])}\n" \
                f"{self._forecast["astro"]["moon"]["about"]}\n"

    def get_html(self, source):
        html = ""
        with open(f"{source}", 'r', encoding='utf-8') as file:
            html = file.readlines()
        return '\n'.join(html)
    
    def get_data(self):
        filename = f"{self._forecast_url.split("/")[1]}.html"
        if os.path.isfile(filename) is False:
            html = self.get_request(f"{self._forecast_url}")
            with open(f"{filename}", "w", encoding="utf-8") as file:
                file.writelines(html)
        else:
            today_date = datetime.now()
            timestamp_ctime = os.path.getctime(filename)
            creation_date_time = datetime.fromtimestamp(timestamp_ctime)
            time_difference = today_date - creation_date_time
            
            if time_difference > timedelta(hours=1):
                html = self.get_request(f"{self._forecast_url}")
            else:
                html = self.get_html(filename)
        return html

    def get_request(self, source: str, params: list = [], json: bool = False, save_in_file: bool = False):
        url = f"{self._domain}{source}"
        try:
            headers = {"User-Agent": ua.random}
            response = requests.get(url=url, params=params, headers=headers)
            response.encoding = "utf-8"

            if save_in_file:
                if json is False:
                    filename = f"{url.split("/")[3]}.html"
                    if os.path.exists(filename):
                        os.remove(filename)

                    with open(f"{filename}", "w", encoding="utf-8") as file:
                        file.writelines(response.txt)
            return response.json() if json else response.text
        except requests.exceptions.HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except requests.exceptions.ConnectionError as conn_err:
            print(f'Connection error occurred: {conn_err}')
        except requests.exceptions.Timeout as timeout_err:
            print(f'Timeout error occurred: {timeout_err}')
        except requests.exceptions.RequestException as req_err:
            print(f'An unexpected error occurred: {req_err}')

    def search_place(self) -> None:
        params = {"q": self.city, "geo": "ru", "limit": 10}
        data = self.get_request("/mq/city/q/", params=params, json=True)
        self._forecast_url = f"/weather-{data["data"][0]["slug"]}-{data["data"][0]["id"]}/"

    def get_weather_forecast(self, html: str) -> None:
        soup = BeautifulSoup(html, 'lxml')

        weather_tabs = soup.find('div', class_='weathertabs')
        weather_tabs_links = weather_tabs.find_all('a', class_='weathertab')
        
        self._forecast["weather_now"] = weather_tabs_links[0].get('data-tooltip')

        buf = weather_tabs_links[0].find('div', class_='weather-value').find('temperature-value')
        self._forecast["temperature_now"] = f"{buf.get('value')}{buf.get('from-unit')}"
        
        buf = weather_tabs_links[0].find('div', class_='weather-feel').find('temperature-value')
        self._forecast["temperature_feel_now"] = f"{buf.get('value')}{buf.get('from-unit')}"

        astro = soup.find('div', class_='widget widget-astro')
        astro_sun = astro.find('div', class_='widget-body').find('div', class_='astro-sun')
        astro_moon = astro.find('div', class_='widget-body').find('div', class_='astro-moon')
        self._forecast["astro"] = {
            "title": astro.find('div', class_='widget-title') \
                            .get_text(separator="", strip=True) \
                            .replace('  ', '') \
                            .replace('    ', '') \
                            .replace('    ', '') \
                            .replace('\n\n\n\n', ' '),
            "sun": {
                "info": [
                    item.get_text(separator=" ", strip=True).replace('  ', '').replace('\n', ' ')
                    for item in astro_sun.find('div', class_='astro-times').find_all('div')
                ],
                "about": astro_sun.find('div', class_='astro-bottom') \
                                .get_text(separator="", strip=True) \
                                .replace('  ', '').replace('\n', ' ')
            },
            "moon": {
                "info": [
                    item.get_text(separator=" ", strip=True).replace('  ', '').replace('\n', ' ')
                    for item in astro_moon.find('div', class_='astro-times').find_all('div')
                ],
                "about": astro_moon.find('div', class_='astro-bottom') \
                                .get_text(separator="", strip=True) \
                                .replace('  ', '').replace('\n', ' ')
            }
        }
    
    def process(self) -> None:
        self.search_place()
        html = self.get_data()
        self.get_weather_forecast(html)
        

if __name__ == '__main__':
    weather_forecast = WeatherForecast(sys.argv[1])
    weather_forecast.process()
    print(str(weather_forecast))
