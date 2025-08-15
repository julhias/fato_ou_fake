# backend/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class RegisterSchema(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    role: str = 'pesquisador' # Valor padrão é 'pesquisador

class RegisterRequestSchema(BaseModel):
    nome: str
    email: EmailStr