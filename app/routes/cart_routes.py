from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import User, Book, CartItem, Review, Order, OrderItem
from ..extensions import db


def register_cart_routes(app):
    @app.route('/cart')
    @login_required
    def view_cart():
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum(item.book.price * item.quantity for item in cart_items)

        if request.args.get('deleted') == '1':
            flash("Книга удалена из корзины", "info")


        return render_template('cart.html', cart_items=cart_items, total=total)


    @app.route('/add_to_cart/<int:book_id>', methods=['POST'])
    def add_to_cart(book_id):
        book = Book.query.get_or_404(book_id)
        reviews = Review.query.filter_by(book_id=book_id).all()
        prev = request.form.get('prev') or url_for('index')

        if not current_user.is_authenticated:
            flash('Сначала войдите в аккаунт, чтобы добавить книгу в корзину.', 'login_error')
            return render_template('book_detail.html', book=book, reviews=reviews, prev=prev)

        try:
            quantity = max(int(request.form.get('quantity', 1)), 1)
        except ValueError:
            quantity = 1

        existing_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            item = CartItem(user_id=current_user.id, book_id=book_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        flash('Книга добавлена в корзину!', 'cart_added')
        return render_template('book_detail.html', book=book, reviews=reviews, prev=prev)


    @app.route('/cart/update/<int:item_id>', methods=['POST'])
    @login_required
    def update_cart_item(item_id):
        item = CartItem.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return "Недоступно", 403

        try:
            quantity = int(request.form['quantity'])
            if quantity < 1:
                db.session.delete(item)
                db.session.commit()
                return redirect(url_for('view_cart', deleted='1'))
            else:
                item.quantity = quantity
                db.session.commit()
                return '', 204  # OK, no content
        except Exception:
            flash("Ошибка при обновлении", "error")
            return redirect(url_for('view_cart'))

    @app.route('/cart/remove/<int:item_id>', methods=['POST'])
    @login_required
    def remove_cart_item(item_id):
        item = CartItem.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return "Недоступно", 403

        db.session.delete(item)
        db.session.commit()
        flash("Книга удалена из корзины", "info")
        return redirect(url_for('view_cart'))


    @app.route('/remove_selected', methods=['POST'])
    @login_required
    def remove_selected():
        selected_ids = request.form.getlist('selected_items')
        if not selected_ids:
            flash("Выберите хотя бы одну книгу для удаления", "error")
        else:
            deleted = CartItem.query.filter(
                CartItem.id.in_(selected_ids),
                CartItem.user_id == current_user.id
            ).delete(synchronize_session='fetch')
            db.session.commit()
            if deleted:
                flash("Выбранные книги удалены", "info")
        return redirect(url_for('view_cart'))


    @app.route('/cart/total')
    @login_required
    def cart_total():
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = round(sum(item.book.price * item.quantity for item in cart_items), 2)

        return jsonify({'total': total})

