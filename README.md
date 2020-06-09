Бот автомастерской MikesGarage

Перед началом использования создайте config.py и proxyconfig.py

В config.py в 1 строчке напишите 
```
TOKEN = 'ВАШ_ТОКЕН'
chat_id = 'ID_чата'
```
ID_чата - куда бот будет присылать сообщения

Чтобы узнать ID чата, можно добавить в чат бота - @RawDataBot
и он отдаст ID чата. 

В proxyconfig.py - настройки прокси

```
from telebot import apihelper
apihelper.proxy = {'https': 'socks5h://логин:пароль@IP_сервер:порт'}
```