#Telegram bot code copied from https://www.freecodecamp.org/news/how-to-create-a-telegram-bot-using-python/
#license plate checker code copied from SkipTracer https://github.com/xillwillx/skiptracer/blob/master/src/skiptracer/plugins/plate/__init__.py
#install Telegrom Python bot 'pip3 install pyTelegramBotAPI'
#install Beautiful Soup 'pip3 install beautifulsoup4'
#Create your own Telegram using Botfather. Then setcommands for 'carinfo' and 'fccinfo'

import os
import telebot
from bs4 import BeautifulSoup as bs
import requests
import re
import csv

#BOT_TOKEN = os.environ.get('BOT_TOKEN')
BOT_TOKEN = 'INSERT YOUR TELEGRAM API TOKEN HERE'

bot = telebot.TeleBot(BOT_TOKEN)


def get_plate_info(plate, state):
    plate = plate.upper()
    state = state.upper()
    url = 'https://www.faxvin.com/license-plate-lookup/result?plate={}&state={}'.format(plate, state)
    response = requests.get(url)
    html = response.content
    soup = bs(html, "html.parser")
    if soup.body.find_all(string=re.compile('.*{0}.*'.format('Sorry, the plate your currently looking for is not available.')), recursive=True):
        return "No plate found"
    try:
        table = soup.find('table', attrs={'class': 'tableinfo'})
    except BaseException:
        return "No source returned, try again later"

    try:
        cells = table.findAll("td")
    except BaseException:
        return "No results were found. Try again later or check FaxVin manually"

    make = cells[1].b.text
    model = cells[2].b.text
    year = cells[3].b.text
    automobile = year + " " + make + " " + model

    return automobile


def get_fcc_info(year, make, model):
    csv_file = csv.reader(open('car_fcc_info_DB.csv', "r"), delimiter=",")
    fcc_data = ""
    for row in csv_file:
        if year == row[0] and re.search(make, row[1], re.IGNORECASE) and re.search(re.escape(model), row[2], re.IGNORECASE):
            fcc_data = fcc_data + row[0] + " " + row[1] + " " + row[2] + "\n"
            fcc_data = fcc_data + "FCC ID: " + row[3] + "\n"
            fcc_data = fcc_data + "Freq: " + row[4] + " MHz " + row[5] + "\n" 
            fcc_data = fcc_data + "Exploit: " + row[6] + "\n"
            fcc_data = fcc_data + row[7] + "\n\n"

    if len(fcc_data) < 2:
        fcc_data = "Record not found"

    print(fcc_data)
    return fcc_data



@bot.message_handler(commands=['carinfo'])
def car_question(message):
    text = "What is the license plate and state? Enter the plate number without hyphens or spaces. State must be two letter. Example: WYU634 NE"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, car_info)


def car_info(message):
    regex = "(\w+)\s([a-zA-Z][a-zA-Z])"
    print("User: " + str(message.chat.id))
    print("Requesting info for: " + message.text)
    if re.match(regex, message.text):
        reg_result = re.match(regex, message.text)
        plate_info = get_plate_info(reg_result.group(1), reg_result.group(2))
        bot.send_message(message.chat.id, plate_info, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Bad format")


@bot.message_handler(commands=['fccinfo'])
def fcc_question(message):
    text = "What is the Year Make Model of the car? Example: 2012 Honda Civic"
    sent_msg = bot.send_message(message.chat.id, text, parse_mode="Markdown")
    bot.register_next_step_handler(sent_msg, fcc_info)

def fcc_info(message):
    regex = "(\d+)\s(\S+)\s(\S.*)"
    if re.match(regex, message.text):
        reg_result = re.match(regex, message.text)
        keyfob = get_fcc_info(reg_result.group(1), reg_result.group(2), reg_result.group(3))
        bot.send_message(message.chat.id, keyfob, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "Bad format")


bot.infinity_polling()
