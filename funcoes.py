import re
from country_codes import COUNTRY_CODES



def calculate_global_status(items):
    statuses = [i.status for i in items]

    if all(s == "pending" for s in statuses):
        return "aguardando"
    if all(s == "done" for s in statuses):
        return "concluido"
    return "em_andamento"

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