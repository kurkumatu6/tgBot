from config import *
from db import *
import telebot
from random import randint
from telebot import types
from newsapi import NewsApiClient


bot = telebot.TeleBot(TOKENBOT, parse_mode=None)
newsapi = NewsApiClient(api_key=TOKENNEWS)
@bot.message_handler(commands=['start'])
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	itemNews = types.KeyboardButton('Получить новости')
	itemSub = types.KeyboardButton('Мои подписки')
	itemCate = types.KeyboardButton('Все категории')
	markup.add(itemNews, itemSub, itemCate)
	bot.reply_to(message, 	registr(connect, cursor, message.from_user.id), reply_markup = markup )
@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message,  "для просмотра всех возможных категорий введите /subscriptionsAdd \n для просмотра своих подписок /showMySubs \n для получения новостей /getNews")

@bot.message_handler(commands=['subscriptionsAdd'])
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	# userId = selectUser(connect, cursor, message.from_user.id)
	bot.reply_to(message, 	showCategoryes(connect, cursor))

@bot.message_handler(commands=showCategoryesSystem(connect, cursor, "add"))
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	userId = selectUser(connect, cursor, message.from_user.id)
	print(message.text[4:])
	bot.reply_to(message, podpis(connect, cursor, userId, message.text[4:]))

@bot.message_handler(commands=showCategoryesSystem(connect, cursor, "del"))
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	userId = selectUser(connect, cursor, message.from_user.id)
	print(message.text[4:])
	bot.reply_to(message, unsubs(connect, cursor, userId, message.text[4:]))

@bot.message_handler(commands=["showMySubs"])
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	userId = selectUser(connect, cursor, message.from_user.id)
	bot.reply_to(message, showPodpis(connect, cursor, userId))

@bot.message_handler(commands=["getNews"])
def send_welcome(message):
	connect = sqlite3.connect("subs.db")
	cursor = connect.cursor()
	userId = selectUser(connect, cursor, message.from_user.id)
	for i in showPodpisSystem(connect, cursor, userId):
		top_headlines = newsapi.get_top_headlines(category=i[1], page_size=1, page=1, language="ru")
		text = f'{top_headlines["articles"][0]["title"]}({top_headlines["articles"][0]["url"]})'
		bot.send_message(message.chat.id, f'<a href="{top_headlines["articles"][0]["url"]}">{top_headlines["articles"][0]["title"]}</a>', parse_mode='HTML')

categoryArray = {}
for i in showCategoryes(connect, cursor):
	categoryArray[f"подписаться на категорию '{i[0]}'"] = i[0]
categoryArrayDel = {}
for i in showCategoryes(connect, cursor):
	categoryArrayDel[f"отписаться от категории '{i[0]}'"] = i[0]
print(categoryArray)
print(categoryArray.get(f"подписаться на 'бизнес'"))
print(categoryArray.get(f"подписаться на 'бизнесфывафыва'"))
@bot.message_handler(func=lambda message: True)
def echo_all(message):
	if message.text == "Получить новости":
		connect = sqlite3.connect("subs.db")
		cursor = connect.cursor()
		userId = selectUser(connect, cursor, message.from_user.id)
		podpis = showPodpisSystem(connect, cursor, userId)
		for i in podpis:
			ranPage = randint(1,11)
			top_headlines = newsapi.get_top_headlines(category=i[1], page_size=1, page=ranPage, language="ru")
			text = f'{top_headlines["articles"][0]["title"]}({top_headlines["articles"][0]["url"]})'
			bot.send_message(message.chat.id,f'<a href="{top_headlines["articles"][0]["url"]}">{top_headlines["articles"][0]["title"]}</a>',parse_mode='HTML')
		print(podpis)
		if podpis == []:
			bot.send_message(message.chat.id,"Вы не подписаны не на одну из категорий поэтому тут пусто")


	if message.text == 'Все категории':
		connect = sqlite3.connect("subs.db")
		cursor = connect.cursor()
		# userId = selectUser(connect, cursor, message.from_user.id)
		rez = showCategoryes(connect, cursor)
		categ = ""
		num = 1
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		for i in rez:
			categ += f"{num}) {i[0]} \n"
			num += 1
			btn = types.KeyboardButton(f"подписаться на категорию '{i[0]}'")
			markup.add(btn)
		btn = types.KeyboardButton("Назад")
		markup.add(btn)
		bot.reply_to(message, categ, reply_markup = markup)


	if message.text == 'Назад':
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		itemNews = types.KeyboardButton('Получить новости')
		itemSub = types.KeyboardButton('Мои подписки')
		itemCate = types.KeyboardButton('Все категории')
		markup.add(itemNews, itemSub, itemCate)
		bot.send_message(message.chat.id, "Возвращаю", reply_markup=markup)


	if  categoryArray.get(message.text) != None:
		categ = categoryArray.get(message.text)
		connect = sqlite3.connect("subs.db")
		cursor = connect.cursor()
		userId = selectUser(connect, cursor, message.from_user.id)
		bot.send_message(message.chat.id, podpisForName(connect, cursor, userId, categ))


	if message.text == 'Мои подписки':
		connect = sqlite3.connect("subs.db")
		cursor = connect.cursor()
		userId = selectUser(connect, cursor, message.from_user.id)
		subsuser = showPodpis(connect, cursor, userId)
		rez = 'Вы подписаны на: \n'
		count = 1
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		for i in subsuser:
			rez += f"{count}) {i[0]}\n"
			count += 1
			btn = types.KeyboardButton(f"отписаться от категории '{i[0]}'")
			markup.add(btn)
		btn = types.KeyboardButton("Назад")
		markup.add(btn)
		if count == 1:
			rez = 'У вас нет подписок'
		bot.reply_to(message, rez, reply_markup = markup)


	if  categoryArrayDel.get(message.text) != None:
		categ = categoryArrayDel.get(message.text)
		connect = sqlite3.connect("subs.db")
		cursor = connect.cursor()
		userId = selectUser(connect, cursor, message.from_user.id)
		bot.send_message(message.chat.id, unsubsForName(connect, cursor, userId, categ))
		#bot.send_message(message.chat.id, "asdasdasda")
		# reset(message)

		userId = selectUser(connect, cursor, message.from_user.id)
		subsuser = showPodpis(connect, cursor, userId)
		rez = 'Вы подписаны на: \n'
		count = 1
		markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
		for i in subsuser:
			rez += f"{count}) {i[0]}\n"
			count += 1
			btn = types.KeyboardButton(f"отписаться от категории '{i[0]}'")
			markup.add(btn)
		if count == 1:
			rez = 'У вас нет подписок'
		btn = types.KeyboardButton("Назад")
		markup.add(btn)
		bot.send_message(message.chat.id, rez, reply_markup=markup)

# def reset(message):
#
	# userId = selectUser(connect, cursor, message.from_user.id)
	# subsuser = showPodpis(connect, cursor, userId)
	# rez = 'Вы подписаны на: \n'
	# count = 1
	# markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
	# for i in subsuser:
	# 	rez += f"{count}) {i[0]}\n"
	# 	count += 1
	# 	btn = types.KeyboardButton(f"отписаться от '{i[0]}'")
	# 	markup.add(btn)
	# btn = types.KeyboardButton("Назад")
	# markup.add(btn)
	# bot.send_message(message, rez, reply_markup=markup)


bot.infinity_polling()