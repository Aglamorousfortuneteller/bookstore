from flask import Flask
from .extensions import db, login_manager
from .models import User
from .utils import load_books_from_json
import os
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
from . import register_routes


@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import models

        # Регистрируем маршруты
        register_routes.register_all_routes(app)

        db_path = os.path.join(app.root_path, '..', 'instance', 'app.db')
        if os.path.exists(db_path):
            os.remove(db_path)

        db.create_all()
        books_path = os.path.join(app.root_path, '..', 'data', 'books_catalog.json')
        load_books_from_json(books_path)

    return app


