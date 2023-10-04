from tech_func import get_headers, get_request
from bs4 import BeautifulSoup
import aiohttp



async def get_nickname(id):
    url = f'https://gomafia.pro/stats/{id}'
    response = await get_request(url)
    soup = BeautifulSoup(response, 'lxml')
    nickname = soup.find('div', class_='ProfileUserInfo_profile-user__name__iJAAE').text
    return nickname


async def get_tour_links(id):
    tour_hrefs = []
    pages = await get_pages(id)
    for page in range(1, pages + 1):
        url = f'https://gomafia.pro/stats/{id}?tab=history&page={page}'
        response = await get_request(url)
        soup = BeautifulSoup(response, 'lxml')
        tournaments = soup.find_all('a', class_='Links_links__c3oXE Links_links_primary__fsjS6')

        for tour in tournaments:
            link = tour.get('href')
            tour_hrefs.append('https://gomafia.pro/' + link)

    return tour_hrefs


async def get_pages(id):
    url = f'https://gomafia.pro/stats/{id}?tab=history&page=1'
    async with aiohttp.ClientSession(headers=await get_headers()) as session:
        async with session.get(url) as response:
            content = await response.text()
            soup = BeautifulSoup(content, 'lxml')
            pages_count_obj = soup.find_all('div', class_='Pagination_pagination__page___s0V8')
            try:
                count_pages = int(pages_count_obj[-1].text)
            except IndexError:
                count_pages = 1
    return count_pages
