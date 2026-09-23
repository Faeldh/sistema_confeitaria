from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from conexao import conectar

# =============================================================================
# 🎓 AULA 1: MOTOR DE BUSCA CHROME (QCompleter) E MODELAGEM DE INPUTS
# Criamos a propriedade 'completer_tipos' direto no self (janela principal).
# Usamos o QCompleter para transformar a LineEdit em um campo de busca 
# preditiva inteligente que ignora maiúsculas e minúsculas (CaseInsensitive).
# =============================================================================
def configurar_campos(self):
    """Aplica o visual moderno, ativa as máscaras inteligentes por código, o Completer e o clique direito"""
    # 🔍 MÁSCARA FIXA DE TELEFONE
    self.txt_telefoneFornecedor.setInputMask("(00) 00000-0000;_")
    
    # Restringe o campo de CPF/CNPJ para aceitar no máximo 18 caracteres (tamanho máximo de um CNPJ pontuado)
    self.txt_cpfCnpj.setMaxLength(18)
    
    # 🔍 RECALCULADOR INTELIGENTE POR CÓDIGO: Formata dinamicamente enquanto digita
    try:
        self.txt_cpfCnpj.textEdited.disconnect()
    except:
        pass
    self.txt_cpfCnpj.textEdited.connect(lambda: checar_mascara_dinamica_fornecedor(self))

    # 🌟 MOTOR CHROME BLINDADO: Instancia o completador direto na janela principal
    self.completer_tipos = QtWidgets.QCompleter(self)
    self.completer_tipos.setFilterMode(Qt.MatchStartsWith)
    self.completer_tipos.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
    self.completer_tipos.setCaseSensitivity(Qt.CaseInsensitive)
    self.txt_tipoFornecedor.setCompleter(self.completer_tipos)
    
    # 🔍 CLIQUE DIREITO ATIVO: Altera a política do campo para aceitar menu de contexto
    self.txt_tipoFornecedor.setContextMenuPolicy(Qt.CustomContextMenu)
    try:
        self.txt_tipoFornecedor.customContextMenuRequested.disconnect()
    except:
        pass
    self.txt_tipoFornecedor.customContextMenuRequested.connect(lambda pos: abrir_menu_clique_direito_tipo(self, pos))

    # Configuração estética e amigável da tabela central de fornecedores (Efeito Clean)
    self.tableWidgetFornecedores.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    self.tableWidgetFornecedores.setShowGrid(False)
    self.tableWidgetFornecedores.setStyleSheet("""
        QTableWidget { background-color: white; border: 2px solid #3F4A2F; border-radius: 10px; gridline-color: transparent; }
        QTableWidget::item { border-bottom: 1px solid #3F4A2F; padding: 6px; color: #2D3748; }
        QTableWidget::item:selected { background-color: #3F4A2F; color: #E6D2A2; }
        QHeaderView::section { background-color: #3F4A2F; color: #E6D2A2; padding: 6px; border: none; font-weight: bold; qproperty-alignment: AlignCenter; }
    """)
    
    carregar_tipos_completer(self)
def checar_mascara_dinamica_fornecedor(self):
    """Aplica a pontuação de CPF ou CNPJ por código de forma fluída e sem prender o teclado"""
    # Captura apenas os números puros que o usuário digitou
    texto_puro = ''.join(filter(str.isdigit, self.txt_cpfCnpj.text()))

    # 🔍 MODO CPF: Formata até 11 dígitos
    if len(texto_puro) <= 11:
        if len(texto_puro) > 3: 
            texto_puro = texto_puro[:3] + '.' + texto_puro[3:]
        if len(texto_puro) > 7: 
            texto_puro = texto_puro[:7] + '.' + texto_puro[7:]
        if len(texto_puro) > 11: 
            texto_puro = texto_puro[:11] + '-' + texto_puro[11:]
        texto_formatado = texto_puro[:14]
        
    # 🔍 MODO CNPJ: Se passar de 11 dígitos, remonta as pontuações no padrão de empresa
    else:
        if len(texto_puro) > 2: 
            texto_puro = texto_puro[:2] + '.' + texto_puro[2:]
        if len(texto_puro) > 6: 
            texto_puro = texto_puro[:6] + '.' + texto_puro[6:]
        if len(texto_puro) > 10: 
            texto_puro = texto_puro[:10] + '/' + texto_puro[10:]
        if len(texto_puro) > 15: 
            texto_puro = texto_puro[:15] + '-' + texto_puro[15:]
        texto_formatado = texto_puro[:18]

    # Atualiza o campo na tela de forma segura sem gerar loops na memória
    self.txt_cpfCnpj.blockSignals(True)
    self.txt_cpfCnpj.setText(texto_formatado)
    self.txt_cpfCnpj.setCursorPosition(len(texto_formatado))
    self.txt_cpfCnpj.blockSignals(False)

# =============================================================================
# 🎓 AULA 2: CADEIA DE EVENTOS DO MENU DE CONTEXTO (Clique Direito)
# O método QMenu() cria o pequeno quadrado flutuante na posição exata do cursor.
# Permite realizar caixas de diálogos para a edição rápida e exclusão do tipo.
# =============================================================================
def abrir_menu_clique_direito_tipo(self, posicao):
    """Gera o menu flutuante de Editar ou Excluir ao clicar com o botão direito no campo"""
    texto_atual = self.txt_tipoFornecedor.text().strip()
    if not texto_atual:
        return 
        
    menu = QtWidgets.QMenu(self)
    acao_editar = menu.addAction("✏️ Editar Tipo")
    acao_excluir = menu.addAction("🗑️ Excluir Tipo")
    
    acao_selecionada = menu.exec_(self.txt_tipoFornecedor.mapToGlobal(posicao))
    
    if acao_selecionada == acao_editar:
        novo_nome, ok = QtWidgets.QInputDialog.getText(
            self, "Editar Tipo de Fornecedor", 
            f"Altere o nome do tipo '{texto_atual}':", 
            QtWidgets.QLineEdit.Normal, texto_atual
        )
        if ok and novo_nome.strip():
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("UPDATE tipo_fornecedor SET nome = %s WHERE nome = %s", (novo_nome.strip(), texto_atual))
            conexao.commit()
            self.txt_tipoFornecedor.setText(novo_nome.strip())
            carregar_tipos_completer(self)
            QtWidgets.QMessageBox.information(self, "Sucesso", "Tipo de fornecedor atualizado com sucesso!")

    elif acao_selecionada == acao_excluir:
        resposta = QtWidgets.QMessageBox.question(
            self, "Excluir Tipo", 
            f"Tem certeza que deseja permanentemente excluir o tipo '{texto_atual}'?\nIsso pode afetar outros registros.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if resposta == QtWidgets.QMessageBox.Yes:
            conexao = conectar()
            cursor = conexao.cursor()
            try:
                cursor.execute("DELETE FROM tipo_fornecedor WHERE nome = %s", (texto_atual,))
                conexao.commit()
                self.txt_tipoFornecedor.clear()
                carregar_tipos_completer(self)
                QtWidgets.QMessageBox.information(self, "Sucesso", "Tipo de fornecedor removido!")
            except:
                QtWidgets.QMessageBox.warning(self, "Erro", "Não é possível excluir um tipo que possui fornecedores ativos vinculados!")
# ---------------- SALVAR OU ATUALIZAR FORNECEDOR (Automatizado) ----------------
# =============================================================================
# 🎓 AULA 3: GRAVAÇÃO INTELIGENTE COM CADASTRO SILENCIOSO DE CATEGORIAS
# Esta rotina avalia se a categoria (tipo) descrita já existe na base de dados.
# Se for uma categoria inédita, o Python faz um INSERT automático em segundo plano
# na tabela 'tipo_fornecedor', alimentando o preenchimento Chrome sem poluir a tela!
# =============================================================================
def salvar(self):
    """Salva o fornecedor e cadastra o tipo no banco de forma automática caso seja novo"""
    nome = self.txt_nomeFornecedor.text().strip()
    tipo = self.txt_tipoFornecedor.text().strip() 
    
    cpf_cnpj = self.txt_cpfCnpj.text().replace('.', '').replace('-', '').replace('/', '').replace('_', '').strip()
    telefone = self.txt_telefoneFornecedor.text().replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('_', '').strip()
    
    email = self.txt_emailFornecedor.text().strip()
    rua = self.txt_ruaFornecedor.text().strip()
    numero = self.txt_numFornecedor.text().strip()
    bairro = self.txt_bairroFornecedor.text().strip()
    cidade = self.txt_cidadeFornecedor.text().strip()
    complemento = self.txt_complementoFornecedor.text().strip()
    info = self.txt_infoAdicionais.toPlainText().strip()

    if not nome:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'O nome do fornecedor é obrigatório!')
        return
        
    if not tipo:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'O tipo de fornecedor é obrigatório!')
        return

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        # Verifica se o tipo de insumo já existe globalmente cadastrado no phpMyAdmin
        cursor.execute("SELECT id_tipo FROM tipo_fornecedor WHERE nome = %s", (tipo,))
        res_tipo = cursor.fetchone()
        
        if not res_tipo:
            # Cadastra dinamicamente na tabela filha caso o tipo não exista
            cursor.execute("INSERT INTO tipo_fornecedor (nome) VALUES (%s)", (tipo,))
            conexao.commit()
            carregar_tipos_completer(self)

        # --- MODO 1: ATUALIZAÇÃO DE REGISTRO (UPDATE) ---
        if hasattr(self, 'id_fornecedor') and self.id_fornecedor:
            sql = """
                UPDATE fornecedor
                SET nome=%s, tipo=%s, cpf_cnpj=%s, telefone=%s, email=%s, rua=%s,
                    numero=%s, bairro=%s, cidade=%s, complemento=%s, informacoes=%s
                WHERE id_fornecedor=%s
            """
            dados = (nome, tipo, cpf_cnpj, telefone, email, rua, numero, bairro, cidade, complemento, info, self.id_fornecedor)
            cursor.execute(sql, dados)
            conexao.commit()
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'Ficha do fornecedor atualizada com sucesso!')
            atualizar(self)
            limpar(self)
            return

        # --- MODO 2: NOVO CADASTRO (INSERT) ---
        sql = """
            INSERT INTO fornecedor
            (nome, tipo, cpf_cnpj, telefone, email, rua, numero, bairro, cidade, complemento, informacoes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        dados = (nome, tipo, cpf_cnpj, telefone, email, rua, numero, bairro, cidade, complemento, info)
        cursor.execute(sql, dados)
        conexao.commit()

        if cursor.rowcount > 0:
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'Fornecedor cadastrado com sucesso!')
            atualizar(self)
            limpar(self)
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Erro', f'Falha operacional no banco de dados: {e}')
# =============================================================================
# 🎓 AULA 4: LISTAGEM HIGIENIZADA POR POSIÇÃO DA TUPLA
# O comando fetchall() envia as linhas do MySQL estruturadas em tuplas.
# Para eliminar de vez as aspas ('',) e parênteses feios da tabela, extraímos 
# cada dado por sua posição numérica rígida no SELECT: dados[0], dados[1]...
# Aqui também injetamos o botão de texto "X" cinza com efeito hover vermelho.
# =============================================================================
def atualizar(self):
    """Busca os fornecedores no banco e preenche a tabela com alinhamento centralizado e o X discreto"""
    conexao = conectar()
    cursor = conexao.cursor()

    sql = "SELECT id_fornecedor, nome, tipo, cpf_cnpj, telefone FROM fornecedor ORDER BY nome"
    cursor.execute(sql)
    resultado = cursor.fetchall()

    self.tableWidgetFornecedores.setRowCount(0)
    self.tableWidgetFornecedores.setColumnCount(6) # ID, Nome, Tipo, CPF/CNPJ, Telefone, Excluir
    self.tableWidgetFornecedores.setHorizontalHeaderLabels(["ID", "Nome", "Tipo", "CPF/CNPJ", "Telefone", ""])

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetFornecedores.insertRow(row_num)
        
        # 🌟 EXTRAÇÃO EM ÍNDICES SEGUROS: Limpa por completo as aspas da sua listagem
        id_forn = str(row_data[0])
        nome_forn = str(row_data[1])
        tipo_forn = str(row_data[2])
        doc_forn = str(row_data[3])
        tel_forn = str(row_data[4])

        # Formatação visual de CPF ou CNPJ automática dentro das células
        if len(doc_forn) == 14:
            doc_formatado = f"{doc_forn[:2]}.{doc_forn[2:5]}.{doc_forn[5:8]}/{doc_forn[8:12]}-{doc_forn[12:]}"
        elif len(doc_forn) == 11:
            doc_formatado = f"{doc_forn[:3]}.{doc_forn[3:6]}.{doc_forn[6:9]}-{doc_forn[9:]}"
        else:
            doc_formatado = doc_forn

        # Formatação visual de telefone celular ou fixo com DDD na tabela
        tel_formatado = f"({tel_forn[:2]}) {tel_forn[2:7]}-{tel_forn[7:]}" if len(tel_forn) == 11 else tel_forn

        # Cria os itens de célula
        item_id = QtWidgets.QTableWidgetItem(id_forn)
        item_nome = QtWidgets.QTableWidgetItem(nome_forn)
        item_tipo = QtWidgets.QTableWidgetItem(tipo_forn)
        item_doc = QtWidgets.QTableWidgetItem(doc_formatado)
        item_tel = QtWidgets.QTableWidgetItem(tel_formatado)

        # Força o alinhamento de cada dado exatamente no CENTRO da célula
        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)
        item_tipo.setTextAlignment(Qt.AlignCenter)
        item_doc.setTextAlignment(Qt.AlignCenter)
        item_tel.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetFornecedores.setItem(row_num, 0, item_id)
        self.tableWidgetFornecedores.setItem(row_num, 1, item_nome)
        self.tableWidgetFornecedores.setItem(row_num, 2, item_tipo)
        self.tableWidgetFornecedores.setItem(row_num, 3, item_doc)
        self.tableWidgetFornecedores.setItem(row_num, 4, item_tel)

        # 🔍 DESIGN DISCRETO DO "X": Fino, elegante e ganha o realce vermelho moderno no hover
        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { background-color: transparent; color: #718096; font-size: 13px; font-weight: bold; border: none; padding: 0px; margin: 0px; }
            QPushButton:hover { color: #E53E3E; font-size: 15px; }
        """)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(lambda checked, id_f=id_forn, nome_f=nome_forn: deletar_pela_tabela(self, id_f, nome_f))

        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        self.tableWidgetFornecedores.setCellWidget(row_num, 5, container)

    header = self.tableWidgetFornecedores.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignCenter)
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch) 
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
    
    carregar_tipos_completer(self)
# =============================================================================
# 🎓 AULA 5: FILTRAGEM DINÂMICA LOUWER E CARGA DE DADOS COM ÍNDICES SEGUROS
# A instrução LOWER() converte tudo para minúsculo na hora de comparar no banco,
# garantindo que a busca filtre de forma mágica independente do Caps Lock.
# O blockSignals(True) na rotina de limpar esvazia a tela e reinstala o placeholder
# cinza sem que as funções automáticas se engalfinhem em loops invisíveis.
# =============================================================================
def pesquisa(self):
    """Filtra a tabela dinamicamente por Nome, Segmento/Tipo, CPF/CNPJ ou Cidade enquanto o usuário digita"""
    texto = self.lineEditPesquisaFornecedor.text().strip()

    conexao = conectar()
    cursor = conexao.cursor()

    # 🚀 MOTOR DE BUSCA EXPANDIDO: Agora varre Nome, Tipo/Segmento, CPF/CNPJ e Cidade de uma só vez!
    sql = """
    SELECT id_fornecedor, nome, tipo, cpf_cnpj, telefone 
    FROM fornecedor 
    WHERE LOWER(nome) LIKE LOWER(%s) 
       OR LOWER(tipo) LIKE LOWER(%s) 
       OR LOWER(cpf_cnpj) LIKE LOWER(%s)
       OR LOWER(cidade) LIKE LOWER(%s)
    ORDER BY nome
    """
    
    # O sinal de porcentagem "%" antes e depois garante que ele ache o termo no início, meio ou fim da palavra!
    like = f"%{texto}%"
    
    # Enviamos o parâmetro de busca para preencher cada uma das 4 opções da query acima
    cursor.execute(sql, (like, like, like, like))
    resultado = cursor.fetchall()

    self.tableWidgetFornecedores.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetFornecedores.insertRow(row_num)
        
        id_forn = str(row_data[0])
        nome_forn = str(row_data[1])
        tipo_forn = str(row_data[2])
        doc_forn = str(row_data[3])
        tel_forn = str(row_data[4])

        # Trata formatação visual de CPF ou CNPJ automática na listagem
        if len(doc_forn) == 14:
            doc_formatado = f"{doc_forn[:2]}.{doc_forn[2:5]}.{doc_forn[5:8]}/{doc_forn[8:12]}-{doc_forn[12:]}"
        elif len(doc_forn) == 11:
            doc_formatado = f"{doc_forn[:3]}.{doc_forn[3:6]}.{doc_forn[6:9]}-{doc_forn[9:]}"
        else:
            doc_formatado = doc_forn

        tel_formatado = f"({tel_forn[:2]}) {tel_forn[2:7]}-{tel_forn[7:]}" if len(tel_forn) == 11 else tel_forn

        item_id = QtWidgets.QTableWidgetItem(id_forn)
        item_nome = QtWidgets.QTableWidgetItem(nome_forn)
        item_tipo = QtWidgets.QTableWidgetItem(tipo_forn)
        item_doc = QtWidgets.QTableWidgetItem(doc_formatado)
        item_tel = QtWidgets.QTableWidgetItem(tel_formatado)

        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)
        item_tipo.setTextAlignment(Qt.AlignCenter)
        item_doc.setTextAlignment(Qt.AlignCenter)
        item_tel.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetFornecedores.setItem(row_num, 0, item_id)
        self.tableWidgetFornecedores.setItem(row_num, 1, item_nome)
        self.tableWidgetFornecedores.setItem(row_num, 2, item_tipo)
        self.tableWidgetFornecedores.setItem(row_num, 3, item_doc)
        self.tableWidgetFornecedores.setItem(row_num, 4, item_tel)

        # Injeta o botão minimalista de exclusão "X" com efeito Hover vermelho
        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { background-color: transparent; color: #718096; font-size: 13px; font-weight: bold; border: none; padding: 0px; margin: 0px; }
            QPushButton:hover { color: #E53E3E; font-size: 15px; }
        """)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(lambda checked, id_f=id_forn, nome_f=nome_forn: deletar_pela_tabela(self, id_f, nome_f))

        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        self.tableWidgetFornecedores.setCellWidget(row_num, 5, container)


def deletar_pela_tabela(self, id_fornecedor, nome_fornecedor):
    """Abre um alerta de confirmação humana e deleta o fornecedor do banco de dados"""
    confirmacao = QtWidgets.QMessageBox.question(
        self, 'Confirmar exclusão',
        f'Tem certeza que deseja permanentemente excluir o fornecedor "{nome_fornecedor}"?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )

    if confirmacao == QtWidgets.QMessageBox.No:
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM fornecedor WHERE id_fornecedor = %s", (id_fornecedor,))
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Fornecedor excluído com sucesso!')
        limpar(self)
        atualizar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível excluir o fornecedor.')

def carregar_tipos_completer(self):
    """Alimenta o motor invisível do Chrome de forma blindada contra erros de inicialização"""
    if not hasattr(self, 'completer_tipos'):
        return

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT nome FROM tipo_fornecedor ORDER BY nome")
        resultado = cursor.fetchall()
        
        # Puxa o texto cru desempacotando o índice [0] da tupla para a lista do Chrome ler
        lista_palavras = [str(linha[0]) for linha in resultado]
        
        modelo_palavras = QtCore.QStringListModel(lista_palavras)
        self.completer_tipos.setModel(modelo_palavras)
    except Exception as e:
        print(f"Erro ao alimentar o Completer de tipos: {e}")

def buscar_por_id(self, id_fornecedor):
    """Recupera os registros do fornecedor clicado por tuplas exatas e preenche as caixas de texto"""
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT nome, tipo, cpf_cnpj, telefone, email,
           rua, numero, bairro, cidade, complemento, informacoes
    FROM fornecedor
    WHERE id_fornecedor = %s
    """
    cursor.execute(sql, (id_fornecedor,))
    resultado = cursor.fetchone()

    if resultado:
        self.txt_cpfCnpj.blockSignals(True)

        # Desempacota os índices numéricos rígidos retirando as aspas da tela
        self.txt_nomeFornecedor.setText(str(resultado[0]))
        self.txt_tipoFornecedor.setText(str(resultado[1])) 
        self.txt_cpfCnpj.setText(str(resultado[2]))
        self.txt_telefoneFornecedor.setText(str(resultado[3]))
        self.txt_emailFornecedor.setText(str(resultado[4]))
        self.txt_ruaFornecedor.setText(str(resultado[5]))
        self.txt_numFornecedor.setText(str(resultado[6]))
        self.txt_bairroFornecedor.setText(str(resultado[7]))
        self.txt_cidadeFornecedor.setText(str(resultado[8]))
        self.txt_complementoFornecedor.setText(str(resultado[9]))
        self.txt_infoAdicionais.setPlainText(str(resultado[10]))

        self.id_fornecedor = id_fornecedor
        self.btn_salvarFornecedor.setText("Salvar Alterações")
        self.btn_limparFornecedor.setText("Limpar Formulário")

        self.txt_cpfCnpj.blockSignals(False)

def limpar(self):
    """Zera proativamente todas as caixas de texto da esquerda sem risco de disparar loops de eventos"""
    self.tableWidgetFornecedores.blockSignals(True)
    self.txt_cpfCnpj.blockSignals(True)

    self.txt_nomeFornecedor.setText('')
    self.txt_tipoFornecedor.setText('') 
    self.txt_cpfCnpj.clear() # Limpeza absoluta para o placeholder pular na tela
    self.txt_cpfCnpj.setPlaceholderText("000.000.000-00 ou CNPJ")
    self.txt_cpfCnpj.setMaxLength(18)
    
    self.txt_telefoneFornecedor.setText('')
    self.txt_emailFornecedor.setText('')
    self.txt_ruaFornecedor.setText('')
    self.txt_numFornecedor.setText('')
    self.txt_bairroFornecedor.setText('')
    self.txt_cidadeFornecedor.setText('')
    self.txt_complementoFornecedor.setText('')
    self.txt_infoAdicionais.clear()
    
    self.txt_nomeFornecedor.repaint()
    self.txt_cpfCnpj.repaint()
    self.txt_telefoneFornecedor.repaint()
    self.txt_infoAdicionais.repaint()

    if hasattr(self, "id_fornecedor"):
        del self.id_fornecedor

    self.tableWidgetFornecedores.clearSelection()
    self.btn_salvarFornecedor.setText("Cadastrar Fornecedor ")
    self.btn_limparFornecedor.setText("Limpar Formulário")
    
    self.txt_cpfCnpj.blockSignals(False)
    self.tableWidgetFornecedores.blockSignals(False)

def pesquisar_fornecedor(self):
    """Método ponte exigido pelo arquivo menu.py para chamar a filtragem de dados"""
    pesquisa(self)
