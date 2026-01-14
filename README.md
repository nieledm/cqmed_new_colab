# Onboarding Formulário

Estrutura mínima para o app Flask de gerenciamento de checklist de onboarding.

Como rodar (Windows):

1. Criar e ativar virtualenv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Rodar a aplicação

```powershell
python run.py
```

O template principal está em `templates/request.html` e a fábrica de app é `create_app()` em `app.py`.
