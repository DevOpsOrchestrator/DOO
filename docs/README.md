# Tutorial de Instalação do XXX

## Requisitos

1) Python 3.11 ou maior ([Instalação](https://docs.python.org/3/using/index.html));
2) Pip 23 ou maior ([Instalação](https://pip.pypa.io/en/stable/installation/));
3) Postgresql 15 ou maior ([Download](https://www.postgresql.org/download/));
4) Gitlab 16 ou maior ([Instalação](https://about.gitlab.com/install/)).

## Instalação
O XXX foi desenvolvido em Python, utilizando o framework Django. Para instalar o Django e as dependências necessárias, basta executar o seguinte comando:

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

echo 'export DB_NAME=xxx DB_USER=postgres DB_PASSWORD=postgres DB_HOST=localhost DB_PORT=5432' >> ~/.bashrc && source ~/.bashrc
```

Crie o banco e o usuario no Postgresql. Execute os seguintes comandos:

Para entrar no console do Postgres:

```bash

sudo -u postgres psql

```
Criando o banco:
```bash
CREATE DATABASE xxx;
```
Criando o usuario:
```bash
CREATE USER xxx WITH PASSWORD '123456789';
```
Mudando o dono do banco:
```bash
ALTER DATABASE xxx OWNER TO xxx;
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

Pronto, basta acessa o xxx na url [http://localhost:8000](http://localhost:8000) e se logar utilizando o usuario e senha criados nos passos anteriores.


