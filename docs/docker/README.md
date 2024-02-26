## Requisitos
* Docker versão 25 ou maior, [Download](https://docs.docker.com/get-docker/);
* Docker Compose versão 2.24.5 ou maior, [Download](https://docs.docker.com/compose/install/).

## Docker Hub
* Imagens do DOO no [dockerhub](https://hub.docker.com/r/devopsorchestrator/doo/tags).

## Docker Compose
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

## Exemplos

* Instalação de serviço Web, siga o seguinte [tutorial](webserver)
