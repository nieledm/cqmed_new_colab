from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, AccessRequest, ChecklistItem, ChecklistTemplate, Category, Area
from utils.helpers import login_required, calculate_global_status, organize_checklist_tree
from services.webhook_service import send_to_n8n

requests_bp = Blueprint("requests", __name__)

@requests_bp.route("/")
@login_required
def index():
    reqs = AccessRequest.query.order_by(AccessRequest.created_at.desc()).all()
    in_progress = []
    closed = []

    for r in reqs:
        status = calculate_global_status(r.checklist_items)
        r.global_status = status 
        
        if status == "concluido":
            closed.append(r)
        else:
            in_progress.append(r)
    
    categories = Category.query.filter_by(active=True).all()
    areas = Area.query.filter_by(active=True).all()
    templates = ChecklistTemplate.query.filter_by(is_active=True).all()

    return render_template(
        "index.html", 
        in_progress=in_progress,
        closed=closed,
        categories=categories,
        areas=areas,
        checklist_templates=templates
    )

@requests_bp.route("/request/new", methods=["POST"])
@login_required
def create_request():
    data = request.form
    try:
        sd = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date() if data.get("start_date") else None
        ed = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date() if data.get("end_date") else None
    except ValueError:
        sd, ed = None, None

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
    db.session.commit()

    selected_ids = request.form.getlist("checklist_items")
    if selected_ids:
        templates = ChecklistTemplate.query.filter(ChecklistTemplate.id.in_(selected_ids)).all()
        template_to_item_map = {}

        parents = [t for t in templates if not t.parent_id]
        children = [t for t in templates if t.parent_id]

        for t in parents:
            item = ChecklistItem(
                request_id=new_req.id,
                description=t.description,
                area_id=t.area_id,
                item_type=t.item_type,
                status="pending"
            )
            db.session.add(item)
            db.session.flush()
            template_to_item_map[t.id] = item.id

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
    
    try:
        cat_name = new_req.category.name if new_req.category else "Sem Categoria"
        if new_req.start_date:
            info_inicio = f"Categoria: {cat_name} | WhatsApp: {new_req.whatsapp_number}"
            info_fim = "Data prevista no contrato. Verificar renovação."
            send_to_n8n(
                new_req.collaborator_name, 
                "INICIO DO COLABORADOR ", 
                new_req.start_date, 
                info_inicio, 
                "FINALIZAÇÃO DO COLABORADOR ", 
                new_req.end_date, 
                info_fim
            )
    except Exception as e:
        print(f"Erro ao enviar para n8n: {e}")
    
    return redirect(url_for("requests.request_detail", request_id=new_req.id))

@requests_bp.route("/request/<int:request_id>")
@login_required
def request_detail(request_id):
    req = AccessRequest.query.get_or_404(request_id)
    checklist_tree = organize_checklist_tree(req.checklist_items)
    global_status = calculate_global_status(req.checklist_items)

    return render_template(
        "request.html",
        req=req,
        checklist_tree=checklist_tree,
        global_status=global_status,
    )

@requests_bp.route("/checklist/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_checklist(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    item.status = "done" if item.status == "pending" else "pending"
    item.updated_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("requests.request_detail", request_id=item.request_id))

@requests_bp.route("/request/<int:request_id>/revoke", methods=["POST"])
@login_required
def create_revocation(request_id):
    original_req = AccessRequest.query.get_or_404(request_id)
    
    revocation = AccessRequest(
        collaborator_name=original_req.collaborator_name,
        category_id=original_req.category_id,
        request_type="OFFBOARDING",
        email_contact=original_req.email_contact,
        created_at=datetime.utcnow()
    )
    db.session.add(revocation)
    db.session.commit()

    original_items = ChecklistItem.query.filter_by(request_id=original_req.id, status="done").all()
    id_map = {}

    parents = [i for i in original_items if not i.parent_id]
    children = [i for i in original_items if i.parent_id]

    for p in parents:
        new_item = ChecklistItem(
            request_id=revocation.id,
            description=p.description,
            area_id=p.area_id,
            item_type=p.item_type,
            status="pending"
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
    return redirect(url_for("requests.request_detail", request_id=revocation.id))

@requests_bp.route("/request/<int:request_id>/edit", methods=["GET", "POST"])
@login_required
def edit_request(request_id):
    req = AccessRequest.query.get_or_404(request_id)

    if request.method == "POST":
        data = request.form

        req.collaborator_name = data.get("collaborator_name")
        req.category_id = data.get("category_id")
        req.email_contact = data.get("email_contact")
        req.whatsapp_number = data.get("whatsapp_number")

        try:
            if data.get("start_date"):
                req.start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
            if data.get("end_date"):
                req.end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()
        except ValueError:
            pass

        selected_template_ids = [int(i) for i in request.form.getlist("checklist_items") if i.isdigit()]
        selected_templates = ChecklistTemplate.query.filter(ChecklistTemplate.id.in_(selected_template_ids)).all() if selected_template_ids else []
        selected_descriptions = {t.description for t in selected_templates}

        for item in list(req.checklist_items):
            if item.description not in selected_descriptions:
                db.session.delete(item)

        db.session.flush()

        existing_descriptions = {i.description for i in req.checklist_items}
        parent_item_map = {}

        for item in req.checklist_items:
            if not item.parent_id:
                matching_template = next((t for t in selected_templates if t.description == item.description), None)
                if matching_template:
                    parent_item_map[matching_template.id] = item.id

        parents_templates = [t for t in selected_templates if not t.parent_id]
        children_templates = [t for t in selected_templates if t.parent_id]

        for t in parents_templates:
            if t.description not in existing_descriptions:
                new_item = ChecklistItem(
                    request_id=req.id,
                    description=t.description,
                    area_id=t.area_id,
                    item_type=t.item_type,
                    status="pending"
                )
                db.session.add(new_item)
                db.session.flush()
                parent_item_map[t.id] = new_item.id
                existing_descriptions.add(t.description)

        for t in children_templates:
            if t.description not in existing_descriptions:
                parent_item_id = parent_item_map.get(t.parent_id)
                if parent_item_id:
                    new_item = ChecklistItem(
                        request_id=req.id,
                        description=t.description,
                        area_id=t.area_id,
                        item_type=t.item_type,
                        parent_id=parent_item_id,
                        status="pending"
                    )
                    db.session.add(new_item)

        db.session.commit()
        flash("Solicitação atualizada com sucesso!", "success")
        return redirect(url_for("requests.request_detail", request_id=req.id))

    categories = Category.query.filter_by(active=True).all()
    areas = Area.query.filter_by(active=True).all()
    templates = ChecklistTemplate.query.filter_by(is_active=True).all()
    current_item_descriptions = [i.description for i in req.checklist_items]

    return render_template(
        "request_edit.html", 
        req=req,
        categories=categories,
        areas=areas,
        checklist_templates=templates,
        current_item_descriptions=current_item_descriptions
    )