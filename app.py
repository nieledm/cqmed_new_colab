import os
from flask import Flask
from models import db
from dotenv import load_dotenv
from urllib.parse import quote_plus
from blueprints import auth_bp, requests_bp, settings_bp, users_bp
from flask_jwt_extended import JWTManager

load_dotenv()

usuario = os.getenv("POSTGRES_USER")
senha = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
banco = os.getenv("POSTGRES_DB")

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave_secreta_desenvolvimento_123")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_chave_secreta_456")

    # String de conexão PostgreSQL
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{usuario}:{senha}@{host}:{port}/{banco}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(requests_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(users_bp)

    return app

if __name__ == "__main__":
    port_app = int(os.getenv("PORT", 5050))
    create_app().run(host="0.0.0.0", port=port_app, debug=True)