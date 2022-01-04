Проект состоит из скрипта main.py и Telegram-бота с вашим собственным названием. 

Пользователь с помощью специальных команд бота может выполнить следующие действия (получить следующую информацию): 
1. Узнать топ самых дешёвых отелей в городе (команда /lowprice). 
2. Узнать топ самых дорогих отелей в городе (команда /highprice). 
3. Узнать топ отелей, наиболее подходящих по цене и расположению от центра (самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
Без запущенного скрипта бот на команды (и на что-либо ещё) не реагирует.
Описание работы команд

Команда /lowprice После ввода команды у пользователя запрашивается: 
1. Город, где будет проводиться поиск. 
2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
Команда /highprice После ввода команды у пользователя запрашивается: 
1. Город, где будет проводиться поиск.
2. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).

Команда /bestdeal После ввода команды у пользователя запрашивается: 
1. Город, где будет проводиться поиск. 
2. Диапазон цен. 
3. Диапазон расстояния, на котором находится отель от центра. 
4. Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).

Описание внешнего вида и UI Окно Telegram-бота, который при запущенном Python-скрипте должен уметь воспринимать следующие команды: 
● /help — помощь по командам бота,
● /lowprice — вывод самых дешёвых отелей в городе,
● /highprice — вывод самых дорогих отелей в городе,
● /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра.

Сообщение с результатом команды должно содержать краткую информацию по каждому отелю. В эту информацию как минимум входит:

● название отеля, ● адрес,
● как далеко расположен от центра, 
● цена.

Технические требования 
● Скрипт для Telegram-бота должен быть написан с использованием библиотек Pytelegrambotapi и requests. 
● Запуск бота должен выполняться командой python main.py из Терминала, из папки с проектом. 
Реализация main.py и остальных файлов проекта остаётся за вами. Файлы не должны содержать ошибок, работа должна быть корректной.
● Техническая реализация. Команды бота, описанные в ТЗ, должны работать в соответствии с постановкой. 
Также выдача результата производится исключительно по соответствующей команде Telegram-бота.
● Интерфейс должен быть отзывчивым: при возникновении пользовательских ошибок (ввод несуществующих команд, ввод данных неверного типа и так далее) выводится соответствующее уведомление. 
● К скрипту должен быть приложен файл readme.md, который содержит в себе инструкцию (документацию) для работы со скриптом и пользователем.