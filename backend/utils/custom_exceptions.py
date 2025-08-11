# backend/utils/custom_exceptions.py
class ServiceError(Exception):
    """Exceção base para erros na camada de serviço."""
    def __init__(self, message="Ocorreu um erro no serviço", status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(ServiceError):
    """Lançado quando um recurso não é encontrado."""
    def __init__(self, resource_name="Recurso"):
        super().__init__(f"{resource_name} não encontrado", 404)

class ValidationError(ServiceError):
    """Lançado para erros de validação de dados."""
    def __init__(self, details):
        super().__init__("Dados de entrada inválidos", 400)
        self.details = details

class UnauthorizedError(ServiceError):
    """Lançado para falhas de autenticação ou autorização."""
    def __init__(self, message="Não autorizado"):
        super().__init__(message, 401)