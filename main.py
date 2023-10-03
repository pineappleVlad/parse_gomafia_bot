import aiohttp
import asyncio
from fake_headers import Headers
from bs4 import BeautifulSoup
import unicodedata

async def get_headers():
    headers = Headers(browser='firefox', os='win')
    return headers.generate()

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

async def get_request(url):
    async with aiohttp.ClientSession(headers=await get_headers()) as session:
        async with session.get(url) as response:
            content = await response.text()
    return content

async def get_tour_links(id):
    tour_hrefs = []
    pages = await get_pages(id)
    for page in range(1, pages + 1):
        url = f'https://gomafia.pro/stats/{id}?tab=history&page={page}'
        response = await get_request(url)
        soup = BeautifulSoup(response, 'lxml')
        tournaments = soup.find_all('a', class_='Links_links__c3oXE Links_links_primary__fsjS6')
        nickname = soup.find('div', class_='ProfileUserInfo_profile-user__name__iJAAE').text


        for tour in tournaments:
            link = tour.get('href')
            tour_hrefs.append('https://gomafia.pro/' + link)
    return tour_hrefs, nickname


async def get_total_lx(url, nickname):
    url += '?tab=tournament'
    response = await get_request(url)
    soup = BeautifulSoup(response, 'lxml')
    table = soup.find('div', class_='TableTournamentResult_tournaments-table-result__Y93S7')
    try:
        rows = table.find_all('tr')
    except AttributeError:
        return 0, 0
    for row in rows:
        cells = row.find_all('td')
        cleaned_nickname = unicodedata.normalize("NFKD", nickname).strip().lower()
        cleaned_cell_text = unicodedata.normalize("NFKD", cells[1].text.strip().lower())
        if cleaned_cell_text == cleaned_nickname:
            total = cells[6].text.strip()
            kills = cells[11].text.strip()
            return total, kills

async def gomafia_parse(id):
    three_hit_class = 'TableTournamentResultGame_table-tournament-result-game__item_g__W7YD7'
    one_hit_class = 'TableTournamentResultGame_table-tournament-result-game__item_lg__N_ZqL'
    zero_hit_class = 'TableTournamentResultGame_table-tournament-result-game__item_b__cyV3k'
    tours, nickname = await get_tour_links(id)
    total_zero_maf, total_one_maf, total_two_mafs, total_three_mafs, all_kills = 0, 0, 0, 0, 0
    for tour in tours:
        total, kills = await get_total_lx(tour, nickname)
        total = float(total)
        all_kills += int(kills)
        one_or_two_maf_count = 0
        tour += '?tab=games'
        response = await get_request(tour)
        soup = BeautifulSoup(response, 'lxml')
        games_list = soup.find_all('table', class_='TableTournamentResultGame_table-tournament-result-game__WkjoT')
        for game in games_list:
            rows = game.find_all('tr', class_='TableTournamentResultGame_table-tournament-result-game__item__SbL_M')
            for row in rows:
                columns = row.find_all('td')
                table_nick = columns[1].text.strip()
                clean_table_nick = unicodedata.normalize("NFKD", table_nick).strip().lower()
                clean_nickname = unicodedata.normalize("NFKD", nickname).strip().lower()
                if columns[2].get('class') is not None:
                    kill_status = columns[2].get('class')
                else:
                    continue
                if clean_table_nick != clean_nickname:
                    continue
                else:
                    if three_hit_class in kill_status:
                        total -= 0.5
                        total_three_mafs += 1
                        break
                    elif one_hit_class in kill_status:
                        one_or_two_maf_count += 1
                        break
                    elif zero_hit_class in kill_status:
                        total_zero_maf += 1
                        break
        two_mafs_count = int(float(total) // 0.25)
        total_two_mafs += two_mafs_count
        total_one_maf += one_or_two_maf_count - two_mafs_count
    return nickname, total_zero_maf, total_one_maf, total_two_mafs, total_three_mafs, all_kills

# def output(zero, one, two, three, all):
#     zero = int(zero)
#     one = int(one)
#     two = int(two)
#     three = int(three)
#     all = int(all)
#     hit_pc = int((two + three) / all * 100)
#
#     print(f"За {all} отстрелов ты оставил")
#     print(f"Двойки: {two}")
#     print(f'Тройки: {three}')
#     print(f'В одного: {one}')
#     print(f'Не попал: {zero}')
#     print(f'процент попадания в двойки/тройки - {hit_pc}%')
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     try:
#         nickname, zero, one, two, three, all = loop.run_until_complete(gomafia_parse(867))
#         output(zero, one, two, three, all)
#     except TypeError:
#         print('Неизвестная ошибка')

