# backend/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# O caminho para o arquivo .env continua o mesmo, ele será lido no servidor
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding='utf-8')

    # Configurações do banco de dados (lidas do .env)
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    SECRET_KEY: str

    # --- CONFIGURAÇÕES DE PRODUÇÃO ---

    # Caminho absoluto para a pasta no servidor onde os arquivos serão salvos.
    # Tem substituir pelo caminho real no seu servidor.
    UPLOAD_FOLDER: str = "/var/www/fato-ou-fake/uploads"
    
    # URL base pública que apontará para os arquivos salvos.
    # Substituir pelo domínio real da sua aplicação.
    SERVER_BASE_URL: str = "https://servidor.ufscar.br"

settings = Settings()

# Garante que a pasta de uploads exista no servidor quando a aplicação iniciar
os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)