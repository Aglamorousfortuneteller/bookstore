from app.routes.auth_routes import register_auth_routes
from app.routes.book_routes import register_book_routes
from app.routes.cart_routes import register_cart_routes
from app.routes.order_routes import register_order_routes
from app.routes.static_routes import register_static_routes

def register_all_routes(app):
    register_auth_routes(app)
    register_book_routes(app)
    register_cart_routes(app)
    register_order_routes(app)
    register_static_routes(app)