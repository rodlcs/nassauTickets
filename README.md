# nassauTickets

Sistema de Controle de Atendimento para um Laboratório de Análises Clínicas.

## Descrição

O **nassauTickets** controla a emissão, a fila, a chamada e o atendimento de senhas em um laboratório de análises clínicas. O cliente retira a senha de forma anônima em um totem, acompanha a chamada em um painel e é atendido em um guichê por um atendente.

O sistema trabalha com três agentes:

- **AS (Agente Sistema):** emite senhas, comunica-se com o banco de dados, atualiza o painel e responde aos comandos dos demais agentes.
- **AA (Agente Atendente):** chama o próximo cliente e realiza o atendimento no guichê.
- **AC (Agente Cliente):** emite a senha pelo totem e aguarda a chamada no painel.

E com três tipos de senha:

- **SP:** Senha Prioritária
- **SG:** Senha Geral
- **SE:** Senha para retirada de Exames

## Objetivo

Desenvolver uma aplicação Web completa, aplicando práticas de organização de projeto, versionamento com Git/GitHub, documentação, desenvolvimento com React e integração entre frontend, backend e banco de dados. Projeto da disciplina **Coding: Mobile de Alta Performance**.

## Funcionalidades previstas

- Emissão de senhas pelo totem (SP, SG e SE).
- Fila com regra de prioridade: `[SP] → [SE|SG] → [SP] → [SE|SG]`.
- Painel com as 5 últimas senhas chamadas, com áudio informando prioridade, senha e guichê.
- Chamada, início, finalização e "Chamar Novamente" (com indicação de "Última chamada").
- Máquina de estados da senha: `EMITIDA → AGUARDANDO → CHAMADA → CHAMADA_NOVAMENTE → EM_ATENDIMENTO → ATENDIDA`, com o desvio para `NÃO_COMPARECEU`.
- Numeração no padrão `YYMMDD-PPSQ`, com sequência reiniciada diariamente.
- Login do atendente, com perfil adicional de gestor.
- Relatórios diário e mensal (quantitativos, detalhamento, tempo médio e auditoria).
- Tratamento de concorrência entre atendentes e comportamento diante de falhas do backend ou do banco.

## Tecnologias utilizadas

| Camada | Tecnologia |
|---|---|
| Frontend | React 19 + Vite |
| Backend | Python + Flask *(em desenvolvimento)* |
| Banco de dados | MySQL 8.0 *(em desenvolvimento)* |
| Versionamento | Git e GitHub |

### Justificativa da escolha do backend

O backend será desenvolvido em **Python com Flask**. A escolha se deve a:

- **Simplicidade:** o Flask é um microframework enxuto, adequado a uma API REST com poucas rotas e regras de negócio bem definidas, sem a estrutura pesada de um framework maior.
- **Legibilidade:** o código Python é claro, o que facilita a implementação das regras de prioridade, da máquina de estados e dos relatórios.
- **Integração com MySQL:** há drivers e bibliotecas maduras para acesso ao MySQL 8.0 e para controle de transações, importante no tratamento de concorrência.
- **Familiaridade:** a equipe tem mais afinidade com Python, o que reduz o tempo de desenvolvimento.

## Arquitetura

```
┌───────────────┐   HTTP / JSON   ┌───────────────┐    SQL    ┌───────────────┐
│   Frontend    │ ──────────────► │    Backend    │ ────────► │     MySQL     │
│ React + Vite  │ ◄────────────── │ Flask (API)   │ ◄──────── │      8.0      │
└───────────────┘                 └───────────────┘           └───────────────┘
 Totem · Painel · Guichê           Regras de negócio
                                   Fila · Estados · Relatórios
```

O frontend (React) consome a API REST do backend (Flask), que aplica as regras de negócio e persiste os dados no MySQL.

## Estrutura do repositório

```
nassauTickets/
├── backend/          # API em Flask
├── docs/
│   ├── branding/     # Identidade visual
│   ├── mer/          # Modelo Entidade-Relacionamento
│   ├── mockups/      # Protótipos das telas
│   ├── models/
│   │   └── uml/      # Diagramas UML
│   └── requirements/ # Requisitos e regras de negócio
├── frontend/         # Aplicação React
├── .gitignore
├── LICENSE
└── README.md
```

## Pré-requisitos

- Node.js (versão 22 ou superior)
- npm
- Python 3.12 ou superior
- MySQL 8.0
- Git

## Instalação

```bash
git clone https://github.com/rodlcs/nassauTickets.git
cd nassauTickets
git checkout dev
```

### Frontend

```bash
cd frontend
npm install
```

### Backend *(em desenvolvimento)*

As instruções de instalação do backend (ambiente virtual, dependências e criação do banco) serão adicionadas assim que ele for implementado.

## Execução

### Frontend

```bash
cd frontend
npm run dev
```

A aplicação ficará disponível em `http://localhost:5173/`. Mantenha o terminal aberto enquanto estiver usando.

### Backend *(em desenvolvimento)*

Instruções de execução serão adicionadas junto com a implementação da API.

## Configuração

As configurações sensíveis (usuário e senha do banco, chave secreta) ficarão em um arquivo `.env` dentro de `backend/`, que **não é versionado**. Um arquivo `.env.example` com as variáveis necessárias será disponibilizado quando o backend estiver pronto.

## Membros

| Nome | Matrícula | Papel |
|---|---|---|
| Rodrigo Lucas Ferreira | 01811731 | Scrum Master, Documentador, Desenvolvedor e Testador |

## Branches

| Branch | Finalidade |
|---|---|
| `main` | Versão estável, atualizada apenas por merge vindo da `dev`. |
| `dev` | Branch de desenvolvimento. Todo o código é enviado primeiro para ela. |

Fluxo de trabalho:

1. O desenvolvimento é feito na `dev`, com commits pequenos e objetivos.
2. Ao concluir uma etapa, a `dev` é integrada à `main` por merge.

Os commits seguem o padrão `tipo: descrição`, por exemplo `feat:`, `fix:`, `docs:` e `chore:`.

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
