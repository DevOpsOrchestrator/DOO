## Requisitos

1) Python 3.11 ([Instalação](https://docs.python.org/3/using/index.html));
2) Pip 23 ou maior ([Instalação](https://pip.pypa.io/en/stable/installation/));
3) Postgresql 15 ou maior ([Download](https://www.postgresql.org/download/));
4) Git 2.34 ou maior ([Download](https://git-scm.com/downloads))
5) Gitlab 16 ou maior ([Instalação](https://about.gitlab.com/install/)).

## Instalação
Faça o clone do DOO, com o seguinte comando:

```shel
git clone https://github.com/DevOpsOrchestrator/DOO.git
```
entre na pasta DOO,

O DOO foi desenvolvido em Python, utilizando o framework Django. Para instalar o Django e as dependências necessárias, basta executar o seguinte comando:

```bash

pip install -r requirements.txt

```
Adicione a variavel de ambiente de nome VAULT_PASS com a senha que será utilizada para encriptar e descripitar o inventario e as variaveis do codigo ansible gerado. 
Execute o seguinte comando:

```bash

echo "export VAULT_PASS=password" >> ~/.bashrc && source ~/.bashrc

```
Adicione a variável de ambiente de nome REPOSITORY com o caminho do repositório local onde será gerado o código Ansible. Execute o seguinte comando:

```bash

echo "export REPOSITORY=caminho" >> ~/.bashrc && source ~/.bashrc

```

Adicione as variaveis de ambiente com as credenciais do banco de dados postgres, as variaveis são DB_NAME,DB_USER,DB_PASSWORD,DB_HOST,DB_PORT. Execute o seguinte comando:

```bash

echo 'export DB_NAME=doo DB_USER=doo DB_PASSWORD=doo123 DB_HOST=localhost DB_PORT=5432' >> ~/.bashrc && source ~/.bashrc
```

Crie o banco e o usuario no Postgresql. Execute os seguintes comandos:

Para entrar no console do Postgres:

```bash

sudo -u postgres psql

```
Criando o banco:
```bash
CREATE DATABASE doo;
```
Criando o usuario:
```bash
CREATE USER doo WITH PASSWORD 'doo123';
```
Mudando o dono do banco:
```bash
ALTER DATABASE doo OWNER TO doo;
```

Para criar o banco e suas tabelas execute o seguinte comando:

```bash

python manage.py makemigrations && python manage.py migrate

```
Copie os arquivos estaticos executando o seguinte comando:

```bash

python manage.py collectstatic

```
Crie o usuario root executando o seguinte comando:

```bash

python manage.py createsuperuser

```
Inicie o servidor executando o seguinte comando:

```bash

python manage.py runserver

```

Pronto, basta acessa o DOO na url [http://localhost:8000](http://localhost:8000) e se logar utilizando o usuario e senha criados nos passos anteriores.


## Docker

### Requisitos
* Docker versão 25 ou maior, [Download](https://docs.docker.com/get-docker/);
* Docker Compose versão 2.24.5 ou maior, [Download](https://docs.docker.com/compose/install/).

### Docker Hub
* Imagens do DOO no [dockerhub](https://hub.docker.com/r/devopsorchestrator/doo/tags).

### Docker Compose
Para facilitar o entendimento vamos utilizar um arquivo `.env` com as seguintes variaveis:
```Dotenv
POSTGRESQL_VERSION=15
POSTGRESQL_NAME=doo_postgres
POSTGRESQL_HOST=postgres
POSTGRESQL_PORT_EXTERNAL=5432
POSTGRES_DB=doo
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

DOO_NAME=doo
DEBUG=true
DJANGO_DEBUG=false
DB_WAIT_DEBUG=false

SECRET_KEY='r8OwDznj!!dci#P9ghmRfdu1Ysxm0AiPeDCQhKE+N_rClfWNj'
SKIP_SUPERUSER=false
SUPERUSER_API_TOKEN=0123456789abcdef0123456789abcdef01234567
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_NAME=admin
SUPERUSER_PASSWORD=admin
```

Um arquivo `docker-compose.yml` minimo para DOO funcionar, segue o seguinte padrão:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:${POSTGRESQL_VERSION}
    container_name: ${POSTGRESQL_NAME}
    hostname: ${POSTGRESQL_HOST}
    ports:
      - ${POSTGRESQL_PORT_EXTERNAL}:5432
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      TZ: "America/Fortaleza"
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -d $${POSTGRES_DB} -U $${POSTGRES_USER}"]
      interval: 10s
      timeout: 30s
      retries: 10

  doo:
    ports:
      - 8000:8000
      - 3000:3000
    image: devopsorchestrator/doo:latest
    container_name: ${DOO_NAME}
    hostname: ${DOO_NAME}
    environment:
      DEBUG: ${DEBUG}
      DJANGO_DEBUG: ${DJANGO_DEBUG}
      DB_NAME: ${POSTGRES_DB}
      DB_PASSWORD: ${POSTGRES_PASSWORD}
      DB_USER: ${POSTGRES_USER}
      DB_HOST: ${POSTGRESQL_NAME}
      DB_WAIT_DEBUG: ${DB_WAIT_DEBUG}
      SECRET_KEY: ${SECRET_KEY}
      SKIP_SUPERUSER: ${SKIP_SUPERUSER}
      SUPERUSER_API_TOKEN: ${SUPERUSER_API_TOKEN}
      SUPERUSER_EMAIL: ${SUPERUSER_EMAIL}
      SUPERUSER_NAME: ${SUPERUSER_NAME}
      SUPERUSER_PASSWORD: ${SUPERUSER_PASSWORD}
    depends_on:
    - postgres
    
```

Para subir a aplicação e o banco de dados Postgres basta executar o seguinte comando na raiz do projeto:

```bash
docker compose up
```
Algumas variaveis podem ser editadas no arquivo .env na raiz do projeto, segue uma explicação sobre as mesmas:

```Dotenv
REPOSITORY='/home/app/repository' #Pasta onde o código gerado será salvo localmente

DOO_NAME=doo                      #Nome do container
DB_WAIT_DEBUG=0                   #Ao ativar essa flag será mostrado mas detalhes de erro de DB

SECRET_KEY='r8OwDznj!!dci#P9ghmR' #SECRET_KEY do Django, sempre altere para produção
SKIP_SUPERUSER=false              #Ao ativar essa flag não será criado o usuario admim
SUPERUSER_API_TOKEN=0123456789ab  #Token do usuário admin
SUPERUSER_EMAIL=admin@example.com #Email do usuário admin
SUPERUSER_NAME=admin              #Login do usuário admin
SUPERUSER_PASSWORD=admin          #Senha do usuário admin

POSTGRESQL_VERSION=15             #Versão do Postgres
POSTGRESQL_NAME=postgres          #Nome do container do Postgres
POSTGRESQL_HOST=localhost         #Nome do host do Postgres
POSTGRESQL_PORT_EXTERNAL=5432     #Porta do Postgres
POSTGRES_DB=doo                   #Nome do banco no Postgres
POSTGRES_USER=postgres            #Usuário do Postgres
POSTGRES_PASSWORD=postgres        #Senha do Postgres

```