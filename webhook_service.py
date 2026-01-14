import requests
import json
import os

# URL do seu Webhook no n8n (Coloque no .env depois!)
# Lembre-se: O n8n tem URLs de "Test" e "Production". Use a de teste enquanto desenvolve.
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL_TESTE", "http://localhost:5678/webhook-test/onboarding-event")

def send_to_n8n(event_type, collaborator_name, date_obj, extra_info=""):
    """
    Envia dados para o n8n processar.
    event_type: 'ONBOARDING_START', 'ONBOARDING_END', 'OFFBOARDING'
    """
    if not date_obj:
        return
    
    # Prepara os dados (Payload)
    payload = {
        "type": event_type,
        "name": collaborator_name,
        "date": date_obj.strftime("%Y-%m-%d"),
        "details": extra_info
    }

    try:
        # Envia como JSON
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Sucesso: Evento enviado ao n8n ({event_type})")
        else:
            print(f"⚠️ Erro n8n: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Falha ao conectar com n8n: {e}")