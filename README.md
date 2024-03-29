# Telegram Bot для взаимодействия с заявками из КПО Кобра

### Установка
* Установить pipenv

```
pip install pipenv
```

* Клонировать репозиторий

```
git clone git@github.com:maximishchenko/ag_task_bot.git
```

* Активировать виртуальное окружение

```
pipenv shell
```

* Установить зависимости

```
pipenv install
```

### Настройка параметров

* Скопировать шаблон конфигурации

```
cp template/config/config.ini.template config/config.ini
cp template/config/log.ini.template config/log.ini
```
> В случае, когда производится первоначальное развертывание БД, необходимо илициализировать миграции yoyo

> Важно! Имя БД db.sqlite3 привязано в коде приложения
```
yoyo init --database sqlite:///db.sqlite3 migration

```
* Применить миграции базы данных
```
yoyo apply
```

* Указать парметры подключения к КПО Кобра и Telegram Bot API

### Запуск вручную

* Запуск рассылки уведомлений о заявках на текущую дату

```
python tasks_notify.py
```

* Запуск бота

```
python bot.py
```

* Ручной запуск проверок pre-commit
```
pipenv run pre-commit run -a
```
