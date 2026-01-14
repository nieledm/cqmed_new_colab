from app import create_app
from models import db, Category, Area, ChecklistTemplate

app = create_app()

with app.app_context():
    print("--- Iniciando Populacao do Banco de Dados ---")

    # 1. Criar Áreas
    areas = ["TI", "Lab manager", "RH", "Comunicação"]
    db_areas = {}
    
    for nome in areas:
        area = Area.query.filter_by(name=nome).first()
        if not area:
            area = Area(name=nome)
            db.session.add(area)
            print(f"Criada Área: {nome}")
        db_areas[nome] = area # Guarda para usar nos templates
    
    db.session.commit() # Commit para gerar os IDs das áreas

    # 2. Criar Categorias (Isso resolve o problema do select vazio)
    categorias = [
        "Funcionário/Bolsista Padrão",
        "Colaborador",
        "Funcionário Compras/Contas",
        "Administrador do Sistema",
        "Usuario Externo"
    ]

    for nome in categorias:
        cat = Category.query.filter_by(name=nome).first()
        if not cat:
            db.session.add(Category(name=nome))
            print(f"Criada Categoria: {nome}")

    # 3. Criar Templates de Checklist (Isso resolve a mensagem de 'Nenhum template')
    # Exemplo: Item Pai -> Item Filho
    
    # Template TI
    if "TI" in db_areas:
        area_ti = db_areas["TI"]
        
        # Pai
        email_setup = ChecklistTemplate.query.filter_by(description="Configuração de Email Institucional").first()
        if not email_setup:
            email_setup = ChecklistTemplate(description="Configuração de Email Institucional", area_id=area_ti.id, item_type="group")
            db.session.add(email_setup)
            db.session.flush() # Para ter o ID
            
            # Filhos
            db.session.add(ChecklistTemplate(description="Criar conta no Google Workspace", area_id=area_ti.id, parent_id=email_setup.id))
            db.session.add(ChecklistTemplate(description="Enviar credenciais ao gestor", area_id=area_ti.id, parent_id=email_setup.id))
            print("Criado Template TI: Email")

    # Template RH
    if "RH" in db_areas:
        area_rh = db_areas["RH"]
        if not ChecklistTemplate.query.filter_by(description="Coleta de Documentos").first():
            db.session.add(ChecklistTemplate(description="Coleta de Documentos", area_id=area_rh.id))
            print("Criado Template RH: Documentos")

    db.session.commit()
    print("--- Banco populado com sucesso! ---")