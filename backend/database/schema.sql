-- nassauTickets - Script de criação do banco de dados (MySQL 8.0)
-- Baseado em docs/mer/mer.md
--
-- Uso (dentro do cliente mysql, com o banco já criado):
--   USE nassau_tickets;
--   SOURCE schema.sql;

SET NAMES utf8mb4;

-- USUARIO: atendentes. Perfil GESTOR acessa cadastros e relatórios.
CREATE TABLE IF NOT EXISTS usuario (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    nome        VARCHAR(100) NOT NULL,
    login       VARCHAR(50)  NOT NULL,
    senha_hash  VARCHAR(255) NOT NULL,
    perfil      ENUM('ATENDENTE', 'GESTOR') NOT NULL,
    ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em   DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_usuario_login UNIQUE (login)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- GUICHE: guichês de atendimento.
CREATE TABLE IF NOT EXISTS guiche (
    id      INT AUTO_INCREMENT PRIMARY KEY,
    numero  INT     NOT NULL,
    ativo   BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_guiche_numero UNIQUE (numero)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- TIPO_SENHA: SP, SG e SE.
CREATE TABLE IF NOT EXISTS tipo_senha (
    id                INT AUTO_INCREMENT PRIMARY KEY,
    sigla             CHAR(2)     NOT NULL,
    descricao         VARCHAR(50) NOT NULL,
    ordem_prioridade  INT         NOT NULL,
    CONSTRAINT uq_tipo_senha_sigla UNIQUE (sigla)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- SENHA: senha emitida no totem. Numeração YYMMDD-PPSQ.
-- Obs.: o estado NAO_COMPARECEU é gravado sem acento no banco.
CREATE TABLE IF NOT EXISTS senha (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    numero         VARCHAR(12) NOT NULL,
    tipo_senha_id  INT         NOT NULL,
    data_emissao   DATE        NOT NULL,
    sequencia      INT         NOT NULL,
    estado         ENUM('EMITIDA', 'AGUARDANDO', 'CHAMADA', 'CHAMADA_NOVAMENTE',
                        'EM_ATENDIMENTO', 'ATENDIDA', 'NAO_COMPARECEU')
                   NOT NULL DEFAULT 'EMITIDA',
    emitida_em     DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descartada_em  DATETIME    NULL,
    CONSTRAINT uq_senha_numero UNIQUE (numero),
    CONSTRAINT uq_senha_dia_tipo_seq UNIQUE (data_emissao, tipo_senha_id, sequencia),
    CONSTRAINT fk_senha_tipo FOREIGN KEY (tipo_senha_id) REFERENCES tipo_senha (id),
    INDEX idx_senha_fila (estado, tipo_senha_id, emitida_em)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- ATENDIMENTO: chamadas e atendimento (relatório detalhado e auditoria).
CREATE TABLE IF NOT EXISTS atendimento (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    senha_id             INT      NOT NULL,
    usuario_id           INT      NOT NULL,
    guiche_id            INT      NOT NULL,
    primeira_chamada_em  DATETIME NOT NULL,
    segunda_chamada_em   DATETIME NULL,
    inicio_em            DATETIME NULL,
    fim_em               DATETIME NULL,
    CONSTRAINT uq_atendimento_senha UNIQUE (senha_id),
    CONSTRAINT fk_atendimento_senha   FOREIGN KEY (senha_id)   REFERENCES senha (id),
    CONSTRAINT fk_atendimento_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id),
    CONSTRAINT fk_atendimento_guiche  FOREIGN KEY (guiche_id)  REFERENCES guiche (id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- SENHA_HISTORICO: trilha de auditoria das mudanças de estado.
CREATE TABLE IF NOT EXISTS senha_historico (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    senha_id         INT NOT NULL,
    estado_anterior  ENUM('EMITIDA', 'AGUARDANDO', 'CHAMADA', 'CHAMADA_NOVAMENTE',
                          'EM_ATENDIMENTO', 'ATENDIDA', 'NAO_COMPARECEU') NULL,
    estado_novo      ENUM('EMITIDA', 'AGUARDANDO', 'CHAMADA', 'CHAMADA_NOVAMENTE',
                          'EM_ATENDIMENTO', 'ATENDIDA', 'NAO_COMPARECEU') NOT NULL,
    usuario_id       INT NULL,
    ocorrido_em      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_historico_senha   FOREIGN KEY (senha_id)   REFERENCES senha (id),
    CONSTRAINT fk_historico_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id),
    INDEX idx_historico_senha (senha_id, ocorrido_em)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- Dados fixos: os três tipos de senha definidos no enunciado.
-- ordem_prioridade: 1 = maior prioridade.
INSERT IGNORE INTO tipo_senha (sigla, descricao, ordem_prioridade) VALUES
    ('SP', 'Senha Prioritária',             1),
    ('SE', 'Senha para retirada de Exames', 2),
    ('SG', 'Senha Geral',                   3);