import os
from flask import Flask
from models import db
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

# Carregar .env
load_dotenv()

usuario = os.getenv("USUARIO_DB", "root")
senha = quote_plus(os.getenv("SENHA_DB", ""))
host = os.getenv("HOST_DB", "localhost")
banco = os.getenv("NOME_DB", "onboarding")

def create_app():
	app = Flask(__name__, template_folder="templates")

	app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "chave_secreta_desenvolvimento_123")

	app.config["SQLALCHEMY_DATABASE_URI"] = (
		f"mysql+pymysql://{usuario}:{senha}@{host}/{banco}"
	)

	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	db.init_app(app)

	# Register blueprints
	from rotas import bp as main_bp

	app.register_blueprint(main_bp)

	# Ensure database tables exist
	with app.app_context():
		db.create_all()

	return app


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    create_app().run(host="0.0.0.0", port=port, debug=True)
