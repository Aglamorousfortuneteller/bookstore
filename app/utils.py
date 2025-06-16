import json
from .models import Book
from .extensions import db


GENRE_TO_CATEGORY = {
    "Фантастика": "Художественная литература",
    "Фэнтези": "Художественная литература",
    "Приключения": "Художественная литература",
    "Роман": "Художественная литература",
    "Детектив": "Художественная литература",

    "Саморазвитие": "Нехудожественная литература",
    "История": "Нехудожественная литература",

    "Научная литература": "Учебная литература",

    "Детская литература": "Детская литература",

    "Бизнес": "Бизнес-литература",

    "Манга": "Комиксы, манга, артбуки",
    "Комиксы": "Комиксы, манга, артбуки"
}



def load_books_from_json(filepath):
    try:
        with open(filepath, encoding='utf-8') as f:
            books = json.load(f)
            for b in books:
                exists = Book.query.filter_by(title=b['title'], author=b['author']).first()
                if not exists:
                    genre = b.get('genre')
                    category = GENRE_TO_CATEGORY.get(genre, 'Другое')  # добавляю категорию

                    book = Book(
                        title=b['title'],
                        author=b['author'],
                        year=b['year'],
                        price=b['price'],
                        genre=genre,
                        category=category,
                        cover=b['cover'],
                        description=b['description'],
                        rating=b['rating']
                    )
                    db.session.add(book)
            db.session.commit()
            print("Книги загружены (без дублей)")
    except Exception as e:
        print(f"Ошибка при загрузке книг: {e}")


