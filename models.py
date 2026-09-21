from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    
    # Se for usuário local, terá hash de senha. Se for LDAP, password_hash é None.
    password_hash = db.Column(db.String(255), nullable=True)
    
    is_ldap = db.Column(db.Boolean, default=True)      # True = Valida no LDAP | False = Valida local
    is_admin = db.Column(db.Boolean, default=False)     # Permissão de admin na aplicação
    is_active = db.Column(db.Boolean, default=True)     # Permite bloquear ou conceder acesso
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

class Area(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

class AccessRequest(db.Model):
    __tablename__ = "access_requests"

    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), default="ONBOARDING")
    collaborator_name = db.Column(db.String(200), nullable=False)
    
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    category = db.relationship("Category")

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    email_contact = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    global_status = db.Column(db.String(20), default="aguardando")

    checklist_items = db.relationship(
        "ChecklistItem", backref="request", cascade="all, delete-orphan"
    )

class ChecklistTemplate(db.Model):
    __tablename__ = "checklist_templates"
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("checklist_templates.id"), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=False)
    area = db.relationship("Area")

    item_type = db.Column(db.String(20), default="task") 
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subtemplates = db.relationship(
        "ChecklistTemplate",
        backref=db.backref('parent', remote_side=[id]),
        lazy="dynamic"
    )

class ChecklistItem(db.Model):
    __tablename__ = "checklist_items"

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("access_requests.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("checklist_items.id"), nullable=True)
    
    description = db.Column(db.String(255), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)
    area = db.relationship("Area")

    status = db.Column(db.String(20), default="pending")
    item_type = db.Column(db.String(20), default="task")
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(100))
    
    subitems = db.relationship(
        "ChecklistItem",
        backref=db.backref('parent', remote_side=[id]),
        cascade="all, delete-orphan"
    )