from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, Category, Area, ChecklistTemplate
from utils.helpers import login_required

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings")
@login_required
def index():
    categories = Category.query.all()
    areas = Area.query.all()
    templates = ChecklistTemplate.query.all()
    parents = [t for t in templates if not t.parent_id]

    return render_template(
        "settings.html", 
        categories=categories, 
        areas=areas, 
        templates=templates,
        parents=parents,
        possible_parents=parents
    )

@settings_bp.route("/settings/category/add", methods=["POST"])
@login_required
def add_category():
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    name = request.form.get("name")
    if name:
        db.session.add(Category(name=name))
        db.session.commit()
        flash(f"Categoria '{name}' adicionada com sucesso!", "success")
    return redirect(url_for("settings.index"))

@settings_bp.route("/settings/category/delete/<int:id>", methods=["POST", "GET"])
@login_required
def delete_category(id):
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    item = Category.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash(f"Categoria '{item.name}' removida.", "success")
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir: a categoria está vinculada a solicitações existentes.", "danger")
    return redirect(url_for("settings.index"))

@settings_bp.route("/settings/area/add", methods=["POST"])
@login_required
def add_area():
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    name = request.form.get("name")
    if name:
        db.session.add(Area(name=name))
        db.session.commit()
        flash(f"Área '{name}' adicionada com sucesso!", "success")
    return redirect(url_for("settings.index"))

@settings_bp.route("/settings/area/delete/<int:id>", methods=["POST", "GET"])
@login_required
def delete_area(id):
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    item = Area.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash(f"Área '{item.name}' removida.", "success")
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir: a área está vinculada a itens de checklist em uso.", "danger")
    return redirect(url_for("settings.index"))

@settings_bp.route("/settings/template/add", methods=["POST"])
@login_required
def add_template():
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    description = request.form.get("description")
    area_id = request.form.get("area_id")
    parent_id = request.form.get("parent_id")

    if description and area_id:
        new_template = ChecklistTemplate(
            description=description,
            area_id=area_id,
            parent_id=int(parent_id) if parent_id else None,
            item_type="group" if not parent_id else "task"
        )
        db.session.add(new_template)
        db.session.commit()
        flash("Item do template adicionado com sucesso!", "success")
    return redirect(url_for("settings.index"))

@settings_bp.route("/settings/template/delete/<int:id>", methods=["POST", "GET"])
@login_required
def delete_template(id):
    if not session.get("is_admin"):
        flash("Acesso não autorizado.", "danger")
        return redirect(url_for("requests.index"))

    item = ChecklistTemplate.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash("Item do template removido com sucesso.", "success")
    except Exception:
        db.session.rollback()
        flash("Erro ao remover o item: ele pode estar vinculado a solicitações existentes.", "danger")
    return redirect(url_for("settings.index"))

@settings_bp.route('/template/<int:id>/toggle_default', methods=['POST'])
def toggle_template_default(id):
    template = ChecklistTemplate.query.get_or_404(id)
    template.is_default = not template.is_default
    db.session.commit()
    return redirect(url_for('settings.index'))