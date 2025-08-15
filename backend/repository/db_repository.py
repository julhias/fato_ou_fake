# backend/repository/db_repository.py
import mysql.connector
from backend.core.config import settings


def get_db_connection():
    try:
        return mysql.connector.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME
        )
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o BD: {err}")
        raise

def validar_login_repo(email, senha):
    conn = get_db_connection()
    cursor = conn.cursor(buffered=True)
    try:
        # A forma correta de chamar uma função e obter seu retorno
        cursor.execute(f"SELECT fn_ValidarLogin('{email}', '{senha}')")
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        cursor.close()
        conn.close()

def processar_lote_repo(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('sp_ProcessarLoteResultados', args)
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()

def armazenar_midia_repo(args):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('sp_ArmazenarLoteMidia', args)
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()
def pesquisa_avancada_repo(args):
    """
    Calls the sp_PesquisaAvancada stored procedure and fetches all results.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True) # dictionary=True returns rows as dicts
    try:
        cursor.callproc('sp_PesquisaAvancada', args)
        
        # Stored procedures can return multiple result sets; we fetch the first one.
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())
            
        return results
    finally:
        cursor.close()
        conn.close()


def pesquisar_midia_repo(args):
    """
    Calls the sp_PesquisarMidiaArmazenada stored procedure and fetches all results.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.callproc('sp_PesquisarMidiaArmazenada', args)
        
        results = []
        for result in cursor.stored_results():
            results.extend(result.fetchall())

        return results
    finally:
        cursor.close()
        conn.close()

def registrar_usuario_repo(args):
    """
    Chama a stored procedure sp_AdminRegistrarUsuario para criar um novo utilizador.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc('sp_AdminRegistrarUsuario', args)
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        # Lança o erro para que a camada superior o possa capturar
        raise err
    finally:
        cursor.close()
        conn.close()

def get_admin_emails_repo():
    """Busca os emails de todos os utilizadores com o perfil 'admin'."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT Email FROM Usuario WHERE Role = 'admin'")
        # fetchall() retorna uma lista de tuplas, ex: [('admin1@email.com',), ('admin2@email.com',)]
        # Usamos uma list comprehension para extrair apenas os emails.
        results = [item[0] for item in cursor.fetchall()]
        return results
    finally:
        cursor.close()
        conn.close()


def get_all_users_repo():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT UsuarioID, Nome, Email, Role, DataCadastro FROM Usuario ORDER BY UsuarioID")
        results = cursor.fetchall()
        return results
    finally:
        cursor.close(); conn.close()

def get_user_by_id_repo(user_id):
    """Busca os detalhes de um usuário, incluindo sua role, pelo ID."""
    conn = get_db_connection()
    # Usamos dictionary=True para obter o resultado como um dicionário
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT UsuarioID, Nome, Email, Role FROM Usuario WHERE UsuarioID = %s"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        return user_data
    finally:
        cursor.close()
        conn.close()

