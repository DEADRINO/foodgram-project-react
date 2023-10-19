User
 ## Продуктовый помощник - foodgram

Добро пожаловать в наше приложение для кулинаров! У нас вы можете создавать и делиться своими рецептами, добавлять любимые блюда в избранное и следить за творчеством других авторов. Но это еще не всё! Наш сервис «Список покупок» позволяет вам легко составлять списки продуктов, необходимых для приготовления выбранных блюд. У вас также есть возможность загрузить файл с перечнем ингредиентов в формате .txt для удобного составления списка покупок. Давайте вдохновляться и готовить вкусно вместе!

 ***Для работы с проектом необходимо выполнить действия, описанные ниже.***

 ```bash
git clone <project>
cd foodgram-project-react/infra/
# сделайте копию файла <.env.example> в <.env>
cp .env.example .env
```

**Docker**
 ```bash
docker compose up -d
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py collectstatic --noinput
# Заполните базу тегами и ингредиентами:
docker-compose exec backend python manage.py import_tags
docker-compose exec backend python manage.py import_ingredients
```

***Тестовый пользователь и администратор***

Если выполнены все импорты в базу данных:
```bash
# Админ зона
http://localhost/admin
Login: admin
Password: admin

# Тестовый пользователь
http://localhost/
Email: dabek432@gmail.com
Password: qwerty1234

# Документация
http://localhost/redoc
```

***Технологии:***  
Python 3.9, Django 3.2, DRF 3.13, Nginx, Docker, Docker-compose, Postgresql, Github Actions.  
<!-- 