# Проект Foodgram "Продуктовый помощник".

## Описание

Данный сервис позволяет пользователям публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Данный проект реализован с применением следующего стека технологий:

Python, Django, Django REST Framework, PostgreSQL, NGINX, gunicorn, Docker

## В данном проекте реализованы следующие возможности:

**Для неавторизованных пользователей**
- Самостоятельная регистрация нового пользователя.
- Просмотр рецептов на главной странице.
- Просмотр отдельных страниц рецептов.
- Просмотр страниц пользователей.
- Фильтровать рецепты по тегам.

**Для авторизованных пользователей**
- Все возможности неавторизованных пользователей.
- Входить в систему под своим логином и паролем.
- Выходить из системы(разлогиниваться).
- Менять свой пароль.
- Создавать/редактировать/удалять собственные рецепты.
- Работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов.
- Работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл со количеством необходимых ингридиентов для рецептов из списка покупок.
- Подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.

**Для администраторов**
- Администратор обладает всеми правами авторизованного пользователя.

Плюс к этому он может:
- Изменять пароль любого пользователя,
- Создавать/блокировать/удалять аккаунты пользователей,
- Редактировать/удалять любые рецепты,
- Добавлять/удалять/редактировать ингредиенты.
- Добавлять/удалять/редактировать теги.

Все эти функции реализованы в стандартной админ-панели Django.


## Запуск проекта на виртуальной машине(сервере) в Docker контейнере.

- Подготовка виртуальной машины с операционной системой Linux Ubuntu.

Выполните обновление индексов пакетов в системе Linux и обновите все устаревшие пакеты, находящиеся в вашей системе, до последних версий.

```
sudo apt update
```
```
sudo apt upgrade -y
```

Установите Docker и Docker-Compose.

```
sudo apt install docker.io -y
```
```
sudo apt install docker-compose -y
```
- Установка проекта.

Склонируйте репозиторий проекта на сервер.

```
git clone https://github.com/meferyliv/foodgram-project-react.git
```

Перейдите в папку infra проекта foodgram.

```
cd foodgram-project-react/infra/
```

Создайте файл .env с необходимыми переменными окружения.

```
touch .env
```

Откройте файл .env любым текстовым редактором (vi, vim, nano) и заполните. В папке infra расположен файл шаблон .env.template

После заполнения .env, находясь в той же папке соберите и запустите образы Docker командой:

```
sudo docker-compose up -d
```

После запуска контейнеров необходимо заполнить базу данных(применив миграции), собрать статику, загрузить ингредиенты и теги из подготовленных фикстур.
Для этого выполните следующие инструкции.

```
sudo docker-compose exec backend python manage.py migrate
```

```
sudo docker-compose exec backend python manage.py collectstatic
```

```
sudo docker-compose exec backend python manage.py loaddata dump.json
```

## Автор проекта
Иван Лепский
