import asyncio
import aiohttp
import time
from lxml import html


async def get_data(source):
    tree = html.fromstring(source)
    title = ''.join(tree.xpath("//div[@class='page-title']/h2/text()")).strip()


async def get_url(source):
    tree = html.fromstring(source)
    links = tree.xpath("//div[@class='product-detail text-center']/a/@href")
    return links


async def fetch(session, url, parser='URL'):
    async with session.get(url) as response:
        source = await response.text()
        if parser == 'URL':
            return await get_url(source)
        else:
            await get_data(source)


async def bound_fetch(sem, session, url, parser='URL'):
    async with sem:
        return await fetch(session, url, parser)


async def run():
    tasks = []
    sem = asyncio.Semaphore(1000)

    async with aiohttp.ClientSession() as session:
        for i in range(1, 39):
            u = f'https://zakaz.atbmarket.com/catalog/175?page={i}&per-page=100'
            task = asyncio.create_task(bound_fetch(sem, session, u))
            tasks.append(task)
        us = await asyncio.gather(*tasks)
    urls = [item for sublist in us for item in sublist]

    async with aiohttp.ClientSession() as session:
        for u in urls:
            u = f'https://zakaz.atbmarket.com{u}'
            task = asyncio.create_task(bound_fetch(sem, session, u, ''))
            tasks.append(task)
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    start = time.time()
    asyncio.run(run())
