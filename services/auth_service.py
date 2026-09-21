import os
import ssl
from dotenv import load_dotenv
from ldap3 import ALL, SIMPLE, Connection, Server, Tls
from models import User

load_dotenv()


def authenticate_ldap(username, password):
    """Autentica o usuário no servidor LDAP e retorna seus dados."""
    ldap_server = os.getenv('LDAP_SERVER')
    ldap_domain = os.getenv('LDAP_DOMAIN')
    search_base = os.getenv('LDAP_SEARCH_BASE')

    if not all([ldap_server, ldap_domain, search_base]):
        print(
            'Erro: Variáveis de ambiente do LDAP não configuradas corretamente.'
        )
        return None

    user_dn = fr'{ldap_domain}\{username}'
    tls_config = Tls(validate=ssl.CERT_NONE, version=ssl.PROTOCOL_TLSv1_2)

    try:
        server = Server(
            ldap_server,
            port=636,
            use_ssl=True,
            tls=tls_config,
            get_info=ALL,
        )

        conn = Connection(
            server, user=user_dn, password=password, authentication=SIMPLE
        )

        if conn.bind():
            conn.search(
                search_base=search_base,
                search_filter=f'(sAMAccountName={username})',
                attributes=['memberOf', 'displayName'],
            )

            if conn.entries:
                entry = conn.entries[0]
                grupos = (
                    list(entry.memberOf.values) if 'memberOf' in entry else []
                )
                nome = (
                    str(entry.displayName)
                    if 'displayName' in entry
                    else username
                )
                conn.unbind()
                return {'grupos': grupos, 'nome': nome}

            conn.unbind()
            return {}
        return None
    except Exception as e:
        print(f'Erro na conexão LDAP: {e}')
        return None


def authenticate_user(username, password):
    """Valida o usuário no banco de dados local e estende a autenticação ao LDAP se necessário."""
    user = User.query.filter_by(username=username).first()

    if not user or not user.is_active:
        return None, 'Usuário não autorizado ou inativo no sistema.'

    if user.is_ldap:
        ldap_result = authenticate_ldap(username, password)
        if ldap_result is not None:
            return user, None
        return None, 'Credenciais LDAP inválidas.'

    if user.check_password(password):
        return user, None

    return None, 'Credenciais locais inválidas.'