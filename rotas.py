from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, AccessRequest, ChecklistItem, ChecklistTemplate, Category, Area
from funcoes import calculate_global_status, normalize_phone
from datetime import datetime

from webhook_service import send_to_n8n
bp = Blueprint("main", __name__)

# --- FUNÇÃO AUXILIAR PARA ORGANIZAR HIERARQUIA ---
def organize_checklist_tree(items):
    """
    Organiza uma lista plana de itens em um dicionário agrupado por Áreas,
    respeitando a hierarquia Pai -> Filhos.
    """
    # 1. Separar pais e filhos e agrupar por Área
    grouped = {}
    items_map = {item.id: item for item in items}
    
    # Adiciona atributo temporário 'children_list' aos objetos para o template usar
    for item in items:
        item.children_list = []

    # Monta a árvore
    root_items = []
    for item in items:
        if item.parent_id:
            parent = items_map.get(item.parent_id)
            if parent:
                parent.children_list.append(item)
        else:
            root_items.append(item)

    # Agrupa os raízes (que agora contêm seus filhos) por área
    for item in root_items:
        area_name = item.area.name if item.area else "Geral"
        if area_name not in grouped:
            grouped[area_name] = []
        grouped[area_name].append(item)
        
    return grouped

# --- ROTAS PRINCIPAIS ---

@bp.route("/")
def index():
    reqs = AccessRequest.query.order_by(AccessRequest.created_at.desc()).all()
    in_progress = []
    closed = []

    for r in reqs:
        # Recalcula status na hora (ou pode confiar no banco se salvar sempre)
        status = calculate_global_status(r.checklist_items)
        r.global_status = status 
        
        if status == "concluido":
            closed.append(r)
        else:
            in_progress.append(r)
    
    # Carregar dados para os modais de criação
    categories = Category.query.filter_by(active=True).all()
    areas = Area.query.filter_by(active=True).all()
    # Carregar templates apenas "Pais" para a seleção inicial (ou todos, depende da sua UI)
    templates = ChecklistTemplate.query.filter_by(is_active=True).all()

    return render_template("index.html", 
                           in_progress=in_progress,
                           closed=closed,
                           categories=categories,
                           areas=areas,
                           checklist_templates=templates)

@bp.route("/request/new", methods=["POST"])
def create_request():
    # Coleta de dados básicos
    data = request.form
    
    try:
        sd = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else None
        ed = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else None
    except:
        sd, ed = None, None

    # CRIAÇÃO DO OBJETO (Variável new_req)
    new_req = AccessRequest(
        collaborator_name=data.get("collaborator_name"),
        category_id=data.get("category_id"),
        request_type="ONBOARDING",
        start_date=sd,
        end_date=ed,
        email_contact=data.get("email_contact"),
        whatsapp_number=data.get("whatsapp_number")
    )
    db.session.add(new_req)
    db.session.commit() # Commit inicial para ter o ID

    # Lógica de Checklist
    selected_ids = request.form.getlist("checklist_items")
    if selected_ids:
        # Busca todos os templates selecionados
        templates = ChecklistTemplate.query.filter(ChecklistTemplate.id.in_(selected_ids)).all()
        
        # Dicionário para mapear ID_Template -> Novo_Item_Criado
        template_to_item_map = {}

        # 1. Criar PAIS primeiro
        parents = [t for t in templates if not t.parent_id]
        children = [t for t in templates if t.parent_id]

        # Inserir Pais
        for t in parents:
            item = ChecklistItem(
                request_id=new_req.id,
                description=t.description,
                area_id=t.area_id,
                item_type=t.item_type,
                status="pending"
            )
            db.session.add(item)
            db.session.flush() # Gera ID do item
            template_to_item_map[t.id] = item.id

        # Inserir Filhos
        for t in children:
            if t.parent_id in template_to_item_map:
                item = ChecklistItem(
                    request_id=new_req.id,
                    description=t.description,
                    area_id=t.area_id,
                    item_type=t.item_type,
                    parent_id=template_to_item_map[t.parent_id],
                    status="pending"
                )
                db.session.add(item)

    db.session.commit()
    
    # --- INTEGRAÇÃO N8N (CORRIGIDA) ---
    try:
        # Carregar o nome da categoria com segurança
        # (Às vezes o relacionamento não carrega imediato após commit, então garantimos pegando o ID)
        cat_name = "Sem Categoria"
        if new_req.category:
             cat_name = new_req.category.name
        
        if new_req.start_date:
            info_inicio = f"Categoria: {cat_name} | WhatsApp: {new_req.whatsapp_number}"
            info_fim = f"Data prevista no contrato. Verificar renovação."
            send_to_n8n(new_req.collaborator_name, "INICIO DO COLABORADOR ", new_req.start_date, info_inicio, "FINALIZAÇÃO DO COLABORADOR ", new_req.end_date, info_fim)
            

            # def send_to_n8n(collaborator_name, 
            #           start_event_type, 
            #           start_date_obj, 
            #           start_extra_info,
            #           end_event_type, 
            #           end_date_obj, 
            #           end_extra_info,):
                    
    except Exception as e:
        print(f"Erro ao enviar para n8n: {e}") 
    # -----------------------------------------------------
    
    return redirect(url_for("main.request_detail", request_id=new_req.id))

@bp.route("/request/<int:request_id>/revoke", methods=["POST"])
def create_revocation(request_id):
    """
    Cria uma solicitação de DESLIGAMENTO baseada em uma admissão existente.
    """
    original_req = AccessRequest.query.get_or_404(request_id)
    
    # Cria nova requisição de desligamento
    revocation = AccessRequest(
        collaborator_name=original_req.collaborator_name,
        category_id=original_req.category_id,
        request_type="OFFBOARDING", # Flag importante para o Frontend
        email_contact=original_req.email_contact,
        created_at=datetime.utcnow()
    )
    db.session.add(revocation)
    db.session.commit()

    # Copia os itens do checklist original
    # Lógica: Se estava "Done" na admissão, precisa ser revogado (cria item Pending)
    # Se nunca foi feito, não precisa revogar.
    original_items = ChecklistItem.query.filter_by(request_id=original_req.id, status="done").all()
    
    # Mapeamento para manter hierarquia
    id_map = {} 

    # Primeiro copiamos tudo como "pending" na nova requisição
    # No Frontend de Offboarding: "Pending" = Usuário tem acesso (Checked). "Done" = Acesso removido (Unchecked/Riscado).
    
    # Separa pais e filhos do original
    parents = [i for i in original_items if not i.parent_id]
    children = [i for i in original_items if i.parent_id]

    for p in parents:
        new_item = ChecklistItem(
            request_id=revocation.id,
            description=p.description,
            area_id=p.area_id,
            item_type=p.item_type,
            status="pending" # Pendente de revogação
        )
        db.session.add(new_item)
        db.session.flush()
        id_map[p.id] = new_item.id
    
    for c in children:
        if c.parent_id in id_map:
            new_item = ChecklistItem(
                request_id=revocation.id,
                description=c.description,
                area_id=c.area_id,
                item_type=c.item_type,
                parent_id=id_map[c.parent_id],
                status="pending"
            )
            db.session.add(new_item)
    
    db.session.commit()
    flash("Processo de desligamento iniciado!", "warning")
    return redirect(url_for("main.request_detail", request_id=revocation.id))

@bp.route("/request/<int:request_id>")
def request_detail(request_id):
    req = AccessRequest.query.get_or_404(request_id)
    items = req.checklist_items
    
    # Usa a função auxiliar para organizar a árvore
    checklist_tree = organize_checklist_tree(items)
    global_status = calculate_global_status(items)

    return render_template(
        "request.html",
        req=req,
        checklist_tree=checklist_tree, # Passamos a árvore, não lista plana
        global_status=global_status,
    )

@bp.route("/checklist/<int:item_id>/toggle", methods=["POST"])
def toggle_checklist(item_id):
    """Rota unificada para marcar/desmarcar"""
    item = ChecklistItem.query.get_or_404(item_id)
    
    # Se estava pending vira done, se done vira pending
    item.status = "done" if item.status == "pending" else "pending"
    item.updated_at = datetime.utcnow()
    
    db.session.commit()
    return redirect(url_for("main.request_detail", request_id=item.request_id))

# --- ROTAS DE CONFIGURAÇÃO (AREA/TEMPLATES) ---
@bp.route("/settings/areas", methods=["GET", "POST"])
def manage_areas():
    if request.method == "POST":
        name = request.form.get("name")
        if name:
            db.session.add(Area(name=name))
            db.session.commit()
        return redirect(url_for("main.manage_areas"))
    
    areas = Area.query.all()
    return render_template("settings_areas.html", areas=areas)

@bp.route("/settings/templates", methods=["GET", "POST"])
def manage_templates():
    if request.method == "POST":
        desc = request.form.get("description")
        area_id = request.form.get("area_id")
        parent_id = request.form.get("parent_id") # Opcional
        
        if desc and area_id:
            new_t = ChecklistTemplate(
                description=desc, 
                area_id=area_id, 
                parent_id=parent_id if parent_id else None
            )
            db.session.add(new_t)
            db.session.commit()
        return redirect(url_for("main.manage_templates"))

    templates = ChecklistTemplate.query.all()
    areas = Area.query.filter_by(active=True).all()
    return render_template("settings_templates.html", templates=templates, areas=areas)

# --- ROTAS DE CONFIGURAÇÃO (CRUD) ---

@bp.route("/settings")
def settings():
    # Busca dados para popular as tabelas
    categories = Category.query.all()
    areas = Area.query.all()
    
    # Busca templates e organiza para exibição (Pais com seus Filhos)
    templates = ChecklistTemplate.query.all()
    
    # Separa pais e filhos para facilitar a exibição
    parents = [t for t in templates if not t.parent_id]
    
    # Para o dropdown do formulário (apenas pais podem ter filhos)
    possible_parents = parents 

    return render_template("settings.html", 
                           categories=categories, 
                           areas=areas, 
                           templates=templates,
                           parents=parents,
                           possible_parents=possible_parents)

# --- CRUD CATEGORIAS ---
@bp.route("/settings/category/add", methods=["POST"])
def add_category():
    name = request.form.get("name")
    if name:
        db.session.add(Category(name=name))
        db.session.commit()
    return redirect(url_for("main.settings"))

@bp.route("/settings/category/delete/<int:id>")
def delete_category(id):
    item = Category.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception:
        # Em produção, ideal tratar erro de chave estrangeira (se já estiver em uso)
        db.session.rollback()
    return redirect(url_for("main.settings"))

# --- CRUD ÁREAS ---
@bp.route("/settings/area/add", methods=["POST"])
def add_area():
    name = request.form.get("name")
    if name:
        db.session.add(Area(name=name))
        db.session.commit()
    return redirect(url_for("main.settings"))

@bp.route("/settings/area/delete/<int:id>")
def delete_area(id):
    item = Area.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("main.settings"))

# --- CRUD CHECKLIST TEMPLATES ---
@bp.route("/settings/template/add", methods=["POST"])
def add_template():
    description = request.form.get("description")
    area_id = request.form.get("area_id")
    parent_id = request.form.get("parent_id") # Pode ser vazio
    
    if description and area_id:
        new_template = ChecklistTemplate(
            description=description,
            area_id=area_id,
            parent_id=parent_id if parent_id else None,
            item_type="group" if not parent_id else "task" # Se não tem pai, é grupo. Se tem, é tarefa.
        )
        db.session.add(new_template)
        db.session.commit()
    return redirect(url_for("main.settings"))

@bp.route("/settings/template/delete/<int:id>")
def delete_template(id):
    item = ChecklistTemplate.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return redirect(url_for("main.settings"))