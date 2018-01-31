# asyncio_yandex_timetables_crawling

This is the example of asyncio, aiohttp and aiopg usage for Yandex Schedule crawling and parsing. Aim is to search detailed information about all routes departing or arriving to certain stations for some dates range.
## Requirements
The application requires Python 3.6+ and requirements.txt includes all other required packages.
## Yandex Schedule API
The application is written in accordance to Yandex Schedules API v1.0 (API documentation: https://tech.yandex.ru/rasp/doc/concepts/about-docpage).
Each request contains of following arguments:
```
https://api.rasp.yandex.net/v3.0/schedule/ ?
  apikey=<ключ>
& station=<код станции>
& [lang=<язык>]
& [format=<формат>]
& [date=<дата>]
& [transport_types=<тип транспорта>]
& [event=<прибытие или отправление>]
& [system=<система кодирования для параметра station>]
& [show_systems=<коды в ответе>]
& [direction=<направление>]
& [result_timezone=<часовой пояс>]
```
## Usage
Searching parameters should be placed in config.py:
* Yandex Schedules API key should be received. A detailed description is here: <https://tech.yandex.ru/rasp/doc/concepts/access-docpage/>
* BASE_URL shouldn't be changed. Its alteration probably leads to errors.
* EVENTS list can either contain of departure or arrival or both options.
* PARAMS can be changed.
* Dates range between DATE_START and DATE_END should be determined.
* STATIONS dictionary consists of {'convenient station description': 'yandex_station_code'}, where **yandex_station_code** should be finded this way:
    * For example we want to analyze Pulkovo airport in St. Petersburg. We paste "Санкт-Петербург" and for instance "Москва'
    ![](Screenshot_1.jpg?raw=true)
    * Now we are on the page of the rout between Pulkovo and Moscow Sheremetievo airport, so click on the "Pulkovo"
    ![](Screenshot_2.jpg?raw=true)
    * And here you can see 9600366 in the URL, thus Yandex station code is 's9600366'.
    ![](Screenshot_3.jpg?raw=true)
    * STATIONS can be {'St. Petersburg, Pulkovo': 's9600366'}.
