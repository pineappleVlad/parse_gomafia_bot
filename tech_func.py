import asyncio
import unicodedata
import aiohttp
from bs4 import BeautifulSoup
from fake_headers import Headers
from datetime import datetime

async def get_request(url):
    async with aiohttp.ClientSession(headers=await get_headers()) as session:
        async with session.get(url) as response:
            content = await response.text()
    return content


async def get_headers():
    headers = Headers(browser='firefox', os='win')
    return headers.generate()


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
            total_lx = cells[6].text.strip()
            kills = cells[11].text.strip()
            return total_lx, kills


async def check_date_tour(tour_url):
    response = await get_request(tour_url)
    soup = BeautifulSoup(response, 'lxml')
    change_date = datetime.strptime('05.01.2023', "%d.%m.%Y")
    tour_date = datetime.strptime(soup.find('div', class_='_tid__tournament__top-left-item-description__nFBnP').text.split(" – ")[0], "%d.%m.%Y")
    if tour_date > change_date:
        rules = True
    else:
        rules = False
    return rules


async def game_handler(games_list, nickname, old_tags, new_tags, total_hits, rules, total):
    one_and_two_hits, one_and_zero_hits = 0, 0
    for game in games_list:
        rows = game.find_all('tr', class_='TableTournamentResultGame_table-tournament-result-game__item__SbL_M')
        for row in rows:
            columns = row.find_all('td')
            table_nick = columns[1].text.strip()
            clean_table_nick = unicodedata.normalize("NFKD", table_nick).strip().lower()
            clean_nickname = unicodedata.normalize("NFKD", nickname).strip().lower()
            kill_status = columns[2].get('class')
            if (kill_status is not None) and (clean_table_nick == clean_nickname) and ('TableTournamentResultGame_table-tournament-result-game__item_y__f279H' not in kill_status):
                if new_tags['three'] in kill_status:
                    total -= 0.5
                    total_hits['three'] += 1
                    break
                if rules:
                    if new_tags['zero'] in kill_status:
                        total_hits['zero'] += 1
                        break
                    elif new_tags['one_or_two'] in kill_status:
                        one_and_two_hits += 1
                        break
                else:
                    if old_tags['zero_or_one'] in kill_status:
                        one_and_zero_hits += 1
                        break
                    elif old_tags['two'] in kill_status:
                        total_hits['two'] += 1
                        break
            else:
                continue
    if rules:
        two_hits = int(float(total) // 0.25)
        total_hits['two'] += two_hits
        total_hits['one'] = total_hits['one'] + (one_and_two_hits - two_hits)
    else:
        total_hits['zero_or_one_old_rules'] += one_and_zero_hits

    return total_hits












async def tour_handler(tours, nickname, old_tags, new_tags, total_hits):
    for tour in tours:
        total, kills = await get_total_lx(tour, nickname)
        total = float(total)
        total_hits['all'] += int(kills)
        rules = await check_date_tour(tour)
        tour += '?tab=games'
        response = await get_request(tour)
        soup = BeautifulSoup(response, 'lxml')
        games_list = soup.find_all('table', class_='TableTournamentResultGame_table-tournament-result-game__WkjoT')
        total_hits = await game_handler(games_list, nickname, old_tags, new_tags, total_hits, rules, total)
    return total_hits, nickname
