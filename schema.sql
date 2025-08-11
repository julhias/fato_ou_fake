-- =====================================================================
-- SCHEMA (TABELAS)
-- =====================================================================

-- Tabela para gerenciar usuários e suas permissões
CREATE TABLE Usuario (
    UsuarioID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    SenhaHash VARCHAR(255) NOT NULL, -- NUNCA armazene senhas em texto plano
    Role ENUM('admin', 'pesquisador') NOT NULL DEFAULT 'pesquisador',
    DataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabela para armazenar os tipos de conteúdo possíveis
-- CORREÇÃO: Adicionada a criação da tabela que estava faltando.
CREATE TABLE TiposDeConteudo (
    TipoID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(50) NOT NULL UNIQUE -- Ex: 'Texto', 'Imagem', 'Audio', 'Video'
);

-- Tabela principal de conteúdo, com URL para mídia para melhor performance
CREATE TABLE Conteudo (
    ConteudoID INT PRIMARY KEY AUTO_INCREMENT,
    Texto TEXT,
    MidiaURL VARCHAR(1024),
    DataPublicacao DATETIME,
    Fonte VARCHAR(255),
    CategoriaInicial ENUM('Verdadeiro', 'Falso', 'Indeterminado'),
    Metadados JSON,
    UsuarioUploaderID INT,
    FOREIGN KEY (UsuarioUploaderID) REFERENCES Usuario(UsuarioID) ON DELETE SET NULL
);

-- Tabela de ligação (Muitos-para-Muitos) entre Conteudo e TiposDeConteudo
CREATE TABLE Conteudo_Tipos (
    ConteudoID INT NOT NULL,
    TipoID INT NOT NULL,
    PRIMARY KEY (ConteudoID, TipoID),
    FOREIGN KEY (ConteudoID) REFERENCES Conteudo(ConteudoID) ON DELETE CASCADE,
    FOREIGN KEY (TipoID) REFERENCES TiposDeConteudo(TipoID) ON DELETE CASCADE
);

-- Tabela de algoritmos de detecção
CREATE TABLE Algoritmo (
    AlgoritmoID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(255) NOT NULL,
    Versao VARCHAR(50) NOT NULL,
    Parametros JSON,
    Descricao TEXT,
    DataTreinamento DATE,
    UNIQUE (Nome, Versao)
);

-- Tabela central que conecta um conteúdo a uma análise de um algoritmo
CREATE TABLE ProcessoDeDeteccao (
    ProcessoID INT PRIMARY KEY AUTO_INCREMENT,
    ConteudoID INT NOT NULL,
    AlgoritmoID INT NOT NULL,
    UsuarioExecutorID INT,
    DataExecucao DATETIME NOT NULL,
    TempoExecucao FLOAT,
    Score FLOAT,
    Confianca FLOAT,
    FOREIGN KEY (ConteudoID) REFERENCES Conteudo(ConteudoID) ON DELETE CASCADE,
    FOREIGN KEY (AlgoritmoID) REFERENCES Algoritmo(AlgoritmoID),
    FOREIGN KEY (UsuarioExecutorID) REFERENCES Usuario(UsuarioID) ON DELETE SET NULL
);

-- Tabela com o resultado (rótulo) de um processo de detecção
CREATE TABLE Rotulo (
    RotuloID INT PRIMARY KEY AUTO_INCREMENT,
    ProcessoID INT NOT NULL UNIQUE, -- Relação 1:1 com Processo
    CategoriaDetectada VARCHAR(50) NOT NULL,
    Confianca FLOAT,
    Justificativa TEXT,
    FOREIGN KEY (ProcessoID) REFERENCES ProcessoDeDeteccao(ProcessoID) ON DELETE CASCADE
);

-- Tabela de log/auditoria para rastrear todas as ações
CREATE TABLE HistoricoProcessamento (
    HistoricoID INT PRIMARY KEY AUTO_INCREMENT,
    ProcessoID INT NOT NULL,
    DataRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(50),
    Observacoes TEXT,
    FOREIGN KEY (ProcessoID) REFERENCES ProcessoDeDeteccao(ProcessoID) ON DELETE CASCADE
);


-- =====================================================================
-- FUNÇÕES (FUNCTIONS)
-- =====================================================================

DELIMITER $$

CREATE FUNCTION fn_ObterOuCriarAlgoritmoID(
    p_Nome VARCHAR(255),
    p_Versao VARCHAR(50),
    p_Parametros JSON,
    p_DataTreinamento DATE
)
RETURNS INT
DETERMINISTIC
MODIFIES SQL DATA
BEGIN
    DECLARE v_ID INT;
    SELECT AlgoritmoID INTO v_ID FROM Algoritmo WHERE Nome = p_Nome AND Versao = p_Versao;
    IF v_ID IS NULL THEN
        INSERT INTO Algoritmo (Nome, Versao, Parametros, DataTreinamento)
        VALUES (p_Nome, p_Versao, p_Parametros, p_DataTreinamento);
        SET v_ID = LAST_INSERT_ID();
    END IF;
    RETURN v_ID;
END$$

DELIMITER ;

DELIMITER $$

CREATE FUNCTION fn_ValidarLogin(
    p_Email VARCHAR(255),
    p_SenhaEmTextoPlano VARCHAR(255)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE v_UsuarioID INT DEFAULT 0;
    DECLARE v_SenhaHashArmazenada VARCHAR(256);

    SELECT UsuarioID, SenhaHash INTO v_UsuarioID, v_SenhaHashArmazenada
    FROM Usuario WHERE Email = p_Email;

    IF v_UsuarioID > 0 AND v_SenhaHashArmazenada = SHA2(p_SenhaEmTextoPlano, 256) THEN
        RETURN v_UsuarioID;
    ELSE
        RETURN 0;
    END IF;
END$$

DELIMITER ;

-- =====================================================================
-- PROCEDURES (STORED PROCEDURES)
-- =====================================================================

DELIMITER $$

CREATE PROCEDURE sp_ProcessarLoteResultados(
    IN p_UsuarioID INT,
    IN p_NomeAlgoritmo VARCHAR(255),
    IN p_VersaoAlgoritmo VARCHAR(50),
    IN p_ParametrosAlgoritmo JSON,
    IN p_DataTreinamento DATE,
    IN p_DataExecucao DATETIME,
    IN p_TiposConteudoJSON JSON,
    IN p_LoteDados JSON
)
BEGIN
    DECLARE v_AlgoritmoID INT;
    DECLARE v_ConteudoID INT;
    DECLARE v_ProcessoID INT;
    DECLARE v_ItemJSON JSON;
    DECLARE v_RowCount INT;
    DECLARE i INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    SET v_AlgoritmoID = fn_ObterOuCriarAlgoritmoID(p_NomeAlgoritmo, p_VersaoAlgoritmo, p_ParametrosAlgoritmo, p_DataTreinamento);
    SET v_RowCount = JSON_LENGTH(p_LoteDados);
    WHILE i < v_RowCount DO
        SET v_ItemJSON = JSON_EXTRACT(p_LoteDados, CONCAT('$[', i, ']'));

        INSERT INTO Conteudo (Texto, MidiaURL, Fonte, DataPublicacao, Metadados, UsuarioUploaderID)
        VALUES (
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.texto')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.midiaUrl')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.fonte')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.dataPublicacao')),
            JSON_EXTRACT(v_ItemJSON, '$.metadados'),
            p_UsuarioID
        );
        SET v_ConteudoID = LAST_INSERT_ID();

        IF p_TiposConteudoJSON IS NOT NULL AND JSON_LENGTH(p_TiposConteudoJSON) > 0 THEN
            INSERT INTO Conteudo_Tipos (ConteudoID, TipoID)
            SELECT v_ConteudoID, T.TipoID FROM TiposDeConteudo T
            JOIN JSON_TABLE(p_TiposConteudoJSON, '$[*]' COLUMNS (Nome VARCHAR(50) PATH '$')) AS TiposSelecionados
            ON T.Nome = TiposSelecionados.Nome;
        END IF;

        INSERT INTO ProcessoDeDeteccao (ConteudoID, AlgoritmoID, UsuarioExecutorID, DataExecucao, Score, Confianca)
        VALUES (
            v_ConteudoID, v_AlgoritmoID, p_UsuarioID, p_DataExecucao,
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.score')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.confianca'))
        );
        SET v_ProcessoID = LAST_INSERT_ID();

        INSERT INTO Rotulo (ProcessoID, CategoriaDetectada, Confianca, Justificativa)
        VALUES (
            v_ProcessoID,
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.categoriaDetectada')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.confiancaRotulo')),
            JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.justificativa'))
        );
        SET i = i + 1;
    END WHILE;
    COMMIT;
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE sp_ArmazenarLoteMidia(
    IN p_UsuarioID INT,
    IN p_NomeDataset VARCHAR(255),
    IN p_DescricaoDataset TEXT,
    IN p_FonteGeral VARCHAR(255),
    IN p_MidiaURL VARCHAR(1024)
)
BEGIN
    INSERT INTO Conteudo (MidiaURL, Fonte, Metadados, UsuarioUploaderID)
    VALUES (
        p_MidiaURL,
        p_FonteGeral,
        JSON_OBJECT('dataset', p_NomeDataset, 'descricao', p_DescricaoDataset),
        p_UsuarioID
    );
END$$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE sp_AdminRegistrarUsuario(
    IN p_AdminUsuarioID INT,
    IN p_NovoUsuarioNome VARCHAR(255),
    IN p_NovoUsuarioEmail VARCHAR(255),
    IN p_SenhaEmTextoPlano VARCHAR(255),
    IN p_NovoUsuarioRole ENUM('admin', 'pesquisador')
)
BEGIN
    DECLARE v_AdminRole VARCHAR(50);
    DECLARE v_SenhaHash VARCHAR(256);
    DECLARE v_EmailCount INT;

    SELECT Role INTO v_AdminRole FROM Usuario WHERE UsuarioID = p_AdminUsuarioID;

    IF v_AdminRole IS NULL OR v_AdminRole != 'admin' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Ação não permitida. Apenas administradores podem registrar novos usuários.';
    END IF;

    SELECT COUNT(*) INTO v_EmailCount FROM Usuario WHERE Email = p_NovoUsuarioEmail;

    IF v_EmailCount > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'O email fornecido já está em uso.';
    END IF;

    SET v_SenhaHash = SHA2(p_SenhaEmTextoPlano, 256);

    INSERT INTO Usuario (Nome, Email, SenhaHash, Role)
    VALUES (p_NovoUsuarioNome, p_NovoUsuarioEmail, v_SenhaHash, p_NovoUsuarioRole);

END$$

DELIMITER ;

-- =====================================================================
-- GATILHOS (TRIGGERS)
-- =====================================================================

DELIMITER $$

CREATE TRIGGER trg_DepoisDeInserirProcesso
AFTER INSERT ON ProcessoDeDeteccao
FOR EACH ROW
BEGIN
    INSERT INTO HistoricoProcessamento (ProcessoID, Status, Observacoes)
    VALUES (NEW.ProcessoID, 'Processado', 'Processo de detecção registrado com sucesso.');
END$$

DELIMITER ;

-- =====================================================================
-- DADOS INICIAIS (PARA TESTE)
-- =====================================================================

-- Inserindo um usuário de teste para que você possa fazer login.
-- Email: teste@email.com
-- Senha: 123456
INSERT INTO Usuario (Nome, Email, SenhaHash, Role) VALUES ('Usuário de Teste', 'teste@email.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'pesquisador');

-- Inserindo tipos de conteúdo básicos
INSERT INTO TiposDeConteudo (Nome) VALUES ('Texto'), ('Imagem'), ('Audio'), ('Video');

