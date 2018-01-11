import datetime
import asyncio
import aiohttp
import socket
from models import *
from typing import Dict
# from sqlalchemy.sql import select
# import sqlalchemy as sa
import psycopg2
from psycopg2.sql import SQL, Identifier


def print_stations(tasks_results: list):
    count = 1
    for data in tasks_results:
        if isinstance(data, dict):
            print(count, ')', data['station']['title'], data['date'], data['event'], 'page', data['pagination']['page'])
            count += 1
        else:
            for j in data:
                print(count, ')', j['station']['title'], j['date'], j['event'], 'page', j['pagination']['page'])
                count += 1
    print(f'Количество ссылок: {count-1}')


def get_dates_range(date_start: str, date_end: str) -> list:
    start_date = datetime.datetime.strptime(date_start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(date_end, "%Y-%m-%d")
    dates = [(start_date + datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in
             range(0, (end_date - start_date).days + 1)]
    return dates


async def get_id(conn, model: str, param_name: str, param_value: str):
    async with conn.cursor() as cur:
        await cur.execute(SQL("SELECT id FROM {} WHERE {}=%s").format(Identifier(model), Identifier(param_name)),
                          (param_value,))
        # await cur.execute(sa.select([transport_type.c.id]).select_from(transport_type).where(transport_type.c.title == title))
        result = await cur.fetchone()
        id = None
        if result:
            id = result[0]
    return id


async def insert_station_type(conn, title):
    async with conn.cursor() as cur:
        try:
            await cur.execute('INSERT INTO station_type(title) VALUES(%s)', (title,))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_transport_type(conn, title):
    async with conn.cursor() as cur:
        try:
            await cur.execute('INSERT INTO transport_type(title) VALUES(%s)', (title,))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_station(conn, station_code, station_title, station_type_id, transport_type_id):
    async with conn.cursor() as cur:
        try:
            await cur.execute(
                'INSERT INTO station(code, title, station_type_id, transport_type_id) VALUES(%s, %s, %s, %s)',
                (station_code, station_title, station_type_id, transport_type_id))
            # await cur.execute(station.insert().values(
            #     code=station_code,
            #     title=station_title,
            #     station_type_id=station_type_id,
            #     transport_type_id=transport_type_id))

        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_carrier(conn, code, iata, title):
    async with conn.cursor() as cur:
        try:
            await cur.execute('INSERT INTO carrier(code, iata, title) VALUES(%s, %s, %s)', (code, iata, title))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_vehicle(conn, title):
    async with conn.cursor() as cur:
        try:
            await cur.execute('INSERT INTO vehicle(title) VALUES(%s)', (title,))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_transport_thread(conn, number: str, title: str, uid: str, carrier_id: int, transport_type_id: int,
                                  vehicle_id: int):
    async with conn.cursor() as cur:
        try:
            await cur.execute('''INSERT INTO transport_thread(number, title, uid, carrier_id, transport_type_id, vehicle_id)
                                VALUES(%s, %s, %s, %s, %s, %s)''',
                              (number, title, uid, carrier_id, transport_type_id, vehicle_id))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def insert_thread(conn, departure_date, departure_terminal, to_station_id, arrival_date, arrival_terminal,
                        from_station_id, days):
    async with conn.cursor() as cur:
        try:
            await cur.execute('''INSERT INTO thread(departure_date, departure_terminal, to_station_id, arrival_date, arrival_terminal,
                        from_station_id, days)
                                VALUES(%s, %s, %s, %s, %s, %s, %s)''',
                              (departure_date, departure_terminal, to_station_id, arrival_date, arrival_terminal,
                               from_station_id, days))
        except psycopg2.Error as e:
            print('psycopg2.Error:', e)


async def parse_data(pool, json_response: Dict):
    station_type = json_response['station']['station_type']
    transport_type = json_response['station']['transport_type']
    station_code = json_response['station']['code']
    station_title = json_response['station']['title']

    async with pool.acquire() as conn:
        async with conn.cursor() as cur:

            # ----------------------- Station ----------------------------------------------------------------
            transport_type_id = None
            station_id = await get_id(conn, 'station', 'title', station_code)
            if not station_id:
                station_type_id = await get_id(conn, 'station_type', 'title', station_type)
                if not station_type_id:
                    await insert_station_type(conn, station_type)
                    station_type_id = await get_id(conn, 'station_type', 'title', station_type)
                transport_type_id = await get_id(conn, 'transport_type', 'title', transport_type)
                if not transport_type_id:
                    await insert_transport_type(conn, transport_type)
                    transport_type_id = await get_id(conn, 'transport_type', 'title', transport_type)
                await insert_station(conn, station_code, station_title, station_type_id, transport_type_id)

            carrier_code = ''
            iata = ''
            for i in json_response['schedule']:

                # ----------------------- Carrier ----------------------------------------------------------------
                if 'code' in i['thread']['carrier']:
                    carrier_code = i['thread']['carrier']['code']
                if 'codes' in i['thread']['carrier']:
                    if 'iata' in i['thread']['carrier']['codes']:
                        iata = i['thread']['carrier']['codes']['iata']
                carrier_title = i['thread']['carrier']['title']
                carrier_id = await get_id(conn, 'carrier', 'title', carrier_title)
                if not carrier_id:
                    await insert_carrier(conn, carrier_code, iata, carrier_title)

                # ----------------------- Vehicle ----------------------------------------------------------------
                vehicle_title = 'Поезд'
                if 'vehicle' in i['thread']:
                    if i['thread']['vehicle'] is not None:
                        vehicle_title = i['thread']['vehicle']
                vehicle_id = await get_id(conn, 'vehicle', 'title', vehicle_title)
                if not vehicle_id and vehicle_title:
                    await insert_vehicle(conn, vehicle_title)
                    vehicle_id = await get_id(conn, 'vehicle', 'title', vehicle_title)

                # ----------------------- Transport_thread --------------------------------------------------------
                thread_number = i['thread']['number']
                thread_title = i['thread']['title']
                uid = i['thread']['uid']
                carrier_id = await get_id(conn, 'carrier', 'title', carrier_title)
                await insert_transport_thread(conn, thread_number, thread_title, uid, carrier_id, transport_type_id,
                                              vehicle_id)

                # ----------------------- Thread --------------------------------------------------------
                departure_date = i['departure']
                departure_terminal = i['terminal']
                arrival_date = i['arrival']
                arrival_terminal = i['terminal']
                days = i['days']
                await insert_thread(conn, departure_date, departure_terminal, station_id, arrival_date,
                                    arrival_terminal,
                                    station_id, days)


async def fetch(session, base_url, params_list, pool, page=1):
    params_copy = params_list.copy()
    params_copy.update(page=page)
    async with session.get(base_url, params=params_copy) as response:
        json_response = await response.json()
        await parse_data(pool, json_response)
        return json_response


async def start_crawling(session, base_url, params_list, pool):
    # # done, pending = await asyncio.wait(
    # #     [loop.create_task(fetch_first_page(session, loop, base_url, i)) for i in params_list],
    # #     return_when=asyncio.ALL_COMPLETED)
    #
    # done = await asyncio.gather(*[asyncio.Task(fetch(session, loop, base_url, i)) for i in params_list])
    #
    # # for task in done:
    #     # data = task.result()
    # for data in done:
    #     print('--', data['station']['title'], data['event'], 'page ', data['pagination']['page'])
    # return done

    json_response = await fetch(session, base_url, params_list, pool)
    if 'error' in json_response:
        print(json_response['error']['text'], json_response['error']['request'])

    try:
        if json_response["pagination"]["has_next"]:
            page_count = json_response["pagination"]["page_count"]
            #     # await asyncio.wait(
            #     #     [loop.create_task(fetch_first_page(session, loop, base_url, i)) for i in range(1, page_count + 1)])
            json_response = await asyncio.gather(
                *[asyncio.ensure_future(fetch(session, base_url, params_list, pool, page)) for page in
                  range(1, page_count + 1)])

    except KeyError:
        print(json_response['error']['text'], json_response['error']['request'])
    return json_response


async def main():
    dates = get_dates_range(config.DATE_START, config.DATE_END)

    if config.API_KEY is None:
        print('Не задан API_KEY Яндекс Расписанй')
        return

    params_list = []
    for station in config.STATIONS.values():
        for date in dates:
            for event in config.EVENTS:
                params_copy = config.PARAMS.copy()
                params_copy.update(station=station, date=date, event=event)
                params_list.append(params_copy)

    connector = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False,
    )

    pool = await create_all()

    async with aiohttp.ClientSession(connector=connector) as session:
        # async with engine.acquire() as conn:
        tasks_results = await asyncio.gather(
            *[asyncio.ensure_future(start_crawling(session, config.BASE_URL, i, pool)) for i in
              params_list])
        # loop.run_until_complete(start_crawling(session, loop, base_url, params_list))
        # tasks_results = loop.run_until_complete(asyncio.gather(*tasks))
    # loop.close()

    # print_stations(tasks_results)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(main()))
    loop.close()
