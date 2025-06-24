from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from ..models import User, Book, CartItem, Review, Order, OrderItem
from ..extensions import db

def register_book_routes(app):
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