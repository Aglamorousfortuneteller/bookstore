import json
from app import create_app, db
from app.models import Book

app = create_app()

def import_books_from_json(filepath):
    with app.app_context():
        with open(filepath, encoding='utf-8') as f:
            books = json.load(f)
            for b in books:
                book = Book(
                    title=b['title'],
                    author=b['author'],
                    year=b['year'],
                    price=b['price'],
                    genre=b['genre'],
                    cover=b['cover'],
                    description=b['description'],
                    rating=b['rating']
                )
                db.session.add(book)
            db.session.commit()
            print("✅ Книги из JSON успешно импортированы.")

if __name__ == '__main__':
    import_books_from_json('data/books_catalog.json')
