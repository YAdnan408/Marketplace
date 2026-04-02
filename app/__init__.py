from flask import Flask
from .extensions import db, migrate


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # ── Load config ───────────────────────────────────────────────────────────
    from config import Config
    app.config.from_object(Config)

    # ── Init extensions ───────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)

    # ── Register blueprints ───────────────────────────────────────────────────

    # Frontend (page rendering)
    from .frontend.routes import frontend_bp
    from .frontend.customer.routes import customer_frontend_bp
    from .frontend.seller.routes import seller_frontend_bp
    app.register_blueprint(frontend_bp)
    app.register_blueprint(customer_frontend_bp)
    app.register_blueprint(seller_frontend_bp)

    # Modules (API)
    from .modules.user.routes import user_bp
    from .modules.product.routes import product_bp
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)

    # ── Import models so Flask-Migrate can detect them ────────────────────────
    from .models import customer, seller, product, category, order, order_item  # noqa

    return app
