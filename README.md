# Desafio de Engenharia de Dados | ETL de Proposições Legislativas

Olá, candidato! Bem-vindo ao nosso desafio de engenharia de dados, que visa avaliar sua habilidade em manipular e processar dados de uma API e gerenciar um banco de dados de forma eficaz.

## 🚀 Objetivo:

Desenvolver um pipeline de dados em Python para extrair informações sobre proposições legislativas do estado de Minas Gerais para o ano de 2023, realizar a limpeza necessária dos dados e carregá-los em um esquema de banco de dados relacional.

## 💻 Tecnologias:

- Python
- Qualquer banco de dados relacional (PostgreSQL, MySQL, etc.)
- Docker

## 📜 Requisitos do Projeto:

### 1. Extração de Dados:

- Acesse os dados por meio do endpoint da API: `https://dadosabertos.almg.gov.br/ws/proposicoes/pesquisa/direcionada?tp=1000&formato=json&ano=2023&ord=3`.
- Consulte a [documentação](http://dadosabertos.almg.gov.br/ws/proposicoes/ajuda#Pesquisa%20Direcionada%20%C3%A0s%20Proposi%C3%A7%C3%B5es%20em%20Tramita%C3%A7%C3%A3o) da API para compreender os parâmetros e a estrutura dos dados disponíveis.

### 2. Limpeza de Dados:

- Remova espaçamentos desnecessários, caracteres especiais como "\n", e ajuste os formatos de data e texto conforme necessário.

### 3. Carregamento de Dados:

- Carregue os dados limpos em um banco de dados relacional seguindo o esquema abaixo.

### 4. Dockerização:

- Dockerize a aplicação e o banco de dados para garantir a portabilidade e fácil configuração do ambiente de desenvolvimento e produção.

## Esquema de Banco de Dados:

### Tabela: Proposição
| Campo            | Tipo      | Descrição                                                                                         |
|------------------|-----------|---------------------------------------------------------------------------------------------------|
| id               | Incremental| ID automático                                                                                    |
| author           | String    | Autor da proposição, ex. "Governador Romeu Zema Neto"                                             |
| presentationDate | Timestamp | Data de apresentação da proposição, ex. "2022-10-06T00:00:00Z"                                    |
| ementa           | String    | Assunto da proposição, ex. "Encaminha o Projeto de Lei 4008 2022..."                              |
| regime           | String    | Regime de tramitação da proposição, ex. "Especial"                                                |
| situation        | String    | Situação atual da proposição, ex. "Publicado"                                                     |
| propositionType  | String    | Tipo da proposição, ex. "MSG"                                                                     |
| number           | String    | Número da proposição, ex. "300"                                                                   |
| year             | Integer   | Ano da proposição, ex. 2022                                                                       |
| city             | String    | Cidade fixa "Belo Horizonte"                                                                      |
| state            | String    | Estado fixo "Minas Gerais"                                                                        |

### Tabela: Tramitação
| Campo            | Tipo         | Descrição                                                                                         |
|------------------|--------------|---------------------------------------------------------------------------------------------------|
| id               | Incremental  | ID automático                                                                                     |
| createdAt        | Timestamp    | Data do registro da tramitação, ex. "2022-10-04T00:00:00Z"                                        |
| description      | String       | Descrição do histórico da tramitação, ex. "Proposição lida em Plenário.\nPublicada no DL..."      |
| local            | String       | Local da tramitação, ex. "Plenário"                                                               |
| propositionId    | ForeignKey   | Chave estrangeira que referencia o ID da proposição                                               |

## 🥇 Diferenciais:

- Uso de Docker Compose para orquestração de múltiplos containers.
- Documentação clara do processo de configuração e execução do pipeline.
- Implementação de testes para validar a integridade dos dados.
- Evitar a inserção de dados duplicados no banco.
- Script de ingestão diária dos dados (atualizados).

## 🗳️ Instruções de Submissão:

1. Faça um fork deste repositório para sua conta pessoal do GitHub.
2. Commit e push suas mudanças para o seu fork.
3. Envie um e-mail para [brenno.natal@khipo.com.br] com o link do repositório.

## 🧪 Avaliação:

- Estrutura do código e organização.
- Uso adequado das ferramentas e tecnologias.
- Implementação dos requisitos do projeto.
- Otimização de performance.

Boa sorte com o desafio! Estamos ansiosos para ver sua solução.
