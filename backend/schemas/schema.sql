-- =====================================================================
-- SCHEMA (TABLES)
-- =====================================================================
CREATE TABLE IF NOT EXISTS Usuario (
    UsuarioID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    SenhaHash VARCHAR(255) NOT NULL,
    Role ENUM('admin', 'pesquisador') NOT NULL DEFAULT 'pesquisador',
    DataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS TiposDeConteudo (
    TipoID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Conteudo (
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

CREATE TABLE IF NOT EXISTS Conteudo_Tipos (
    ConteudoID INT NOT NULL,
    TipoID INT NOT NULL,
    PRIMARY KEY (ConteudoID, TipoID),
    FOREIGN KEY (ConteudoID) REFERENCES Conteudo(ConteudoID) ON DELETE CASCADE,
    FOREIGN KEY (TipoID) REFERENCES TiposDeConteudo(TipoID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Algoritmo (
    AlgoritmoID INT PRIMARY KEY AUTO_INCREMENT,
    Nome VARCHAR(255) NOT NULL,
    Versao VARCHAR(50) NOT NULL,
    Parametros JSON,
    Descricao TEXT,
    DataTreinamento DATE,
    UNIQUE (Nome, Versao)
);

CREATE TABLE IF NOT EXISTS ProcessoDeDeteccao (
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

CREATE TABLE IF NOT EXISTS Rotulo (
    RotuloID INT PRIMARY KEY AUTO_INCREMENT,
    ProcessoID INT NOT NULL UNIQUE,
    CategoriaDetectada VARCHAR(50) NOT NULL,
    Confianca FLOAT,
    Justificativa TEXT,
    FOREIGN KEY (ProcessoID) REFERENCES ProcessoDeDeteccao(ProcessoID) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS HistoricoProcessamento (
    HistoricoID INT PRIMARY KEY AUTO_INCREMENT,
    ProcessoID INT NOT NULL,
    DataRegistro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Status VARCHAR(50),
    Observacoes TEXT,
    FOREIGN KEY (ProcessoID) REFERENCES ProcessoDeDeteccao(ProcessoID) ON DELETE CASCADE
);

-- =====================================================================
-- FUNCTIONS
-- =====================================================================
DROP FUNCTION IF EXISTS fn_ObterOuCriarAlgoritmoID;
DELIMITER $$
CREATE FUNCTION fn_ObterOuCriarAlgoritmoID(p_Nome VARCHAR(255), p_Versao VARCHAR(50), p_Parametros JSON, p_DataTreinamento DATE)
RETURNS INT DETERMINISTIC MODIFIES SQL DATA
BEGIN
    DECLARE v_ID INT;
    SELECT AlgoritmoID INTO v_ID FROM Algoritmo WHERE Nome = p_Nome AND Versao = p_Versao;
    IF v_ID IS NULL THEN
        INSERT INTO Algoritmo (Nome, Versao, Parametros, DataTreinamento) VALUES (p_Nome, p_Versao, p_Parametros, p_DataTreinamento);
        SET v_ID = LAST_INSERT_ID();
    END IF;
    RETURN v_ID;
END$$
DELIMITER ;

DROP FUNCTION IF EXISTS fn_ValidarLogin;
DELIMITER $$
CREATE FUNCTION fn_ValidarLogin(p_Email VARCHAR(255), p_SenhaEmTextoPlano VARCHAR(255))
RETURNS INT DETERMINISTIC READS SQL DATA
BEGIN
    DECLARE v_UsuarioID INT DEFAULT 0;
    DECLARE v_SenhaHashArmazenada VARCHAR(256);
    SELECT UsuarioID, SenhaHash INTO v_UsuarioID, v_SenhaHashArmazenada FROM Usuario WHERE Email = p_Email;
    IF v_UsuarioID > 0 AND v_SenhaHashArmazenada = SHA2(p_SenhaEmTextoPlano, 256) THEN
        RETURN v_UsuarioID;
    ELSE
        RETURN 0;
    END IF;
END$$
DELIMITER ;

-- =====================================================================
-- PROCEDURES
-- =====================================================================
DROP PROCEDURE IF EXISTS sp_ProcessarLoteResultados;
DELIMITER $$
CREATE PROCEDURE sp_ProcessarLoteResultados(IN p_UsuarioID INT, IN p_NomeAlgoritmo VARCHAR(255), IN p_VersaoAlgoritmo VARCHAR(50), IN p_ParametrosAlgoritmo JSON, IN p_DataTreinamento DATE, IN p_DataExecucao DATETIME, IN p_TiposConteudoJSON JSON, IN p_LoteDados JSON)
BEGIN
    DECLARE v_AlgoritmoID INT; DECLARE v_ConteudoID INT; DECLARE v_ProcessoID INT; DECLARE v_ItemJSON JSON; DECLARE v_RowCount INT; DECLARE i INT DEFAULT 0;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END;
    START TRANSACTION;
    SET v_AlgoritmoID = fn_ObterOuCriarAlgoritmoID(p_NomeAlgoritmo, p_VersaoAlgoritmo, p_ParametrosAlgoritmo, p_DataTreinamento);
    SET v_RowCount = JSON_LENGTH(p_LoteDados);
    WHILE i < v_RowCount DO
        SET v_ItemJSON = JSON_EXTRACT(p_LoteDados, CONCAT('$[', i, ']'));
        INSERT INTO Conteudo (Texto, MidiaURL, Fonte, DataPublicacao, Metadados, UsuarioUploaderID) VALUES (JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.texto')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.midiaUrl')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.fonte')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.dataPublicacao')), JSON_EXTRACT(v_ItemJSON, '$.metadados'), p_UsuarioID);
        SET v_ConteudoID = LAST_INSERT_ID();
        IF p_TiposConteudoJSON IS NOT NULL AND JSON_LENGTH(p_TiposConteudoJSON) > 0 THEN
            INSERT INTO Conteudo_Tipos (ConteudoID, TipoID) SELECT v_ConteudoID, T.TipoID FROM TiposDeConteudo T JOIN JSON_TABLE(p_TiposConteudoJSON, '$[*]' COLUMNS (Nome VARCHAR(50) PATH '$')) AS TiposSelecionados ON T.Nome = TiposSelecionados.Nome;
        END IF;
        INSERT INTO ProcessoDeDeteccao (ConteudoID, AlgoritmoID, UsuarioExecutorID, DataExecucao, Score, Confianca) VALUES (v_ConteudoID, v_AlgoritmoID, p_UsuarioID, p_DataExecucao, JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.score')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.confianca')));
        SET v_ProcessoID = LAST_INSERT_ID();
        INSERT INTO Rotulo (ProcessoID, CategoriaDetectada, Confianca, Justificativa) VALUES (v_ProcessoID, JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.categoriaDetectada')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.confiancaRotulo')), JSON_UNQUOTE(JSON_EXTRACT(v_ItemJSON, '$.justificativa')));
        SET i = i + 1;
    END WHILE;
    COMMIT;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_ArmazenarLoteMidia;
DELIMITER $$
CREATE PROCEDURE sp_ArmazenarLoteMidia(
    IN p_UsuarioID INT, 
    IN p_NomeDataset VARCHAR(255), 
    IN p_DescricaoDataset TEXT, 
    IN p_FonteGeral VARCHAR(255), 
    IN p_MidiaURL VARCHAR(1024), 
    IN p_TiposConteudoJSON JSON
)
BEGIN
    DECLARE v_ConteudoID INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        ROLLBACK;
        RESIGNAL; 
    END;

    START TRANSACTION; 

    INSERT INTO Conteudo (MidiaURL, Fonte, Metadados, UsuarioUploaderID) 
    VALUES (p_MidiaURL, p_FonteGeral, JSON_OBJECT('dataset', p_NomeDataset, 'descricao', p_DescricaoDataset), p_UsuarioID);
    
    SET v_ConteudoID = LAST_INSERT_ID();

    IF p_TiposConteudoJSON IS NOT NULL AND JSON_LENGTH(p_TiposConteudoJSON) > 0 THEN
        -- Adicionado IGNORE para forçar o MySQL a descartar duplicatas sem gerar erro.
        INSERT IGNORE INTO Conteudo_Tipos (ConteudoID, TipoID) 
        SELECT DISTINCT v_ConteudoID, T.TipoID 
        FROM TiposDeConteudo T 
        JOIN JSON_TABLE(p_TiposConteudoJSON, '$[*]' COLUMNS (Nome VARCHAR(50) PATH '$')) AS TiposSelecionados 
        ON T.Nome = TiposSelecionados.Nome;
    END IF;
    
    COMMIT; 

END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_PesquisaAvancada;
DELIMITER $$
CREATE PROCEDURE sp_PesquisaAvancada(IN p_TextoLivre VARCHAR(255), IN p_NomeAlgoritmo VARCHAR(255), IN p_VersaoAlgoritmo VARCHAR(50), IN p_ParametrosAlgoritmoQuery VARCHAR(255), IN p_ConfiancaMin DECIMAL(5, 2), IN p_ConfiancaMax DECIMAL(5, 2), IN p_ScoreMin DECIMAL(8, 7), IN p_ScoreMax DECIMAL(8, 7), IN p_CategoriaDetectada VARCHAR(50), IN p_FonteConteudo VARCHAR(255), IN p_CategoriaInicial VARCHAR(50), IN p_MetadadosConteudoQuery VARCHAR(255), IN p_TiposConteudoJSON JSON, IN p_DataPublicacaoInicio DATE, IN p_DataPublicacaoFim DATE, IN p_DataExecucaoInicio DATETIME, IN p_DataExecucaoFim DATETIME, IN p_DataTreinamentoInicio DATE, IN p_DataTreinamentoFim DATE, IN p_NomeUploader VARCHAR(255))
BEGIN
    SELECT C.ConteudoID, C.Texto, C.Fonte, C.DataPublicacao, C.MidiaURL, C.CategoriaInicial, A.Nome AS NomeAlgoritmo, A.Versao AS VersaoAlgoritmo, A.DataTreinamento, P.Score, P.Confianca, P.DataExecucao, R.CategoriaDetectada, R.Justificativa, U.Nome AS NomeUploader FROM ProcessoDeDeteccao P JOIN Conteudo C ON P.ConteudoID = C.ConteudoID JOIN Algoritmo A ON P.AlgoritmoID = A.AlgoritmoID JOIN Rotulo R ON P.ProcessoID = R.ProcessoID LEFT JOIN Usuario U ON C.UsuarioUploaderID = U.UsuarioID
    WHERE (p_TextoLivre IS NULL OR C.Texto LIKE CONCAT('%', p_TextoLivre, '%') OR R.Justificativa LIKE CONCAT('%', p_TextoLivre, '%')) AND (p_NomeAlgoritmo IS NULL OR A.Nome LIKE CONCAT('%', p_NomeAlgoritmo, '%')) AND (p_VersaoAlgoritmo IS NULL OR A.Versao = p_VersaoAlgoritmo) AND (p_ParametrosAlgoritmoQuery IS NULL OR CAST(A.Parametros AS CHAR) LIKE CONCAT('%', p_ParametrosAlgoritmoQuery, '%')) AND (p_ConfiancaMin IS NULL OR P.Confianca >= p_ConfiancaMin) AND (p_ConfiancaMax IS NULL OR P.Confianca <= p_ConfiancaMax) AND (p_ScoreMin IS NULL OR P.Score >= p_ScoreMin) AND (p_ScoreMax IS NULL OR P.Score <= p_ScoreMax) AND (p_CategoriaDetectada IS NULL OR R.CategoriaDetectada = p_CategoriaDetectada) AND (p_FonteConteudo IS NULL OR C.Fonte LIKE CONCAT('%', p_FonteConteudo, '%')) AND (p_CategoriaInicial IS NULL OR C.CategoriaInicial = p_CategoriaInicial) AND (p_MetadadosConteudoQuery IS NULL OR CAST(C.Metadados AS CHAR) LIKE CONCAT('%', p_MetadadosConteudoQuery, '%')) AND (p_DataPublicacaoInicio IS NULL OR C.DataPublicacao >= p_DataPublicacaoInicio) AND (p_DataPublicacaoFim IS NULL OR C.DataPublicacao <= p_DataPublicacaoFim) AND (p_DataExecucaoInicio IS NULL OR P.DataExecucao >= p_DataExecucaoInicio) AND (p_DataExecucaoFim IS NULL OR P.DataExecucao <= p_DataExecucaoFim) AND (p_DataTreinamentoInicio IS NULL OR A.DataTreinamento >= p_DataTreinamentoInicio) AND (p_DataTreinamentoFim IS NULL OR A.DataTreinamento <= p_DataTreinamentoFim) AND (p_NomeUploader IS NULL OR U.Nome LIKE CONCAT('%', p_NomeUploader, '%')) AND (p_TiposConteudoJSON IS NULL OR JSON_LENGTH(p_TiposConteudoJSON) = 0 OR EXISTS (SELECT 1 FROM Conteudo_Tipos CT JOIN TiposDeConteudo TC ON CT.TipoID = TC.TipoID JOIN JSON_TABLE(p_TiposConteudoJSON, '$[*]' COLUMNS (Nome VARCHAR(50) PATH '$')) AS TiposSelecionados ON TC.Nome = TiposSelecionados.Nome WHERE CT.ConteudoID = C.ConteudoID))
    ORDER BY P.DataExecucao DESC;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_PesquisarMidiaArmazenada;
DELIMITER $$
CREATE PROCEDURE sp_PesquisarMidiaArmazenada(IN p_TextoLivre VARCHAR(255), IN p_NomeDataset VARCHAR(255), IN p_Fonte VARCHAR(255), IN p_TiposConteudoJSON JSON, IN p_NomeUploader VARCHAR(255))
BEGIN
    SELECT C.ConteudoID, C.MidiaURL, C.Fonte, C.DataPublicacao, C.Metadados, U.Nome AS NomeUploader, (SELECT GROUP_CONCAT(TC.Nome SEPARATOR ', ') FROM Conteudo_Tipos CT JOIN TiposDeConteudo TC ON CT.TipoID = TC.TipoID WHERE CT.ConteudoID = C.ConteudoID) AS TiposDeConteudo FROM Conteudo C LEFT JOIN Usuario U ON C.UsuarioUploaderID = U.UsuarioID
    WHERE NOT EXISTS (SELECT 1 FROM ProcessoDeDeteccao P WHERE P.ConteudoID = C.ConteudoID) AND (p_TextoLivre IS NULL OR JSON_UNQUOTE(JSON_EXTRACT(C.Metadados, '$.dataset')) LIKE CONCAT('%', p_TextoLivre, '%') OR JSON_UNQUOTE(JSON_EXTRACT(C.Metadados, '$.descricao')) LIKE CONCAT('%', p_TextoLivre, '%')) AND (p_NomeDataset IS NULL OR JSON_UNQUOTE(JSON_EXTRACT(C.Metadados, '$.dataset')) LIKE CONCAT('%', p_NomeDataset, '%')) AND (p_Fonte IS NULL OR C.Fonte LIKE CONCAT('%', p_Fonte, '%')) AND (p_NomeUploader IS NULL OR U.Nome LIKE CONCAT('%', p_NomeUploader, '%')) AND (p_TiposConteudoJSON IS NULL OR JSON_LENGTH(p_TiposConteudoJSON) = 0 OR EXISTS (SELECT 1 FROM Conteudo_Tipos CT JOIN TiposDeConteudo TC ON CT.TipoID = TC.TipoID JOIN JSON_TABLE(p_TiposConteudoJSON, '$[*]' COLUMNS (Nome VARCHAR(50) PATH '$')) AS TiposSelecionados ON TC.Nome = TiposSelecionados.Nome WHERE CT.ConteudoID = C.ConteudoID));
END$$
DELIMITER ;

-- --- NOVA PROCEDURE ADICIONADA ---
DROP PROCEDURE IF EXISTS sp_AdminRegistrarUsuario;
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
-- TRIGGERS
-- =====================================================================
DROP TRIGGER IF EXISTS trg_DepoisDeInserirProcesso;
DELIMITER $$
CREATE TRIGGER trg_DepoisDeInserirProcesso AFTER INSERT ON ProcessoDeDeteccao FOR EACH ROW
BEGIN
    INSERT INTO HistoricoProcessamento (ProcessoID, Status, Observacoes)
    VALUES (NEW.ProcessoID, 'Processado', 'Processo de detecção registrado com sucesso.');
END$$
DELIMITER ;

-- =====================================================================
-- DADOS INICIAIS (PARA TESTE)
-- =====================================================================

-- --- CORREÇÃO APLICADA AQUI ---
-- Desativa temporariamente a verificação de chaves estrangeiras para permitir a limpeza das tabelas
SET FOREIGN_KEY_CHECKS=0;

-- Limpa as tabelas de usuários e tipos de conteúdo para garantir um estado limpo
TRUNCATE TABLE Usuario;
TRUNCATE TABLE TiposDeConteudo;
-- Também é uma boa ideia limpar a tabela Conteudo, que depende do Usuario
TRUNCATE TABLE Conteudo; 

-- Reativa a verificação de chaves estrangeiras
SET FOREIGN_KEY_CHECKS=1;
-- ---------------------------------

-- Insere o utilizador de teste com o perfil de ADMIN
INSERT INTO Usuario (Nome, Email, SenhaHash, Role) VALUES ('Administrador de Teste', 'teste@email.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92', 'admin');

-- Insere os tipos de conteúdo básicos
INSERT INTO TiposDeConteudo (Nome) VALUES ('Texto'), ('Imagem'), ('Audio'), ('Video');