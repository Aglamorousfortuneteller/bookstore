from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from ..models import User, Book, CartItem, Review, Order, OrderItem
from ..extensions import db
from datetime import datetime

def register_order_routes(app):
    @app.route('/checkout', methods=['GET', 'POST'])
    @login_required
    def checkout():
        if request.method == 'POST':
            for key, value in request.form.items():
                if key.startswith('quantities_'):
                    try:
                        item_id = int(key.split('_')[1])
                        new_qty = int(value)
                        cart_item = CartItem.query.get(item_id)
                        if cart_item and cart_item.user_id == current_user.id:
                            cart_item.quantity = new_qty
                    except ValueError:
                        continue
            db.session.commit()

            selected_ids_raw = request.form.get('selected_items')
            selected_ids = selected_ids_raw.split(',') if selected_ids_raw else []

            if not selected_ids:
                if request.form.get('flash_error'):
                    flash("Выберите хотя бы один товар для оформления заказа", "error")
                return redirect(url_for('view_cart'))

            session['selected_ids'] = selected_ids
            return redirect(url_for('checkout'))


        selected_ids = session.get('selected_ids')
        if selected_ids:
            cart_items = CartItem.query.filter(
                CartItem.id.in_(selected_ids),
                CartItem.user_id == current_user.id
            ).all()
        else:
            cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

        total = round(sum(item.book.price * item.quantity for item in cart_items), 2)
        delivery_date = datetime.utcnow().date().strftime("%d.%m.%Y")
        return render_template('checkout.html', cart_items=cart_items, total=total, delivery_date=delivery_date)



    @app.route('/confirm_order', methods=['POST'])
    @login_required
    def confirm_order():
        selected_ids = session.get('selected_ids', [])
        cart_items = CartItem.query.filter(
            CartItem.id.in_(selected_ids),
            CartItem.user_id == current_user.id
        ).all()

        if not cart_items:
            flash("Не удалось найти выбранные товары", "error")
            return redirect(url_for("view_cart"))

        total = round(sum(item.book.price * item.quantity for item in cart_items), 2)

        session['order_info'] = {
            "name": request.form['name'],
            "phone": request.form['phone'],
            "delivery_method": request.form['delivery_method'],
            "address": request.form.get('address', ''),
            "pickup_location": request.form.get('pickup_location', ''),
            "total": total,
            "selected_ids": selected_ids
        }

        return render_template('confirm_order.html',
                            name=request.form['name'],
                            phone=request.form['phone'],
                            delivery_method=request.form['delivery_method'],
                            address=request.form.get('address', ''),
                            pickup_location=request.form.get('pickup_location', ''),
                            total=total,
                            delivery_date=datetime.utcnow().date().strftime("%d.%m.%Y"))


    @app.route('/finalize_order', methods=['POST'])
    @login_required
    def finalize_order():
        order_info = session.get('order_info')
        selected_ids = order_info.get('selected_ids', []) if order_info else []

        if not order_info or not selected_ids:
            flash("Ошибка оформления заказа", "error")
            return redirect(url_for('checkout'))

        cart_items = CartItem.query.filter(
            CartItem.id.in_(selected_ids),
            CartItem.user_id == current_user.id).all()

        if not cart_items:
            flash("Корзина пуста", "error")
            return redirect(url_for('checkout'))

        order = Order(
            user_id=current_user.id,
            name=order_info.get('name', ''),
            phone=order_info.get('phone', ''),
            delivery_method=order_info.get('delivery_method', ''),
            address=order_info.get('address', ''),
            pickup_location=order_info.get('pickup_location', ''),
            total_price=order_info.get('total', 0),
            status='Ожидается',
            date=datetime.utcnow())
        db.session.add(order)
        db.session.flush()

        for item in cart_items:
            book = item.book
            order_item = OrderItem(
                order_id=order.id,
                book_id=book.id,
                book_title=book.title,
                quantity=item.quantity,
                price=book.price * item.quantity,
                price_per_item=book.price
            )
            db.session.add(order_item)
        CartItem.query.filter(
            CartItem.id.in_(selected_ids),
            CartItem.user_id == current_user.id).delete(synchronize_session='fetch')
        db.session.commit()
        session.pop('order_info', None)
        return redirect(url_for('order_details', order_id=order.id))


    @app.route('/orders')
    @login_required
    def orders():
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
        return render_template('orders.html', orders=orders)


    @app.route('/orders/<int:order_id>')
    @login_required
    def order_details(order_id):
        order = Order.query.get_or_404(order_id)
        
        return render_template('order_details.html', order=order)

    @app.route('/orders/<int:order_id>/cancel', methods=['POST'])
    @login_required
    def cancel_order(order_id):
        order = Order.query.get_or_404(order_id)

        if order.status == 'Ожидается':
            order.status = 'Отменён'
            db.session.commit()
            flash('Заказ успешно отменён', 'info')
        else:
            flash('Нельзя отменить заказ со статусом: ' + order.status, 'error')
        return redirect(url_for('order_details', order_id=order.id))
