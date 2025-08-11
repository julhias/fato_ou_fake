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