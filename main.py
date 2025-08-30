import sqlite3
import os
from telebot import TeleBot, types

bot = TeleBot(os.environ["BOT_TOKEN"])

def get_raspisaniye(class_name, day):
    conn = sqlite3.connect(f'{class_name}.db')
    cursor = conn.cursor()
    cursor.execute("SELECT raspisaniye FROM timetable WHERE day=?", (day,))
    result = cursor.fetchone()
    conn.close()
    
    if result is None:
        return "Расписание не найдено"
    raspisaniye = result[0]
    return str(raspisaniye)


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn_class = types.InlineKeyboardButton("Выбрать класс", callback_data="class")
    markup.add(btn_class)
    bot.send_message(message.chat.id, "Выберите класс чтобы узнать его расписание\n\n Нажмите на кнопку выбора класса..", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    if call.data == "class":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_a = types.InlineKeyboardButton("Класс А", callback_data="class_a")
        btn_b = types.InlineKeyboardButton("Класс Б", callback_data="class_b")
        btn_v = types.InlineKeyboardButton("Класс В", callback_data="class_v")
        btn_g = types.InlineKeyboardButton("Класс Г", callback_data="class_g")
        btn_d = types.InlineKeyboardButton("Класс Д", callback_data="class_d")
        btn_e = types.InlineKeyboardButton("Класс Е", callback_data="class_e")
        btn_back = types.InlineKeyboardButton("Назад", callback_data="back_to_start")
        markup.add(btn_a, btn_b, btn_v, btn_g, btn_d, btn_e, btn_back)
        bot.edit_message_text("Выберите класс", chat_id, message_id, reply_markup=markup)

    elif call.data == "back_to_start":
        markup = types.InlineKeyboardMarkup()
        btn_class = types.InlineKeyboardButton("Выбор класса", callback_data="class")
        markup.add(btn_class)
        bot.edit_message_text("Выберите класс чтобы узнать его расписание\n\n Нажмите на кнопку выбора класса..", chat_id, message_id, reply_markup=markup)

    elif call.data.startswith("class_"):
        class_name = call.data.split("_")[1]
        markup = types.InlineKeyboardMarkup(row_width=2)
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        buttons = []
        for day in days:
            buttons.append(types.InlineKeyboardButton(day, callback_data=f"raspisaniye_{class_name}_{day.lower()}"))

        for i in range(0, len(buttons), 2):
            markup.row(*buttons[i:i+2])

        markup.add(types.InlineKeyboardButton("Назад", callback_data="class"))
        bot.edit_message_text("Выберите день недели", chat_id, message_id, reply_markup=markup)

    elif call.data.startswith("raspisaniye_"):
        parts = call.data.split("_")
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "Ошибка: некорректные данные")
            return
        
        class_name = parts[1]
        day = "_".join(parts[2:])
        raspisaniye = get_raspisaniye(f"class_{class_name}", day)
        class_names = {
            'a': 'А', 'b': 'Б', 'v': 'В', 'g': 'Г', 'd': 'Д', 'e': 'Е'
        }
        name_of_class = class_names.get(class_name.lower(), class_name.upper())
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Назад", callback_data=f"class_{class_name}"))
        response = f"Расписание для класса {name_of_class} на {day.capitalize()}:\n{raspisaniye}"
        bot.edit_message_text(
            text=response,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=markup
        )

if __name__ == '__main__':
    import time
    print("Бот запущен...")

    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Ошибка polling: {e}")
            time.sleep(5)



