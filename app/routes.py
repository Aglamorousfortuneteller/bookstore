from flask import render_template, request, redirect, url_for, flash, current_app, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, Book, CartItem, Review, Order, OrderItem
from .extensions import db

app = current_app

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    if query:
        books = Book.query.filter(
            Book.title.ilike(f"%{query}%") | Book.author.ilike(f"%{query}%")
        ).all()
    else:
        books = Book.query.all()

    top_books = Book.query.order_by(Book.rating.desc()).limit(3).all()

    return render_template('index.html', books=books, top_books=top_books)



@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        flash("Введите поисковый запрос.", "info")
        return redirect(url_for('index'))
    
    books = Book.query.filter(
        Book.title.ilike(f'%{query}%') |
        Book.author.ilike(f'%{query}%') |
        Book.genre.ilike(f'%{query}%')).all()
    
    return render_template('search_results.html', books=books, query=query)



@app.route('/genre/<genre_name>')
def books_by_genre(genre_name):
    books = Book.query.filter_by(genre=genre_name).all()
    return render_template('genre.html', genre=genre_name, books=books)

@app.route('/category/<category_name>')
def books_by_category(category_name):
    genre_filter = request.args.get('genre')
    if category_name == "Все книги":
        query = Book.query
        if genre_filter:
            query = query.filter_by(genre=genre_filter)
        books = query.all()
        genres_in_category = sorted({book.genre for book in Book.query.all() if book.genre})
    else:
        query = Book.query.filter_by(category=category_name)
        if genre_filter:
            query = query.filter_by(genre=genre_filter)
        books = query.all()
        genres_in_category = sorted({book.genre for book in Book.query.filter_by(category=category_name).all() if book.genre})

    return render_template('category.html', category=category_name, books=books, genres_in_category=genres_in_category, selected_genre=genre_filter)

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


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    reviews = Review.query.filter_by(book_id=book_id).all()
    prev = request.args.get('prev') or request.form.get('prev') or url_for('index')

    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('login'))

        text = request.form['text']
        rating = int(request.form['rating'])
        new_review = Review(user_id=current_user.id, book_id=book_id, text=text, rating=rating)
        db.session.add(new_review)
        db.session.commit()

        all_ratings = [r.rating for r in Review.query.filter_by(book_id=book_id).all()]
        avg_review_rating = sum(all_ratings) / len(all_ratings)
        book.rating = round(avg_review_rating, 2)
        db.session.commit()

        flash('Ваш отзыв успешно добавлен!', 'review')
        return redirect(url_for('book_detail', book_id=book_id, prev=prev))

    return render_template('book_detail.html', book=book, reviews=reviews, prev=prev)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']

        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже зарегистрирован.', 'error')
            return redirect(url_for('register'))

        if phone and User.query.filter_by(phone=phone).first():
            flash('Пользователь с таким номером телефона уже зарегистрирован.', 'error')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(request.form['password'])

        session['pending_user'] = {
            'first_name': request.form['first_name'],
            'last_name': request.form['last_name'],
            'email': email,
            'phone': phone,
            'password_hash': hashed_password,
        }
        return redirect(url_for('confirm_registration'))
    
    return render_template('register.html')


@app.route('/confirm', methods=['GET', 'POST'])
def confirm_registration():
    if request.method == 'POST':
        code = request.form['code']
        if code == '1111':
            data = session.get('pending_user')
            if data:
                user = User(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    phone=data['phone'],
                    password_hash=data['password_hash']
                )
                db.session.add(user)
                db.session.commit()
                session.pop('pending_user', None)
                flash('Регистрация завершена. Теперь вы можете войти.', 'success')
                return redirect(url_for('login'))
            flash('Данные не найдены. Начните регистрацию заново.', 'error')
            return redirect(url_for('register'))
        else:
            flash('Неверный код подтверждения.', 'error')
    return render_template('confirm.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Вы вошли в систему.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.date.desc()).all()
    return render_template('orders.html', orders=orders)


@app.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']

    if not current_user.check_password(current_password):
        flash('Текущий пароль неверен.', 'error')
        return redirect(url_for('profile'))

    current_user.set_password(new_password)
    db.session.commit()
    flash('Пароль успешно обновлён.', 'success')
    return redirect(url_for('profile'))


@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    if request.method == 'POST':
        user = User.query.get(current_user.id)
        logout_user()
        db.session.delete(user)
        db.session.commit()
        return render_template('account_deleted.html')

@app.route('/cart')
@login_required
def view_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.book.price * item.quantity for item in cart_items)

    if request.args.get('deleted') == '1':
        flash("Книга удалена из корзины", "info")


    return render_template('cart.html', cart_items=cart_items, total=total)


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


@app.route('/cart/total')
@login_required
def cart_total():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = round(sum(item.book.price * item.quantity for item in cart_items), 2)

    return jsonify({'total': total})






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