import pymysql.cursors
from PyQt5 import QtWidgets, QtCore
from conexao import conectar  # Usa a sua conexão padrão do PyMySQL

def inicializar(tela):
    """Busca os dados da tabela 'configuracao' e preenche os campos ao abrir o programa."""
    try:
        print("Tentando carregar configurações do banco de dados...")
        conexao = conectar()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        
        # Busca o registro com ID 1
        cursor.execute("SELECT * FROM configuracao WHERE id_config = 1")
        dados = cursor.fetchone()
        
        if dados:
            print("Dados encontrados no banco:", dados)
            
            # Preenche os campos na tela tratando valores nulos
            tela.txt_configNomeEmpresa.setText(str(dados['nome_empresa']) if dados['nome_empresa'] else "")
            tela.txt_configCnpjEmpresa.setText(str(dados['cnpj']) if dados['cnpj'] else "")
            tela.txt_configTelEmpresa.setText(str(dados['telefone']) if dados['telefone'] else "")
            tela.txt_configEmailEmpresa.setText(str(dados['email']) if dados['email'] else "")
            tela.txt_configEnderecoEmpresa.setText(str(dados['endereco']) if dados['endereco'] else "")
            tela.txt_configCidadeEmpresa.setText(str(dados['cidade']) if dados['cidade'] else "")
            
            # Carrega a hora de abertura
            if dados['hora_abertura']:
                hora_ab = QtCore.QTime.fromString(dados['hora_abertura'], "HH:mm")
                tela.timeAbertura.setTime(hora_ab)
            else:
                tela.timeAbertura.setTime(QtCore.QTime(8, 0))
                
            # Carrega a hora de fechamento
            if dados['hora_fechamento']:
                hora_fech = QtCore.QTime.fromString(dados['hora_fechamento'], "HH:mm")
                tela.timeFechamento.setTime(hora_fech)
            else:
                tela.timeFechamento.setTime(QtCore.QTime(18, 0))
                
            print("Campos preenchidos na interface com sucesso!")
        else:
            print("AVISO: Nenhum registro com id_config = 1 foi encontrado na tabela 'configuracao'!")

        cursor.close()
        conexao.close()
    except Exception as e:
        print("ERRO CRÍTICO ao inicializar configurações:", e)
        QtWidgets.QMessageBox.critical(tela, "Erro", f"Não foi possível carregar as configurações: {str(e)}")


def salvar(tela):
    """Pega os dados digitados na tela e atualiza no banco de dados no ID 1."""
    nome = tela.txt_configNomeEmpresa.text().strip()
    cnpj = tela.txt_configCnpjEmpresa.text().strip()
    telefone = tela.txt_configTelEmpresa.text().strip()
    email = tela.txt_configEmailEmpresa.text().strip()
    endereco = tela.txt_configEnderecoEmpresa.text().strip()
    cidade = tela.txt_configCidadeEmpresa.text().strip()
    
    hora_abertura = tela.timeAbertura.time().toString("HH:mm")
    hora_fechamento = tela.timeFechamento.time().toString("HH:mm")

    if not nome:
        QtWidgets.QMessageBox.warning(tela, "Aviso", "O Nome da Confeitaria é obrigatório!")
        return

    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        # Query direta apontando para as colunas corretas do seu banco de dados
        sql = """
            UPDATE configuracao 
            SET nome_empresa = %s, cnpj = %s, telefone = %s, email = %s, 
                endereco = %s, cidade = %s, hora_abertura = %s, hora_fechamento = %s 
            WHERE id_config = 1
        """
        valores = (nome, cnpj, telefone, email, endereco, cidade, hora_abertura, hora_fechamento)
        
        print(f"Tentando salvar no ID 1 com os valores: {valores}")
        cursor.execute(sql, valores)
        conexao.commit()
        
        cursor.close()
        conexao.close()
        
        print("Dados salvos e commitado no banco com sucesso!")
        QtWidgets.QMessageBox.information(tela, "Sucesso", "Configurações salvas com sucesso!")
    except Exception as e:
        print("ERRO ao salvar configurações:", e)
        QtWidgets.QMessageBox.critical(tela, "Erro", f"Não foi possível salvar as configurações: {str(e)}")


def gerenciar_usuarios(tela):
    """Ação para o botão 'Gerenciar usuários' que abre a janela popup modal."""
    from usuarios import ModalUsuarios
    
    # Cria a nossa nova janela modal
    janela_popup = ModalUsuarios(tela)
    
    # O .exec_() faz a janela abrir obrigatoriamente por cima (como um modal legítimo)
    janela_popup.exec_()



def fazer_backup_banco(tela):
    """Gera um backup estruturado de todo o banco db_confeitaria em um arquivo .sql escolhido pelo usuário."""
    # Abre a caixa de diálogo para salvar o arquivo na máquina do usuário
    caminho_destino, _ = QtWidgets.QFileDialog.getSaveFileName(
        tela, "Exportar Backup do Banco de Dados", "backup_mira_confeitaria.sql", "Script SQL (*.sql)"
    )
    
    # Se o usuário cancelar a janela de escolha, interrompe a função
    if not caminho_destino:
        return
        
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        
        # 1. Pega a lista de todas as tabelas criadas no db_confeitaria
        cursor.execute("SHOW TABLES")
        tabelas = [linha[0] for linha in cursor.fetchall()]
        
        with open(caminho_destino, "w", encoding="utf-8") as f:
            # Cabeçalho do arquivo de backup
            f.write("-- ======================================================\n")
            f.write("-- BACKUP COMPLETO - MIRA CONFEITARIA\n")
            f.write("-- ======================================================\n\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")  # Desativa chaves estrangeiras temporariamente para evitar erros ao restaurar
            
            for tabela in tabelas:
                f.write(f"-- ------------------------------------------------------\n")
                f.write(f"-- Estrutura e dados para a tabela `{tabela}`\n")
                f.write(f"-- ------------------------------------------------------\n\n")
                
                # 2. Copia a estrutura exata de criação da tabela (CREATE TABLE)
                cursor.execute(f"SHOW CREATE TABLE `{tabela}`")
                create_table_sql = cursor.fetchone()[1]
                f.write(f"DROP TABLE IF EXISTS `{tabela}`;\n")
                f.write(f"{create_table_sql};\n\n")
                
                # 3. Busca todas as linhas de dados da tabela para gerar os INSERTS
                cursor.execute(f"SELECT * FROM `{tabela}`")
                linhas = cursor.fetchall()
                
                if linhas:
                    f.write(f"-- Despejando dados da tabela `{tabela}`\n")
                    for linha in linhas:
                        valores = []
                        for item in linha:
                            if item is None:
                                valores.append("NULL")
                            elif isinstance(item, (int, float)):
                                valores.append(str(item))
                            else:
                                # Escapa as aspas simples para não quebrar a query SQL
                                item_escapado = str(item).replace("'", "''")
                                valores.append(f"'{item_escapado}'")
                        
                        valores_str = ", ".join(valores)
                        f.write(f"INSERT INTO `{tabela}` VALUES ({valores_str});\n")
                    f.write("\n")
            
            f.write("SET FOREIGN_KEY_CHECKS = 1;\n")  # Reativa as chaves estrangeiras
            
        cursor.close()
        conexao.close()
        
        QtWidgets.QMessageBox.information(tela, "Backup Concluído", "Cópia de segurança (.sql) gerada com sucesso!")
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(tela, "Erro no Backup", f"Falha ao gerar cópia de segurança: {str(e)}")



def exibir_sobre_sistema(tela):
    QtWidgets.QMessageBox.about(
        tela, 
        "Sobre o Sistema", 
        "MIRA Confeitaria - Sistema de Gerenciamento Local" \
        "  Versão: 1.0.0" \
        "   Ambiente: XAMPP / VS Code."
    
        
    )
