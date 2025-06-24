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

### Структура проекта

      bookstore/
      │
      ├── run.py # Точка входа: запуск приложения
      ├── import_books_from_json.py # Импорт каталога книг из JSON
      ├── config.py # Конфигурация Flask-приложения
      │
      ├── app/
      │ ├── init.py # Создание Flask-приложения, инициализация расширений
      │ ├── models.py # Определения моделей БД
      │ ├── extensions.py # Расширения Flask (SQLAlchemy, LoginManager и др.)
      │ ├── register_routes.py # Регистрация всех маршрутов
      │ ├── utils.py # Вспомогательные функции
      │ │
      │ ├── routes/
      │ │ ├── auth_routes.py # Регистрация, вход, выход
      │ │ ├── book_routes.py # Главная, поиск, детали книг, жанры, категории
      │ │ ├── cart_routes.py # Корзина, обновление, удаление, подсчёт стоимости
      │ │ ├── order_routes.py # Оформление заказа, история, детали
      │ │ └── static_routes.py # О магазине, контакты и прочие статические страницы
      │ │
      │ └── templates/
      │ ├── account_deleted.html
      │ ├── base.html
      │ ├── book_detail.html
      │ ├── cart.html
      │ ├── category.html
      │ ├── checkout.html
      │ ├── confirm_order.html
      │ ├── confirm.html
      │ ├── contacts.html
      │ ├── delivery.html
      │ ├── genre.html
      │ ├── index.html
      │ ├── login.html
      │ ├── orders.html
      │ ├── order_details.html
      │ ├── payment.html
      │ ├── profile.html
      │ ├── register.html
      │ └── search_results.html
      │
      ├── static/
      │ ├── covers/
      │ │ └── book_cover.jpg
      │ └── styles.css # Основные стили
      │
      ├── instance/
      │ └── bookstore.db # База данных SQLite (создаётся при первом запуске)
      │
      ├── data/
      │ └── books_catalog.json # Исходные данные для импорта книг
      │
      ├── requirements.txt # Зависимости проекта
      └── README.md # Документация проекта


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

### Project Structure

      bookstore/
      │
      ├── run.py # Entry point: run the app
      ├── import_books_from_json.py # Book catalog import from JSON
      ├── config.py # Flask app configuration
      │
      ├── app/
      │ ├── init.py # Create Flask app, initialise extensions
      │ ├── models.py # DB models: User, Book, CartItem, Order, Review, etc.
      │ ├── extensions.py # Flask extensions (SQLAlchemy, LoginManager, etc.)
      │ ├── register_routes.py # Route registration
      │ ├── utils.py # Utility functions
      │ │
      │ ├── routes/
      │ │ ├── auth_routes.py # Registration, login, logout
      │ │ ├── book_routes.py # Home, search, book details, genres, categories
      │ │ ├── cart_routes.py # Cart management and price calculation
      │ │ ├── order_routes.py # Checkout, order history, details
      │ │ └── static_routes.py # About, contacts, and other static pages
      │ │
      │ └── templates/
      │ ├── account_deleted.html
      │ ├── base.html
      │ ├── book_detail.html
      │ ├── cart.html
      │ ├── category.html
      │ ├── checkout.html
      │ ├── confirm_order.html
      │ ├── confirm.html
      │ ├── contacts.html
      │ ├── delivery.html
      │ ├── genre.html
      │ ├── index.html
      │ ├── login.html
      │ ├── orders.html
      │ ├── order_details.html
      │ ├── payment.html
      │ ├── profile.html
      │ ├── register.html
      │ └── search_results.html
      │
      ├── static/
      │ ├── covers/
      │ │ └── book_cover.jpg
      │ └── styles.css # Main styles
      │
      ├── instance/
      │ └── bookstore.db # SQLite database (created on first run)
      │
      ├── data/
      │ └── books_catalog.json # Source data for book import
      │
      ├── requirements.txt # Project dependencies
      └── README.md # Project documentation
