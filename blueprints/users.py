from flask import Blueprint, render_template, redirect, url_for, flash, session
from models import db, User
from utils.helpers import login_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/users")
@login_required
def manage_users():
    if not session.get("is_admin"):
        flash("Acesso permitido apenas para Administradores.", "danger")
        return redirect(url_for("requests.index"))
    
    users = User.query.order_by(User.id.desc()).all()
    return render_template("users.html", users=users)

@users_bp.route("/users/<int:user_id>/toggle-access", methods=["POST"])
@login_required
def toggle_user_access(user_id):
    if not session.get("is_admin"):
        flash("Ação não autorizada.", "danger")
        return redirect(url_for("requests.index"))

    user = User.query.get_or_404(user_id)
    if user.id == session.get("user_id"):
        flash("Você não pode alterar seu próprio acesso.", "warning")
        return redirect(url_for("users.manage_users"))

    user.is_active = not user.is_active
    db.session.commit()
    
    status_msg = "autorizado" if user.is_active else "bloqueado"
    flash(f"Acesso do usuário '{user.username}' foi {status_msg}.", "success")
    return redirect(url_for("users.manage_users"))

@users_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
def toggle_user_admin(user_id):
    if not session.get("is_admin"):
        flash("Ação não autorizada.", "danger")
        return redirect(url_for("requests.index"))

    user = User.query.get_or_404(user_id)
    if user.id == session.get("user_id"):
        flash("Você não pode alterar suas próprias permissões de Admin.", "warning")
        return redirect(url_for("users.manage_users"))

    user.is_admin = not user.is_admin
    db.session.commit()

    role_msg = "promovido a Administrador" if user.is_admin else "removido de Administrador"
    flash(f"Usuário '{user.username}' foi {role_msg}.", "success")
    return redirect(url_for("users.manage_users"))