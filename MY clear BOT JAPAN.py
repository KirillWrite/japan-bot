import requests
import bs4
import re
import telebot
from telebot import types
from SimpleQIWI import *
import time

bot = telebot.TeleBot('')  # токен от бота в телеграм, взять тут - t.me/BotFather
number = ''  # номер киви
token = ''  # токен киви, взять тут - qiwi.com/api
api = QApi(token=token, phone=number)
sum = 99999  # пожертвование разработчику


menu = types.InlineKeyboardMarkup(row_width=3)
menu.add(types.InlineKeyboardButton(text='Аукционный лист', callback_data='info'))


menu2 = types.InlineKeyboardMarkup(row_width=3)
menu2.add(
    types.InlineKeyboardButton(text='ОПЛАТА', callback_data='oplat'),
    types.InlineKeyboardButton(text='Вернуться в меню', callback_data='back')
)

@bot.message_handler(content_types=["text"])
def message_send(message):
    chat_id = message.chat.id
    message_id = message.message_id
    username = message.from_user.first_name
    starter = f'''
	Привет, {username}! \n--------------------------------- \n👩🏼‍💻 С помощью этого бота можно посмотреть существует ли аукционный лист японского автомобиля для внутреннего рынка Японии \n⬇ Выбери действие ниже
	'''
    if message.text == '/start':
        bot.send_message(chat_id, starter, reply_markup=menu)

def car_number(message):
    chatId = message.chat.id
    car_number_input = message.text
    a = car_number_input
    try:
        response = requests.get(f'https://auctions.fujiyama-trading.ru/report?q={a}')
        page = bs4.BeautifulSoup(response.content, 'html5lib')
        car_info = page.find('table', attrs={'cellpadding': '0'}).find('td', attrs={'valign': 'top','style': 'padding-left: 5px; padding-top: 7px;'}).text.replace('\n', '').replace('\xa0', '')
        q = car_info.split()
        w = (" ".join(q))
        print(w)  # вывод наименования автомобиля
        bot.send_message(chatId, '🕐 Начинаем поиск на сервере...')
        time.sleep(2)
        bot.send_message(chatId, '🕑 Загружаем информацию с базы...')
        time.sleep(1)
        bot.send_message(chatId, w)
        car_auc_list = str(page.find('div', attrs={'class', 'pad_fix_me'}).find('table', attrs={'cellpadding': '0'}).find('td', attrs={'valign': 'top'}).find('img'))
        url = re.findall(r'https?://\S+', car_auc_list)
        url2 = [quotation_marks.strip('"') for quotation_marks in url]
        url3 = ''.join(url2)
        print(url3)  # вывод краткой картиныки аукционника автомобиля
        bot.send_photo(chatId, url3)
        sent = bot.send_message(chatId,'🚗 Аукционный лист существует! \n✅ Нажмите кнопку ОПЛАТА, чтобы поблагодарить разработчика', reply_markup=menu2)
        return a
    except:
        sent = bot.send_message(chatId, 'Номер кузова введён неправильно или не найден, повторите ввод:')
        bot.register_next_step_handler(sent, car_number)
        return

@bot.callback_query_handler(func=lambda call: True)
def handler_call(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    username = call.from_user.first_name
    oplata = 'opl' + str(chat_id)
    sendRequests = f"https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={number}&amountInteger={sum}&amountFraction=0&extra%5B%27comment%27%5D={oplata}&currency=643&blocked%5B0%5D=sum&blocked%5B1%5D=comment&blocked%5B2%5D=account"
    buy1 = types.InlineKeyboardMarkup(row_width=3)
    buy1.add(
        types.InlineKeyboardButton(text='Оплатить', url=sendRequests, callback_data='pay'),
        types.InlineKeyboardButton(text='Назад', callback_data='back')
    )


    if call.data == 'info':
        sent = bot.send_message(chat_id,'Поиск аукционного листа автомобиля \n--------------------------------- \n⌨ Введите номер кузова автомобиля в формате (кузов-номер) \n✅ Например: ZWA10-7894165 ', reply_markup=menu)
        bot.register_next_step_handler(sent, car_number)


    elif call.data == 'oplat':

        bbb = f'''
		🔎Пожертвование разработчику: {sum} руб \n✅ Спасибо за мотивацию \n🆔 Ваш ID: {chat_id}
		'''
        bot.send_message(chat_id, bbb, parse_mode='MarkdownV2', reply_markup=buy1)


    elif call.data == 'back':
        starter = f'''
		Привет, {username}! \n--------------------------------- \n👩🏼‍💻 С помощью этого бота можно посмотреть существует ли аукционный лист японского автомобиля  \n⬇ Выбери действие ниже ️
	    '''
        bot.send_message(chat_id, starter, reply_markup=menu)


bot.polling()
