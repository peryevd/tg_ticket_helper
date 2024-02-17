# email_utils.py
import re
import json
import imaplib
import email
import telebot
import os
import config

from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

# Настройки подключения
username = os.getenv('EMAIL_USERNAME')
password = os.getenv('EMAIL_PASSWORD')
imap_url = os.getenv('IMAP_URL')
chat_id = os.getenv('CHAT_ID')

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))

status_order = config.status_order
file_status_path = config.file_status_path
register_subject = config.register_subject
work_subject = config.work_subject
close_subject = config.close_subject


def check_subject_for_keywords(subject, keywords, status):
    if any(keyword.lower() in subject.lower() for keyword in keywords):
        save_ticket(subject, {
            'id': parse_number_from_subject(subject),
            'status': status
        })


def check_mail():
    mail = imaplib.IMAP4_SSL(imap_url)
    mail.login(username, password)
    mail.select('inbox')  # Выбираем папку "Входящие"

    # Ищем непрочитанные письма без пометки "важно"
    status, messages = mail.search(None, 'UNSEEN', 'NOT', 'FLAGGED')

    if status == 'OK':
        # Преобразование байтовой строки в список идентификаторов
        messages = messages[0].split()

        for mail_id in messages:
            # Получение данных письма
            status, data = mail.fetch(mail_id, '(BODY.PEEK[HEADER])')
            if status == 'OK':
                # Парсинг письма
                msg = email.message_from_bytes(data[0][1])
                subject = decode_header(msg['subject'])[0][0]
                if isinstance(subject, bytes):
                    # Если subject в кодировке, декодируем ее
                    subject = subject.decode(
                        decode_header(msg['subject'])[0][1])

                # Проверяем subject письма на ключевые слова и обрабатываем его
                check_subject_for_keywords(
                    subject, register_subject, "register")
                check_subject_for_keywords(
                    subject, work_subject, "work")
                check_subject_for_keywords(
                    subject, close_subject, "closed")

                # Добавляем пометку "важно" к письму
                mail.store(mail_id, '+FLAGS', '\\Flagged')

    mail.logout()


def parse_number_from_subject(subject):
    return re.search(r'\d+', subject).group()


def load_ticket():
    with open(file_status_path, 'r') as f:
        data = json.load(f)
    return data


def save_ticket(subject, ticket):
    with open(file_status_path, 'r+') as f:  # Открываем файл для чтения и записи
        try:
            current_data = json.load(f)
        except json.JSONDecodeError:  # Если файл пустой или содержит некорректный JSON
            current_data = []

        index = next((i for i, item in enumerate(current_data)
                     if item['id'] == ticket['id']), None)
        if index is not None:
            if (ticket['status'] == 'closed'):
                a = bot.delete_message(chat_id, current_data[index]['msg_id'])
                print(a)
                current_data.pop(index)
            else:
                current_data[index]['status'] = ticket['status']
                message = f"*Обращение* \n*Тема:* {subject}\n*Статус:* {ticket['status']}"
                bot.edit_message_text(
                    message, chat_id, current_data[index]['msg_id'], parse_mode="Markdown")
        else:
            message = f"*Обращение* \n*Тема:* {subject}\n*Статус:* {ticket['status']}"
            msg_id = bot.send_message(chat_id, message, parse_mode="Markdown")
            current_data.append({**ticket, "msg_id": msg_id.id})

        f.seek(0)
        f.truncate()
        json.dump(current_data, f, ensure_ascii=False, indent=4)
