import telebot
from config import TOKEN
import asyncio
from backend import gomafia_parse


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '💬 Привет! Если хочешь узнать свою статистику по лх за все турниры на gomafia, введи айди своего ника (посмотреть можно, открыв ссылку профиля). 💬')
    bot.send_message(message.chat.id, '🤖 Бот может неправильно посчитать двойки из-за округления/коэффициента 🤖')

@bot.message_handler()
def stat(message):
    id = message.text

    async def get_stat():
        try:
            bot.send_message(message.chat.id,
                             f'❗ Собираем информацию, потребуется какое-то время ❗ \n'
                             f'❗ Обращаем внимание, что сбор статистики начинается с начала января 2023 года, когда в силу вступили новые правила о компенсации ❗ \n'
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
        sher_pc = int(hits['sher_death'] / hits['red_death'] * 100)

        bot.send_message(message.chat.id,
                         f'📊 Статистика игрока {nickname} \n'
                         f'💀 Отстрелы: {hits["all"]} \n'
                         f'🤓 Двойки: {hits["two"]} \n'
                         f'🕶 Тройки: {hits["three"]} \n'
                         f'😐 В одного: {hits["one"]} \n'
                         f'🗿 Не попал: {hits["zero"]} \n'
                         f'👍 Процент попадания в двойки/тройки - {hit_pc}% \n'
                         f'👌 Процент попадания в 1+ черных - {hit_one}% \n'
                         f'👮 Смертей за шерифа {hits["sher_death"]} \n'
                         f'🚬 Процент шерифских смертей от общей суммы {sher_pc}% \n'
                         )
        # bot.send_message(message.chat.id,
        #                  f'⚠ В зачет не идут отстрелы по старым правилам, где игрок оставил 0/1 черного в лх, а их было: {hits["zero_or_one_old_rules"]} ⚠'
        #                  )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_stat())




bot.polling(none_stop=True)
