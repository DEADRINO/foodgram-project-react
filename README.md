User
 ## Продуктовый помощник - foodgram

 Приложение, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «cписок покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Есть возможность выгрузить файл (.txt) с перечнем и количеством необходимых ингредиентов для рецептов.

 ***Для работы с проектом необходимо выполнить действия, описанные ниже.***

 ```bash
 Склонируйте проект:
git clone https://github.com/DEADRINO/foodgram-project-react.git
Перейдите в директорию проекта:
cd foodgram-project-react/
Установите зависимости
pip install -r requirements.txt
Примените миграции:
python manage.py migrate
Запустите сервер разработки:
python manage.py runserver
***Тестовый пользователь и администратор***

Если выполнены все импорты в базу данных:
```bash
# Админ зона
http://localhost/admin
Login: admin
Password: admin777

# Тестовый пользователь
http://localhost/
Email: zelik1@yandex.ru
Password: Qwerty999

# Документация
http://localhost/redoc
```

***Технологии:***  
Python 3.9, Django 3.2, DRF 3.13, Nginx, Docker, Docker-compose, Postgresql, Github Actions.  
<!-- 