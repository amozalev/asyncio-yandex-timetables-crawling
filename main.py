import datetime
import asyncio
import socket
import aiohttp
import config
import models


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


async def fetch(session, loop, base_url, params, page=1):
    params_copy = params.copy()
    params_copy.update(page=page)
    # with aiohttp.Timeout(100):
    async with session.get(base_url, params=params_copy) as response:
        json_response = await response.json()
        # if json_response["pagination"]["has_next"]:
        #     page_count = json_response["pagination"]["page_count"]
        #     # await asyncio.wait(
        #     #     [loop.create_task(fetch_first_page(session, loop, base_url, i)) for i in range(1, page_count + 1)])
        #     await asyncio.gather(*[asyncio.Task(fetch(session, loop, base_url, i)) for i in params])
        return json_response


async def start_crawling(session, loop, base_url, params_list):
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

    json_response = await fetch(session, loop, base_url, params_list)
    if 'error' in json_response:
        print(json_response['error']['text'], json_response['error']['request'])

    try:
        if json_response["pagination"]["has_next"]:
            page_count = json_response["pagination"]["page_count"]
            json_response = await asyncio.gather(
                *[asyncio.ensure_future(fetch(session, loop, base_url, params_list, page)) for page in
                  range(1, page_count + 1)])

    except KeyError:
        print(json_response['error']['text'], json_response['error']['request'])
    return json_response


def main():
    dates = get_dates_range(config.DATE_START, config.DATE_END)

    params_list = []
    for station in config.STATIONS.values():
        for date in dates:
            for event in config.EVENTS:
                params_copy = config.PARAMS.copy()
                params_copy.update(station=station, date=date, event=event)
                params_list.append(params_copy)

    conn = aiohttp.TCPConnector(
        family=socket.AF_INET,
        verify_ssl=False,
    )

    loop = asyncio.get_event_loop()
    with aiohttp.ClientSession(loop=loop, connector=conn) as session:
        # loop.run_until_complete(start_crawling(session, loop, base_url, params_list))
        tasks = [asyncio.ensure_future(start_crawling(session, loop, config.BASE_URL, i)) for i in params_list]
        # tasks_results = loop.run_until_complete(asyncio.gather(*tasks))
        loop.run_until_complete(models.go())
    loop.close()

    # print_stations(tasks_results)


if __name__ == '__main__':
    main()
