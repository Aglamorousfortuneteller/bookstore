from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from ..models import User
from ..extensions import db


def register_auth_routes(app):
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

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')


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
