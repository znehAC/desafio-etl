# Desafio de Engenharia de Dados | ETL de Proposições Legislativas

# Pipeline de Ingestão Diária de Dados

## Visão Geral

Este projeto automatiza a extração diária, transformação e carga (ETL) de dados para um banco de dados PostgreSQL usando Python. Utiliza o Docker Compose para a orquestração de containers e garante a integridade dos dados através do SQLAlchemy e validação de esquema com marshmallow.

## Funcionalidades

- **Docker Compose**: Orquestra múltiplos containers incluindo o banco de dados PostgreSQL e serviços da aplicação.
- **Processo ETL Automatizado**: Extração diária de dados de uma API, transformação usando Pandas e validação de esquema com marshmallow, e carregamento no banco de dados.
- **Integridade dos Dados**: Evita a inserção de dados duplicados no banco de dados.
- **Agendamento**: Executa o processo ETL diariamente à meia-noite usando a biblioteca `schedule`.
- **Tratamento de Erros**: Registra erros e tenta novamente operações falhas com um backoff exponencial.

## Extrutura do projeto
  ```
  projeto/
  │
  ├── src/
  │   ├── alembic/        (Configurações do alembic (migration))
  │   ├── alembic.ini
  │   │
  │   ├── daily.py        (Script para execução diária do pipeline)
  │   ├── etl.py          (Script com o código do pipeline)
  │   ├── models.py       (Modelos para ORM com SQLAlchemy)
  │
  ├── .env                (Configurações)
  ├── docker-compose.yml  
  ├── Dockerfile
  ├── requirements.txt    (Modulos requeridos do Python)
```
## Configuração

### Pré-requisitos

- Docker
- Docker Compose 
- Criar volume externo do database
```bash
docker volume create pg_base
```

### Exemplo de Configuração do Arquivo .env

Crie um arquivo `.env` no diretório raiz do projeto e configure as variáveis de ambiente necessárias conforme o exemplo abaixo:

```plaintext
DB_NAME=database_name
DB_HOST=db
DB_PORT=5432
DB_USER=user
DB_PASS=password

ETL_MAX_WORKERS=5
ETL_ENGINE_POOL_SIZE=10
ETL_RETRIES=3
ETL_BACKOFF_FACTOR=0.3
```

- `DB_NAME`: Nome do banco de dados PostgreSQL a ser utilizado.
- `DB_HOST`: Endereço do host onde o banco de dados PostgreSQL está hospedado.
- `DB_PORT`: Porta utilizada para se conectar ao banco de dados PostgreSQL.
- `DB_USER`: Nome de usuário do banco de dados PostgreSQL.
- `DB_PASS`: Senha do usuário do banco de dados PostgreSQL.
- `ETL_MAX_WORKERS`: Número máximo de workers para processamento paralelo durante a extração de dados.
- `ETL_ENGINE_POOL_SIZE`: Tamanho máximo do pool de conexões do SQLAlchemy para o banco de dados.
- `ETL_RETRIES`: Número de tentativas de recuperação em caso de falha durante a extração de dados.
- `ETL_BACKOFF_FACTOR`: Fator de backoff exponencial para intervalo de espera entre tentativas de recuperação.

### Configuração de automação

No arquivo daily.py é possível adicionar datas (schedules) para a atualização

```
schedule.every().day.at("00:00").do(daily_job)
```

### Comandos Úteis
- Para iniciar o projeto com Docker Compose:
```bash
docker compose up -d
```
- Executar a pipeline ETL manualmente
```bash
docker exec -it app python etl.py
```

#### Informações de contato
- **Email:** adrianocesar321@gmail.com
