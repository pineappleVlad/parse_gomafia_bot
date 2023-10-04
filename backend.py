import aiohttp
from tech_func import tour_handler
from inner_gets_funcs import get_nickname, get_tour_links


async def gomafia_parse(id):
    old_hit_tags = {
        'zero_or_one': 'TableTournamentResultGame_table-tournament-result-game__item_b__cyV3k',
        'two': 'TableTournamentResultGame_table-tournament-result-game__item_lg__N_ZqL',
        'three': 'TableTournamentResultGame_table-tournament-result-game__item_g__W7YD7'
    }
    new_hit_tags = {
        'zero': 'TableTournamentResultGame_table-tournament-result-game__item_b__cyV3k',
        'one_or_two': 'TableTournamentResultGame_table-tournament-result-game__item_lg__N_ZqL',
        'three': 'TableTournamentResultGame_table-tournament-result-game__item_g__W7YD7'
    }
    total_hits = {
        'zero': 0,
        'one': 0,
        'two': 0,
        'three': 0,
        'all': 0,
        'zero_or_one_old_rules': 0
    }

    nickname = await get_nickname(id)
    tours_list = await get_tour_links(id)
    result = await tour_handler(tours_list, nickname, old_hit_tags, new_hit_tags, total_hits)
    return result, nickname




















