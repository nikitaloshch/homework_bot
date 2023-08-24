# Homework_bot
Телеграм бот который отслеживает статус проверки домашней работы на Яндекс.Практикуме.
### Технологии:
- Python 3
- python-telegram-bot 13

## Инструкции по установке
Клонируем репозиторий:
```
git clone git@github.com:nikitaloshch/homework_bot.git
```
Перейдем в него:
```
cd homework_bot
```

Установим и активируем виртуальное окружение:
```
python -m venv env
```
```
source venv/Scripts/activate
```

Установим зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Заполним .env:
```
- токен профиля Яндекс.Практикума
- токен телеграм бота
- свой ID в Телеграме
```

Запустим проект:
```
python homework.py
```
