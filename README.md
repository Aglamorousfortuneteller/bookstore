# Bookstore

## Русскоязычная версия

### Описание

Это учебное веб-приложение интернет-магазина книг, разработанное с использованием Flask. Пользователи могут просматривать каталог, регистрироваться, добавлять книги в корзину и оформлять заказы.

### Функции

- Регистрация и вход с подтверждением по коду
- Просмотр каталога книг по жанрам и категориям
- Поиск книг по ключевому слову
- Подробная информация о книге (описание, цена, год, рейтинг)
- Добавление книг в корзину, обновление количества
- Оформление заказа с выбором способа доставки
- Просмотр истории заказов
- Оставление отзывов (только для авторизованных пользователей)

### Технологии

- Python 3.10+
- Flask, Flask-Login, Flask-SQLAlchemy
- Jinja2-шаблоны
- SQLite (или PostgreSQL)
- HTML5, CSS3 (возможна интеграция с Bootstrap)
- Git + GitHub для контроля версий

### Запуск проекта

1. Клонировать репозиторий
2. Создать виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # или venv\Scripts\activate в Windows
   ```
3. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. Запустить сервер:
   ```bash
   flask run
   ```

При первом запуске база данных будет автоматически создана, если она отсутствует.

---

## English Version

### Description

This is a demo online bookstore web app built with Flask. Users can browse the catalog, register, add books to the cart, and place orders.

### Features

- Registration and login with code confirmation
- Book catalog browsing by categories and genres
- Search books by keyword
- Book detail page with description, price, year, and rating
- Add books to cart, update quantities
- Checkout with delivery method selection
- Order history view
- Submit reviews (authenticated users only)

### Technologies

- Python 3.10+
- Flask, Flask-Login, Flask-SQLAlchemy
- Jinja2 templates
- SQLite or PostgreSQL
- HTML5, CSS3 (Bootstrap optional)
- Git + GitHub for version control

### Run Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   flask run
   ```

The database will be created automatically on first run if it does not exist.
