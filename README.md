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
cp config/config.ini.template config/config.ini
```

* Указать парметры подключения к КПО Кобра и Telegram Bot API

### Запуск

```
python report.py
```