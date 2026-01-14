from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabelas de Configuração (Dinâmicas para editar no front)
class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.name

class Area(db.Model):
    __tablename__ = "areas"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.name

class AccessRequest(db.Model):
    __tablename__ = "access_requests"

    id = db.Column(db.Integer, primary_key=True)
    request_type = db.Column(db.String(20), default="ONBOARDING") # ONBOARDING ou OFFBOARDING
    collaborator_name = db.Column(db.String(200), nullable=False)
    
    # FK para Categoria
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    category = db.relationship("Category")

    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    email_contact = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Status global (calculado ou salvo para performance)
    global_status = db.Column(db.String(20), default="aguardando")

    checklist_items = db.relationship(
        "ChecklistItem", backref="request", cascade="all, delete-orphan"
    )

class ChecklistTemplate(db.Model):
    __tablename__ = "checklist_templates"
    
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("checklist_templates.id"), nullable=True)
    description = db.Column(db.String(255), nullable=False)
    
    # FK para Area
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
    
    # Guardamos o nome da área como string ou ID. 
    # Como áreas podem ser deletadas, guardar o ID é melhor, mas para histórico string é mais seguro.
    # Vamos manter FK para manter consistência no painel.
    area_id = db.Column(db.Integer, db.ForeignKey("areas.id"), nullable=True)
    area = db.relationship("Area")

    # Status: pending (pendente/tem acesso) | done (feito/removido)
    status = db.Column(db.String(20), default="pending")
    item_type = db.Column(db.String(20), default="task")
    updated_at = db.Column(db.DateTime)
    updated_by = db.Column(db.String(100))
    
    subitems = db.relationship(
        "ChecklistItem",
        backref=db.backref('parent', remote_side=[id]),
        cascade="all, delete-orphan"
    )