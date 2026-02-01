# Разные парсеры

Здесь публикаю свои наработки по парсингу разных сайтов. Делаю потому что интересно.

Чтобы все заработало прежде проделайте это (2 команда для Windows, для линукса погуглите):
```
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
```

1. Парсер сайта [мойкруг](https://career.habr.com/) - moikrug.py
Вакансии выводятся по конкретным парамтрам - python, бекенд-разработчик, миддл. Просто запускаем и любуемся списком вакансий не заходя на сайт.

```
python moikrug.py 
```

Список городов можно посмотреть [тут](https://www.gismeteo.ru/catalog/russia/)

2. Парсер страницы [Gismeteo](https://www.gismeteo.ru/weather-dmitrov-4330)

```
python gismeteo.py Москва
python gismeteo.py Токио
python gismeteo.py другой_город
```

Список городов можно посмотреть [тут](https://www.gismeteo.ru/catalog/russia/)