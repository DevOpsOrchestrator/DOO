# DevOpsOrchestrator
Este é o repositório de código do **DevOpsOrchestrator (DOO)**, plataforma integrada que utiliza a infraestrutura como código para automatizar o gerenciamento de serviços.

Essa plataforma permite que os administradores de rede utilizem uma interface gráfica para acessar servidores e realizar configurações que antes eram feitas manualmente.
O DOO é fruto de uma pesquisa de Thiago de Abreu Lima sob orientação do professor Dr. Ramon dos Reis Fontes, iniciada em 2022 no Programa de Pós-Graduação em Tecnologia da Informação - PPGTI da Universidade Federal do Rio Grande do Norte - UFRN.

## Instalação

Instale o DOO seguindo esse [tutorial](docs/README.md).


## Docker

Para subir a aplicação e o banco de dados Postgres basta executar o seguinte comando na raiz do projeto:

```bash
docker compose up
```
Algumas variaveis podem ser editadas no arquivo .env na raiz do projeto, segue uma explicação sobre as mesmas:

```bash
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


