import sys
import os
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_bot_project.settings')

django.setup()

import telebot
from telebot import types
from pydantic import BaseModel, ValidationError, Field
from datetime import datetime, date, timedelta
from django.conf import settings
from django.db.models import Count
from collections import defaultdict
from patients.models import Patient


bot = telebot.TeleBot('7378884099:AAHuRk93uNlPfrXGKrKL5J6cCgsOITn55EA')


class PatientModel(BaseModel):
    full_name: str

    @classmethod
    def validate_full_name(cls, value):
        if not value.replace(' ', '').isalnum():
            raise ValueError('ФИО не должно содержать специальных символов')
        return value

    birth_date: date

    @classmethod
    def validate_birth_date(cls, value):
        age = (date.today() - value).days // 365
        if age < 0 or age > 100:
            raise ValueError('Некорректная дата рождения. Убедитесь, что пациент старше 0 лет и не старше 100 лет.')
        return value


@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton('Добавить пациента')
    item2 = types.KeyboardButton('Пациенты сегодня')
    item3 = types.KeyboardButton('Пациенты за неделю')

    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, "Привет! Я бот для учета пациентов. Выберите действие из меню:",
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Добавить пациента')
def handle_add_patient_command(message):
    msg = bot.send_message(message.chat.id, "Введите ФИО пациента:")
    bot.register_next_step_handler(msg, process_full_name_step)

def process_full_name_step(message):
    try:
        full_name = message.text.strip()
        PatientModel.validate_full_name(full_name)
        msg = bot.send_message(message.chat.id, "Введите дату рождения в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(msg, process_birth_date_step, full_name)
    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка валидации: {e}")
        msg = bot.send_message(message.chat.id, "Введите корректное ФИО:")
        bot.register_next_step_handler(msg, process_full_name_step)

def process_birth_date_step(message, full_name):
    try:
        birth_date = datetime.strptime(message.text.strip(), '%d.%m.%Y').date()
        PatientModel.validate_birth_date(birth_date)
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3':
            Patient.objects.create(full_name=full_name, birth_date=birth_date)
        bot.send_message(message.chat.id, "Пациент успешно добавлен!")

        show_action_buttons(message.chat.id)

    except ValidationError as e:
        bot.send_message(message.chat.id, f"Ошибка валидации: {e}")
        msg = bot.send_message(message.chat.id, "Введите корректную дату рождения в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(msg, process_birth_date_step, full_name)
    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка валидации: {e}")
        msg = bot.send_message(message.chat.id, "Введите корректную дату рождения в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(msg, process_birth_date_step, full_name)


@bot.message_handler(func=lambda message: message.text == 'Пациенты сегодня')
def handle_patients_today_command(message):
    today = date.today()
    patients_today = Patient.objects.filter(created_at__date=today)

    if patients_today.exists():
        response = f"Статистика по пациентам за текущий день:\n"
        response += f"Всего пациентов: {patients_today.count()}\n\n"
        response += f"Список пациентов:\n"
        for patient in patients_today:
            response += f"- {patient.full_name}\n"
    else:
        response = "На сегодня нет добавленных пациентов."

    bot.send_message(message.chat.id, response, parse_mode='Markdown')

    show_action_buttons(message.chat.id)


@bot.message_handler(func=lambda message: message.text == 'Пациенты за неделю')
def handle_patients_per_day_command(message):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6) 
    patients_per_day = Patient.objects.filter(created_at__date__range=[week_start, week_end]) \
                                      .values('created_at__date') \
                                      .annotate(count=Count('id'))

    days_of_week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    response = "Статистика по пациентам за текущую неделю:\n\n"
    for day_idx, day_name in enumerate(days_of_week):
        patients_count = next((item['count'] for item in patients_per_day if item['created_at__date'].weekday() == day_idx), 0)
        response += f"{day_name}: {patients_count}\n"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')


    show_action_buttons(message.chat.id)


def show_action_buttons(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text='Добавить пациента', callback_data='add_patient'),
        types.InlineKeyboardButton(text='Пациенты за сегодня', callback_data='patients_today'),
        types.InlineKeyboardButton(text='Пациенты за неделю', callback_data='patients_per_day')
    ]
    keyboard.add(*buttons)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data == 'add_patient':
        handle_add_patient_command(call.message)
    elif call.data == 'patients_today':
        handle_patients_today_command(call.message)
    elif call.data == 'patients_per_day':
        handle_patients_per_day_command(call.message)

if __name__ == '__main__':
    bot.polling(none_stop=True)