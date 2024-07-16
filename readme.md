# Medical Bot Project

Этот проект представляет собой Telegram-бота для управления пациентами медицинского учреждения.

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/username/medical_bot_project.git
   cd medical_bot_project

2. Создайте и активируйте виртуальное окружение
(Либо используйте альтернативный вариант, см. ниже):
python -m venv venv
source venv/bin/activate

Для Windows: venv\Scripts\activate

3. Установите зависимости:
pip install -r requirements.txt

4. Настройте базу данных:
python manage.py migrate

5. Запустите бота:
python patients/bot.py

## Альтернативный вариант:

Если вы хотите запустить проект без создания виртуального окружения, выполните следующие шаги:

- Убедитесь, что все зависимости установлены, используя команду pip install -r requirements.txt.
- Настройте базу данных, если необходимо, с помощью команды python manage.py migrate.
- Запустите сервер разработки Django, используя команду python manage.py runserver

Этот вариант используется в случае, если у вас уже настроена среда разработки и не требуется изолированное виртуальное окружение.


## Использование

После запуска бота используйте команды или кнопки в Telegram для управления пациентами:

/add_patient - Добавить нового пациента.

![add_patient](images/add_patient.png)

/patients_today - Просмотреть пациентов, пришедших сегодня.

![patients_today](images/patients_today.png)

/patients_per_day - Просмотреть статистику по пациентам за текущую неделю.

![patients_per_day](images/patients_per_day.png)