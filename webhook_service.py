import requests
import json
import os

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL_PRODUCTION", "http://localhost:5678/webhook-test/onboarding-event")

def send_to_n8n(collaborator_name, 
                      start_event_type, 
                      start_date_obj, 
                      start_extra_info,
                      end_event_type, 
                      end_date_obj, 
                      end_extra_info,):
    """
    Envia dados para o n8n processar.
    """
    if not start_date_obj:
        return
    
    # Prepara os dados (Payload)
    payload = {
        "name": collaborator_name,
        "start_type": start_event_type,
        "start_date": start_date_obj.strftime("%Y-%m-%d"),
        "start_details": start_extra_info,
        "end_type": end_event_type,
        "end_date": end_date_obj.strftime("%Y-%m-%d"),
        "end_details": end_extra_info
    }

    try:
        # Envia como JSON
        response = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Sucesso: Evento enviado ao n8n - Início para {collaborator_name} em {start_date_obj.strftime('%Y-%m-%d')}")
        else:
            print(f"⚠️ Erro n8n: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Falha ao conectar com n8n: {e}")