import os
import sys
import time
import logging
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from my_exceptions import WrongResponse, TelegramError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('YA_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEG_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEG_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяем, что есть все токены.
    Если нет хотя бы одного, то останавливаем бота.
    """
    logging.info('Проверка наличия всех токенов')
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message: str) -> None:
    """Отправляем сообщение в telegram."""
    try:
        logging.debug('Начало отправки статуса в telegram')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка отправки статуса в telegram: {error}')
        raise TelegramError(f'Ошибка отправки статуса в telegram: {error}')
    else:
        logging.info('Статус отправлен в telegram')


def get_api_answer(timestamp: int) -> dict:
    """Получение ответа от сервера."""
    logging.info('Проверяем статус 200')
    try:
        response = requests.get(ENDPOINT,
                                headers=HEADERS,
                                params={'from_date': timestamp}
                                )
        if response.status_code != HTTPStatus.OK:
            raise WrongResponse('Ответ не возвращает 200')
        return response.json()
    except Exception as error:
        raise WrongResponse(f'Ошибка при запросе к основному API: {error}')


def check_response(response: dict) -> list:
    """Проверяет ответ API."""
    logging.info('Проверка ответа API')
    if not isinstance(response, dict):
        raise TypeError('Ответ API не является dict')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('homeworks не является list')
    return homeworks


def parse_status(homework: dict) -> str:
    """Извлекает из информации о конкретной домашней.
    работе статус этой работы.
    """
    logging.info('Проводим проверки и извлекаем статус работы')
    if 'homework_name' not in homework:
        raise KeyError('Нет ключа homework_name в ответе API')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статуc домашки {homework_status}')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logging.info('Запуск бота')
    if not check_tokens():
        message = 'Отсутствует токен. Бот остановлен!'
        logging.critical(message)
        sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            number_of_hw = len(homework)
            if number_of_hw > 0:
                message = parse_status(homework[0])
                send_message(bot, message)
                logging.info('Новый статус домашки')
            else:
                logging.info('Новые статусы домашки отсутствуют')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.critical(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s, %(levelname)s, %(funcName)s, '
               '%(lineno)s, %(name)s, %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    main()
