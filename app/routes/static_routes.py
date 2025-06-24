from flask import render_template
from ..models import User, Book, CartItem, Review, Order, OrderItem
from ..extensions import db


def register_static_routes(app):
    @app.template_filter('delivery_label')
    def delivery_label(method):
        return {
            'courier': 'Доставка курьером',
            'postman': 'Почта',
            'store': 'Самовывоз'
        }.get(method, 'Неизвестно')

    @app.template_filter('pickup_label')
    def pickup_label(code):
        return {
            'moscow_tverskaya_8': 'Москва, ул. Тверская, 8',
            'pushkina_kolotushkina': 'ул. Пушкина, д. Колотушкина',
            'zazhopinsk_pobedy_1': 'Зажопинск, пр. Победы, д. 1 (ориентир — танк)'
        }.get(code, 'Неизвестный пункт')



    @app.route('/delivery')
    def delivery():
        return render_template('delivery.html')

    @app.route('/contacts')
    def contacts():
        return render_template('contacts.html')

    @app.route('/payment')
    def payment():
        return render_template('payment.html')

    @app.context_processor
    def inject_genres():
        return dict(genres=[g[0] for g in db.session.query(Book.genre).distinct() if g[0]])