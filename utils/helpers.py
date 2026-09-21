from functools import wraps
import re
from flask import session, flash, redirect, url_for
from utils.country_codes import COUNTRY_CODES

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def calculate_global_status(items):
    """Calcula se a solicitação está concluída ou em andamento com base nos itens."""
    if not items:
        return "pendente"
    is_finished = all(
        getattr(item, 'completed', False) or getattr(item, 'status', '') == 'done'
        for item in items
    )
    return "concluido" if is_finished else "em_andamento"

def organize_checklist_tree(items):
    """Organiza os itens em um dicionário agrupado por áreas mantendo a hierarquia Pai -> Filhos."""
    grouped = {}
    items_map = {item.id: item for item in items}
    
    for item in items:
        item.children_list = []

    root_items = []
    for item in items:
        if item.parent_id:
            parent = items_map.get(item.parent_id)
            if parent:
                parent.children_list.append(item)
        else:
            root_items.append(item)

    for item in root_items:
        area_name = item.area.name if item.area else "Geral"
        if area_name not in grouped:
            grouped[area_name] = []
        grouped[area_name].append(item)
        
    return grouped

def normalize_phone(country, ddd, phone):
    ''' Normaliza o número de telefone para o formato internacional E.164.'''
    # Limpa caracteres não numéricos
    ddd = re.sub(r"\D", "", (ddd))
    phone = re.sub(r"\D", "", (phone))

     # Remove o "0" à esquerda do DDD se existir
    if ddd.startswith("0"):
        ddd = ddd[1:]

    country_code = COUNTRY_CODES.get(country)
    
    if not country_code:
        # Tenta buscar com a primeira letra maiúscula caso venha tudo minusculo
        country_code = COUNTRY_CODES.get(country.capitalize())
        raise ValueError(f"País '{country}' não encontrado.")

    full_phone = f"+{country_code}{ddd}{phone}"

    return full_phone

def validate_phone(country, ddd, phone):
    ''' Valida se o formato do telefone faz sentido para o país informado. '''
    ddd = re.sub(r"\D", "", str(ddd))
    phone = re.sub(r"\D", "", str(phone))
    
    # Validação específica para o Brasil
    if country.lower() == "brazil" or country.lower() == "brasil":
        return len(ddd) == 2 and len(phone) in (8, 9)
    
    # Validação genérica para outros países (mínimo aceitável de dígitos)
    # A maioria dos países tem entre 6 e 12 dígitos no total
    total_len = len(ddd) + len(phone)
    if 7 <= total_len <= 15:
        return True
        
    return False