from app import create_app
from models import db

app = create_app()

with app.app_context():
    print("Apagando tabelas...")
    db.drop_all()
    print("Criando tabelas...")
    db.create_all()
    print("Banco recriado com sucesso!")