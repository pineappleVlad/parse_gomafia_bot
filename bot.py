import telebot
from config import TOKEN
import asyncio
from backend import gomafia_parse


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '💬 Привет! Если хочешь узнать свою статистику по лх за все турниры на gomafia, введи айди своего ника (посмотреть можно, открыв ссылку профиля). 💬')
    bot.send_message(message.chat.id,
                     f'🤖 Бот может неправильно посчитать двойки из-за округления/коэффициента 🤖 \n'
                     f'Если вы нашли ошибки в работе бота - пишите @kingananaz (telegram)'
                     )

@bot.message_handler()
def stat(message):
    id = message.text

    async def get_stat():
        try:
            bot.send_message(message.chat.id,
                             f'❗ Собираем информацию, потребуется какое-то время ❗ \n'
                             f'Обращаем внимание, что сбор статистики начинается с начала января 2023 года, когда в силу вступили новые правила о компенсации  \n'
                             )
            total_hits, nickname = await gomafia_parse(id)
        except (AttributeError, TypeError):
            bot.send_message(message.chat.id,
                             '❌ По вашему айди невозможно собрать статистику  ❌')
            return
        hits = total_hits[0]
        if hits['all'] == 0:
            bot.send_message(message.chat.id, 'Не найдено сыгранных турниров 😳')
            return
        hit_pc = int((hits['two'] + hits['three']) / hits['all'] * 100)
        hit_one = int((hits['one'] + hits['two'] + hits['three']) / (hits['all'] - hits['zero_or_one_old_rules'])  * 100)
        sher_pc = int((hits['sher_death'] / hits['sher_cards']) * 100)
        red_pc = int((hits['red_death'] / hits['red_cards']) * 100)
        av_pc = int(hits['all'] / hits['tours_count'])

        bot.send_message(message.chat.id,
                         f'📊 Статистика игрока {nickname} \n'
                         f'💀 Отстрелы: {hits["all"]} \n'
                         f'🤓 Двойки: {hits["two"]} \n'
                         f'🕶 Тройки: {hits["three"]} \n'
                         f'😐 В одного: {hits["one"]} \n'
                         f'🗿 Не попал: {hits["zero"]} \n'
                         f'👍 Процент попадания в двойки/тройки - {hit_pc}% \n'
                         f'👌 Процент попадания в 1+ черных - {hit_one}% \n'
                         f'👮 Смертей за шерифа: {hits["sher_death"]} (всего шерифских карт - {hits["sher_cards"]}) \n'
                         f'❓ Смертей за красного: {hits["red_death"]} (всего красных карт - {hits["red_cards"]}) \n'
                         f'🚬 Процент пу за шерифа: {sher_pc}% \n'
                         f'🔴 Процент пу за красного: {red_pc}% \n'
                         f'🤔 В среднем отстрелов за турнир: {av_pc} \n'
                         )
        bot.send_message(message.chat.id,
                         f'FREE DONATION ♥ \n'
                         f'Если вы щедрый, приятный, хороший пользователь, можете поддержать разработчика любым донатом \n'
                         f'Телефон - 89513669262, Тинькофф \n'
                         f'Номер карты - 2200 7008 4224 6505 \n'
                         f'FREE DONATION ♥ \n'
                         )
        # bot.send_message(message.chat.id,
        #                  f'⚠ В зачет не идут отстрелы по старым правилам, где игрок оставил 0/1 черного в лх, а их было: {hits["zero_or_one_old_rules"]} ⚠'
        #                  )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_stat())




bot.polling(none_stop=True)
