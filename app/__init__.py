# app/__init__.py
from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from .config import Config
# from .models import db  # or however you import db
# from .models import User  # import your models before creating

# app = Flask(__name__)
# Initialize extensions
db = SQLAlchemy()           # Provides ORM capabilities
jwt = JWTManager()          # Handles JWT authentication

# Global set to store revoked JWT token identifiers (jti)
revoked_tokens = set()

def create_app():
    """
    Application factory function.
    Creates and configures the Flask application.
    """
    app = Flask(__name__)

    CORS(app)

    # Load configuration from the Config class
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    jwt.init_app(app)

    # from .models import User  # import your models before creating

    with app.app_context():
        from .models import User  # import your models before creating
        db.create_all()

        # ✅ Move this into the app context
        if not User.query.first():  # Optional: only add users if table is empty
            user1 = User(username="David", email="david@myemail.com", password="1234")
            user2 = User(username="John", email="john@myemail.com", password="5678")

            db.session.add_all([user1, user2])
            db.session.commit()

    # Register the token blocklist loader
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload.get("jti")
        return jti in revoked_tokens

    # Register blueprints for API routes
    from app.routes.api_routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Define a root route that shows all API endpoints
    @app.route("/")
    def home():
        endpoints = []
        # Iterate over all registered routes in the application
        for rule in app.url_map.iter_rules():
            # Skip the static endpoint if you have one
            if rule.endpoint != "static":
                endpoints.append({
                    "endpoint": rule.endpoint,
                    "methods": sorted(list(rule.methods)),
                    "url": str(rule)
                })
        return jsonify({
            "message": "StudySmarter API is running!",
            "available_endpoints": endpoints
        }), 200

    return app
    