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
        "Usuario Externo",
        "Outros"
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
                
        if not ChecklistTemplate.query.filter_by (description="Adicionar ao grupo de email CQMED").first():
            db.session.add(ChecklistTemplate(description="Adicionar ao grupo de email CQMED", area_id=area_ti.id))
            print("Criado Template TI: Grupo de Email")

        if not ChecklistTemplate.query.filter_by (description="Adicionar  à intranet").first():
            db.session.add(ChecklistTemplate(description="Adicionar à intranet", area_id=area_ti.id))
            print("Criado Template TI: Intranet")

        if not ChecklistTemplate.query.filter_by (description="Adicionar ao WhatsApp").first():
            db.session.add(ChecklistTemplate(description="Adicionar ao WhatsApp", area_id=area_ti.id))
            print("Criado Template TI: WhatsApp")
        
        if not ChecklistTemplate.query.filter_by (description="Fazer VPN").first():
            db.session.add(ChecklistTemplate(description="Fazer VPN", area_id=area_ti.id))
            print("Criado Template TI: VPN")

        if not ChecklistTemplate.query.filter_by (description="Criar usuário no servidor").first():
            db.session.add(ChecklistTemplate(description="Criar usuário no servidor", area_id=area_ti.id))
            print("Criado Template TI: Usuário no Servidor")

        #Pai
        mesa_setup = ChecklistTemplate.query.filter_by(description="Mesa/Desktop").first()
        if not ChecklistTemplate.query.filter_by (description="Mesa").first():
            if not mesa_setup:
                mesa_setup = ChecklistTemplate(description="Mesa/Desktop", area_id=area_ti.id, item_type="group")
                db.session.add(mesa_setup)
                db.session.flush() # Para ter o ID
            
            #Filhos
            db.session.add(ChecklistTemplate(description="Mesa", area_id=area_ti.id, parent_id=mesa_setup.id))
            db.session.add(ChecklistTemplate(description="Desktop", area_id=area_ti.id, parent_id=mesa_setup.id))
            print("Criado Template TI: Mesa/Desktop")

        # Pai Biometria
        biometria_setup = ChecklistTemplate.query.filter_by(description="Biometria").first()
        if not biometria_setup:
            biometria_setup = ChecklistTemplate(description="Biometria", area_id=area_ti.id, item_type="group")
            db.session.add(biometria_setup)
            db.session.flush() # Para ter o ID
            
            # Filhos Biometria
            db.session.add(ChecklistTemplate(description="CQMED", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="CQMED - Comercial", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Cultura de Células", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Cultura de Células - Comercial", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Massas (LACTAD)", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Massas (LACTAD) - Comercial", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Warehouse (LACTAD)", area_id=area_ti.id, parent_id=biometria_setup.id))
            db.session.add(ChecklistTemplate(description="Warehouse (LACTAD) - Comercial", area_id=area_ti.id, parent_id=biometria_setup.id))
            print("Criado Template TI: Biometria")

        # Pai Softwares
        softwares_setup = ChecklistTemplate.query.filter_by(description="Softwares").first()
        if not softwares_setup:
            softwares_setup = ChecklistTemplate(description="Softwares", area_id=area_ti.id, item_type="group")
            db.session.add(softwares_setup)
            db.session.flush() # Para ter o ID
            
            # Filhos Softwares
            db.session.add(ChecklistTemplate(description="Scarab", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Phenix", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="XDS", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="CCP4", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Pandda", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="CryoSPARC", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="AlphaFold3", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Schrodinger", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="SnapGene", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Geneius", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Prism", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Rstudio Server", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="FindMolecues", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="chemdraw", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Inkscape", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Pymol", area_id=area_ti.id, parent_id=softwares_setup.id))
            db.session.add(ChecklistTemplate(description="Mass Lynx", area_id=area_ti.id, parent_id=softwares_setup.id))
            print("Criado Template TI: Softwares")

        # Pai Acesso a servidores de bioinformatica
        bioinfo_setup = ChecklistTemplate.query.filter_by(description="Acesso a Servidores de Bioinformática").first()
        if not bioinfo_setup:
            bioinfo_setup = ChecklistTemplate(description="Acesso a Servidores de Bioinformática", area_id=area_ti.id, item_type="group")
            db.session.add(bioinfo_setup)
            db.session.flush() # Para ter o ID
            
            # Filhos Bioinfo
            db.session.add(ChecklistTemplate(description="Hypatia", area_id=area_ti.id, parent_id=bioinfo_setup.id))
            db.session.add(ChecklistTemplate(description="Target", area_id=area_ti.id, parent_id=bioinfo_setup.id))
            db.session.add(ChecklistTemplate(description="Fujita", area_id=area_ti.id, parent_id=bioinfo_setup.id))
            db.session.add(ChecklistTemplate(description="Oscuria", area_id=area_ti.id, parent_id=bioinfo_setup.id))
            print("Criado Template TI: Acesso a Servidores de Bioinformática")


    # Template RH
    if "RH" in db_areas:
        area_rh = db_areas["RH"]
        if not ChecklistTemplate.query.filter_by(description="Coleta de Documentos").first():
            db.session.add(ChecklistTemplate(description="Coleta de Documentos", area_id=area_rh.id))
            print("Criado Template RH: Documentos")

    db.session.commit()
    print("--- Banco populado com sucesso! ---")