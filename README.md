# Projeto Fato ou Fake: Plataforma de Análise e Armazenamento de Mídia

Este projeto é uma aplicação web completa projetada para centralizar, armazenar e consultar resultados de análises de detecção de fake news, bem como para guardar os lotes de mídias (imagens, vídeos, textos) utilizados nessas análises.

---

## ✨ Funcionalidades Principais

- **Autenticação de Usuários**: Sistema de login seguro utilizando tokens JWT.
- **Upload de Resultados**: Permite que usuários autenticados enviem lotes de resultados de análises em formato `.json` ou `.csv`, seja por upload de arquivo local ou via link do Google Drive.
- **Armazenamento de Mídia**: Funcionalidade para fazer upload de arquivos de mídia (imagens, vídeos, etc.) diretamente para o servidor da aplicação.
- **Consulta de Dados**: Uma interface de pesquisa para buscar e visualizar os dados e mídias armazenadas no sistema.
- **API RESTful**: Backend robusto construído com Flask, seguindo as melhores práticas de desenvolvimento de APIs.

---

## 🛠️ Tecnologias Utilizadas

- **Backend**:
  - **Linguagem**: Python 3
  - **Framework**: Flask
  - **Banco de Dados**: MySQL (ou outro SQL de sua preferência)
  - **Autenticação**: JSON Web Tokens (JWT)
  - **Servidor de Produção**: Gunicorn & Nginx

- **Frontend**:
  - HTML5
  - CSS3
  - JavaScript (Vanilla)

---

## 🚀 Como Executar (Ambiente de Desenvolvimento)

Siga os passos abaixo para configurar e rodar o projeto em sua máquina local.

### Pré-requisitos

- **Python 3.8+** e `pip`
- **Git**
- **Servidor de Banco de Dados** (ex: MySQL, MariaDB)

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd <nome-do-repositorio>
    ```

2.  **Crie e ative um ambiente virtual (Virtual Environment):**
    ```bash
    # Para Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Para macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instale as dependências do Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure o Banco de Dados:**
    - Crie um banco de dados no seu servidor SQL (ex: `fakenews_db`).
    - O esquema completo para a criação das tabelas está no arquivo `schema.sql`, localizado na raiz do projeto. Execute este script no seu banco de dados.

5.  **Configure as Variáveis de Ambiente:**
    - Na pasta `backend/`, crie um arquivo chamado `.env`.
    - Copie o conteúdo do arquivo `.env.example` (se houver) ou use o modelo abaixo e preencha com suas credenciais locais.

    ```ini
    # backend/.env
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=sua_senha_local
    DB_NAME=fakenews_db
    SECRET_KEY=uma_chave_secreta_para_desenvolvimento

    # Use as credenciais do Mailtrap para teste de e-mails
    MAIL_SERVER=sandbox.smtp.mailtrap.io
    MAIL_PORT=2525
    MAIL_USERNAME=seu_usuario_mailtrap
    MAIL_PASSWORD=sua_senha_mailtrap
    ```

6.  **Execute a aplicação:**
    ```bash
    # A partir da raiz do projeto
    flask --app backend run
    ```
    A API estará disponível em `http://12.0.0.1:5000`. Abra os arquivos `.html` no seu navegador para interagir com a aplicação.

---

## 📦 Deploy (Ambiente de Produção - Servidor)

Para implantar a aplicação em um servidor (como o da UFSCar), siga estes passos:

1.  **Clone a branch de produção:**
    ```bash
    git clone -b versao-servidor <url-do-seu-repositorio>
    ```

2.  **Configure o `.env` de Produção**: Crie o arquivo `backend/.env` no servidor com as credenciais do banco de dados de produção e um `SECRET_KEY` forte. **Não use credenciais de desenvolvimento!**

3.  **Configure o Servidor Web (Nginx)**: Configure o Nginx como um proxy reverso para receber o tráfego público e servir os arquivos estáticos da pasta `/uploads`.

4.  **Execute com Gunicorn**: Use o Gunicorn para iniciar a aplicação Flask de forma robusta. O Gunicorn usará o arquivo `wsgi.py` como ponto de entrada.
    ```bash
    # Exemplo de comando para iniciar o Gunicorn
    gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app
    ```
