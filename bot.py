import telebot
from config import TOKEN
import asyncio
from main import gomafia_parse


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Если хочешь узнать свою статистику по лх за все турниры на gomafia, введи айди своего ника (посмотреть можно, открыв ссылку профиля).')
    bot.send_message(message.chat.id, 'Статистика может быть не совсем правильная из-за коэффициента в финале и округления допа, а также, если вы меняли ник')

@bot.message_handler()
def stat(message):
    id = message.text

    async def get_stat():
        try:
            bot.send_message(message.chat.id,
                             'Собираем информацию, ответ зависит от кол-ва турниров и займет какое-то время (30-200 секунд)')
            nickname, zero, one, two, three, all = await gomafia_parse(id)
        except TypeError:
            print('По вашему айди невозможно собрать статистику, эта проблема может быть из-за смены ника')
            return
        zero, one, two, three, all = int(zero), int(one), int(two), int(three), int(all)
        hit_pc = int((two + three) / all * 100)
        hit_one = int((one + two + three) / all * 100)

        bot.send_message(message.chat.id,
                         f'Статистика игрока {nickname} \n'
                         f'Отстрелы: {all} \n'
                         f'Двойки: {two} \n'
                         f'Тройки: {three} \n'
                         f'В одного: {one} \n'
                         f'Не попал: {zero} \n'
                         f'Процент попадания в двойки/тройки - {hit_pc}% \n'
                         f'Процент попадания в 1+ черных - {hit_one}% \n'
                         )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(get_stat())




bot.polling(none_stop=True)
