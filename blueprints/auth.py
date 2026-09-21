from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User
from services import auth_service

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Preencha o usuário e a senha.", "warning")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()

        # Usuário Local (ex: Administrador)
        if user and not user.is_ldap:
            if not user.check_password(password):
                flash("Usuário ou senha incorretos.", "danger")
                return render_template("login.html")
        # Usuário via LDAP
        else:
            ldap_info = auth_service.authenticate_ldap(username, password)
            if ldap_info is None:
                flash("Credenciais de rede inválidas.", "danger")
                return render_template("login.html")

            if user is None:
                user = User(
                    username=username,
                    name=ldap_info.get("nome", username),
                    is_ldap=True,
                    is_admin=False,
                    is_active=False
                )
                db.session.add(user)
                db.session.commit()

        if not user.is_active:
            flash("Sua conta está inativa ou aguardando aprovação do Administrador.", "warning")
            return render_template("login.html")

        session["user"] = user.username
        session["user_id"] = user.id
        session["is_admin"] = user.is_admin

        flash(f"Bem-vindo(a), {getattr(user, 'name', user.username)}!", "success")
        return redirect(url_for("requests.index"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("auth.login"))