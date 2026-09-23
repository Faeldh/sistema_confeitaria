from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate, Qt
from conexao import conectar

# =============================================================================
# 🎓 AULA 1: FORMATAÇÃO INPUT MASK E TRATAMENTO DE ERROS DINÂMICO
# O método setInputMask() trava os campos para aceitarem apenas caracteres válidos.
# O caractere "0" exige números, e o "_" é o marcador de espaço vazio.
# =============================================================================
def configurar_campos(self):
    """Aplica as máscaras profissionais de digitação e limpa os alertas vermelhos ao escrever"""
    # 🔍 MÁSCARAS DE ENTRADA: Pontuações automáticas de CPF, Celular e CEP
    self.txt_cpf.setInputMask("000.000.000-00;_")
    self.txt_telefone.setInputMask("(00) 00000-0000;_")
    self.txt_cep.setInputMask("00000-000;_")

    # 🔍 FEEDBACK VISUAL: O evento .textChanged limpa instantaneamente a borda 
    # vermelha de erro no exato momento em que o usuário começa a digitar no campo.
    self.txt_nome.textChanged.connect(lambda: self.txt_nome.setStyleSheet(""))
    self.txt_cpf.textChanged.connect(lambda: self.txt_cpf.setStyleSheet(""))
    self.txt_telefone.textChanged.connect(lambda: self.txt_telefone.setStyleSheet(""))


# =============================================================================
# 🎓 AULA 2: VALIDAÇÃO MATEMÁTICA DE COMPATIBILIDADE DE CPF
# Essa rotina realiza a multiplicação dos nove primeiros dígitos por pesos 
# regressivos para verificar se os dois dígitos finais (verificadores) são autênticos.
# =============================================================================
def validar_cpf(cpf):
    """Executa a verificação matemática oficial dos dígitos para rejeitar CPFs falsos"""
    if len(cpf) != 11 or cpf == cpf * 11:
        return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10
    return cpf[-2:] == f"{dig1}{dig2}"


# =============================================================================
# 🎓 AULA 3: OPERAÇÃO UNIFICADA DE GRAVAÇÃO (INSERT OU UPDATE)
# Esta função verifica dinamicamente a existência da propriedade 'id_cliente'. 
# Se ela existir, o sistema entende que é uma alteração (UPDATE); se não, realiza um novo registro (INSERT).
# =============================================================================
def salvar(self):
    """Salva um novo cliente ou atualiza as alterações se estiver no modo de edição"""
    nome = self.txt_nome.text().strip()
    
    # 🔍 DESMASCARADOR COMERCIAL: Remove parênteses e traços para salvar apenas os números limpos no banco
    telefone = self.txt_telefone.text().replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('_', '').strip()
    cpf = self.txt_cpf.text().replace('.', '').replace('-', '').replace('_', '').strip()
    cep = self.txt_cep.text().replace('-', '').replace('_', '').strip()
    
    data_format = self.dateEditNascimento.date().toString('yyyy-MM-dd')
    rua = self.txt_rua.text().strip()
    bairro = self.txt_bairro.text().strip()
    n = self.txt_n.text().strip()
    complemento = self.txt_complemento.text().strip()
    cidade = self.txt_cidade.text().strip()
    email = self.txt_email.text().strip()
    observcoes = self.txt_obs.toPlainText().strip()

    # Reseta os estilos visuais de erros anteriores
    self.txt_nome.setStyleSheet("")
    self.txt_telefone.setStyleSheet("")
    self.txt_cpf.setStyleSheet("")

    # Validação rigorosa de preenchimento obrigatório
    erros = []
    if not nome:
        erros.append("O nome do cliente é obrigatório!")
        self.txt_nome.setStyleSheet("border: 2px solid #DC2626;")
    if not telefone or len(telefone) < 10:
        erros.append("O telefone digitado está incompleto!")
        self.txt_telefone.setStyleSheet("border: 2px solid #DC2626;")
    if not cpf or len(cpf) < 11:
        erros.append("O CPF digitado está incompleto!")
        self.txt_cpf.setStyleSheet("border: 2px solid #DC2626;")
    elif not validar_cpf(cpf):
        QtWidgets.QMessageBox.warning(self, 'Erro', 'O CPF digitado é inválido!')
        self.txt_cpf.setStyleSheet("border: 2px solid #DC2626;")
        self.txt_cpf.setFocus()
        return

    if erros:
        QtWidgets.QMessageBox.warning(self, 'Campos Obrigatórios', '\n'.join(erros))
        return

    conexao = conectar()
    cursor = conexao.cursor()

    # --- MODO 1: ATUALIZAÇÃO (UPDATE) - CORRIGIDO SEM ERROS DE SQL ---
    if hasattr(self, 'id_cliente') and self.id_cliente:
        sql = """
            UPDATE cliente
            SET nome=%s, telefone=%s, cpf=%s, data_format=%s,
                cep=%s, rua=%s, bairro=%s, n=%s, complemento=%s, cidade=%s, email=%s, observcoes=%s
            WHERE id=%s
        """
        dados = (nome, telefone, cpf, data_format, cep, rua, bairro, n, complemento, cidade, email, observcoes, self.id_cliente)
        cursor.execute(sql, dados)
        conexao.commit()
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Ficha do cliente atualizada com sucesso!')
        atualizar(self)
        limpar(self)
        return


    # --- MODO 2: CADASTRO NOVO (INSERT) ---
    sql = 'INSERT INTO cliente(nome, telefone, data_format, cpf, cep, rua, bairro, n, complemento, cidade, email, observcoes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    dados = (nome, telefone, data_format, cpf, cep, rua, bairro, n, complemento, cidade, email, observcoes)
    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Cliente cadastrado com sucesso!')
        atualizar(self)
        limpar(self)


# =============================================================================
# 🎓 AULA 4: EXIBIÇÃO ORGANIZADA COM BOTÃO INTERNO MINIMALISTA (Efeito Clean)
# Para evitar o X vermelho bruto que era cortado, criamos um botão com o caractere "X" 
# em fonte fina e cor cinza discreta. O vermelho elegante só aparece no "Hover" (passar o mouse).
# O uso de setCellWidget() injeta esse botão perfeitamente centralizado em cada linha.
# =============================================================================
def atualizar(self):
    """Busca os registros no MySQL, aplica máscaras de exibição e renderiza a tabela com o X discreto"""
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT id, nome, cpf, telefone, email FROM cliente ORDER BY nome'
    cursor.execute(sql)
    resultado = cursor.fetchall()

    self.tableWidgetClientes.setRowCount(0)
    self.tableWidgetClientes.setColumnCount(6) # ID, Nome, CPF, Telefone, Email, Ação de Excluir
    self.tableWidgetClientes.setHorizontalHeaderLabels(["ID", "Nome", "CPF", "Telefone", "Email", ""])

    # 🔍 TRUQUE DESIGN: Remove divisórias verticais em pé e cria uma borda inferior fina cor oliva nas linhas
    self.tableWidgetClientes.setShowGrid(False)
    self.tableWidgetClientes.setStyleSheet(self.tableWidgetClientes.styleSheet() + "\nQTableWidget::item { border-bottom: 1px solid #3F4A2F; }")

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetClientes.insertRow(row_num)

        id_cli = str(row_data[0])
        nome_cli = str(row_data[1])
        cpf_cli = str(row_data[2])
        tel_cli = str(row_data[3])
        email_cli = str(row_data[4]) if row_data[4] else ""

        # Formata o CPF em tempo real antes de colocar na célula (000.000.000-00)
        cpf_formatado = f"{cpf_cli[:3]}.{cpf_cli[3:6]}.{cpf_cli[6:9]}-{cpf_cli[9:]}" if len(cpf_cli) == 11 else cpf_cli
        
        # Formata o Celular com 9 dígitos ou Fixo com 8 dígitos dinamicamente
        if len(tel_cli) == 11:
            tel_formatado = f"({tel_cli[:2]}) {tel_cli[2:7]}-{tel_cli[7:]}"
        elif len(tel_cli) == 10:
            tel_formatado = f"({tel_cli[:2]}) {tel_cli[2:6]}-{tel_cli[6:]}"
        else:
            tel_formatado = tel_cli

        # Instancia cada célula como um objeto de texto puro para podermos alinhar
        item_id = QtWidgets.QTableWidgetItem(id_cli)
        item_nome = QtWidgets.QTableWidgetItem(nome_cli)
        item_cpf = QtWidgets.QTableWidgetItem(cpf_formatado)
        item_tel = QtWidgets.QTableWidgetItem(tel_formatado)
        item_email = QtWidgets.QTableWidgetItem(email_cli)

        # 🔍 ALINHAMENTO CENTRO: Centraliza a escrita de todas as células de forma idêntica
        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)
        item_cpf.setTextAlignment(Qt.AlignCenter)
        item_tel.setTextAlignment(Qt.AlignCenter)
        item_email.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetClientes.setItem(row_num, 0, item_id)
        self.tableWidgetClientes.setItem(row_num, 1, item_nome)
        self.tableWidgetClientes.setItem(row_num, 2, item_cpf)
        self.tableWidgetClientes.setItem(row_num, 3, item_tel)
        self.tableWidgetClientes.setItem(row_num, 4, item_email)

        # 🔍 NOVO DESIGN DISCRETO DO "X": Substitui o emoji grosseiro por um texto fino e minimalista
        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #718096;          /* Cor cinza neutra padrão */
                font-size: 13px; 
                font-weight: bold; 
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover { 
                color: #E53E3E;          /* Fica vermelho moderno apenas se passar o mouse */
                font-size: 15px;         /* Leve efeito de zoom ao focar */
            }
        """)
        # Bloqueia o foco nativo do teclado (evita aquela linha azul ou tracejada feia ao clicar)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(
            lambda checked, id_c=id_cli, nome_c=nome_cli: deletar_pela_tabela(self, id_c, nome_c)
        )

        # Cria uma caixinha transparente para envelopar e centralizar o botão perfeitamente na célula
        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        
        self.tableWidgetClientes.setCellWidget(row_num, 5, container)

    # Configura os modos de redimensionamento automático de cada coluna da tabela
    header = self.tableWidgetClientes.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignCenter)
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch) 
    header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

    
# =============================================================================
# 🎓 AULA 5: DELETAR PELA TABELA E CONFIRMAÇÃO DE SEGURANÇA
# Um clique acidental poderia apagar dados valiosos. O QMessageBox.question 
# interrompe o código e cria uma janela de alerta exigindo a confirmação humana.
# =============================================================================
def deletar_pela_tabela(self, id_cliente, nome_cliente):
    """Abre um alerta de confirmação e deleta o cliente caso o usuário confirme"""
    confirmacao = QtWidgets.QMessageBox.question(
        self, 'Confirmar exclusão',
        f'Tem certeza que deseja permanentemente excluir o cliente "{nome_cliente}"?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )

    if confirmacao == QtWidgets.QMessageBox.No:
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM cliente WHERE id = %s", (id_cliente,))
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Cliente removido com sucesso!')
        limpar(self)
        atualizar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível excluir o registro do banco.')


# =============================================================================
# 🎓 AULA 6: CLÁUSULA "LIKE" PARA FILTRAGEM DINÂMICA (Pesquisa Rápida)
# A instrução SQL 'LIKE %termo%' varre o banco procurando correspondências em 
# qualquer pedaço do texto (início, meio ou fim). Também replica o novo X minimalista.
# =============================================================================
def pesquisa(self):
    """Varre as colunas nome ou CPF trazendo os resultados que batem com o texto digitado"""
    pesquisa_texto = self.txt_pesquisa.text().strip()

    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = 'SELECT id, nome, cpf, telefone, email FROM cliente WHERE nome LIKE %s OR cpf LIKE %s ORDER BY nome'
    like = f'%{pesquisa_texto}%'
    cursor.execute(sql, (like, like))
    resultado = cursor.fetchall()

    self.tableWidgetClientes.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetClientes.insertRow(row_num)
        
        id_cli = str(row_data[0])
        nome_cli = str(row_data[1])
        cpf_cli = str(row_data[2])
        tel_cli = str(row_data[3])
        email_cli = str(row_data[4]) if row_data[4] else ""

        cpf_formatado = f"{cpf_cli[:3]}.{cpf_cli[3:6]}.{cpf_cli[6:9]}-{cpf_cli[9:]}" if len(cpf_cli) == 11 else cpf_cli
        tel_formatado = f"({tel_cli[:2]}) {tel_cli[2:7]}-{tel_cli[7:]}" if len(tel_cli) == 11 else tel_cli

        item_id = QtWidgets.QTableWidgetItem(id_cli)
        item_nome = QtWidgets.QTableWidgetItem(nome_cli)
        item_cpf = QtWidgets.QTableWidgetItem(cpf_formatado)
        item_tel = QtWidgets.QTableWidgetItem(tel_formatado)
        item_email = QtWidgets.QTableWidgetItem(email_cli)

        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)
        item_cpf.setTextAlignment(Qt.AlignCenter)
        item_tel.setTextAlignment(Qt.AlignCenter)
        item_email.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetClientes.setItem(row_num, 0, item_id)
        self.tableWidgetClientes.setItem(row_num, 1, item_nome)
        self.tableWidgetClientes.setItem(row_num, 2, item_cpf)
        self.tableWidgetClientes.setItem(row_num, 3, item_tel)
        self.tableWidgetClientes.setItem(row_num, 4, item_email)

        # Garante o novo design do X minimalista cinza/vermelho também nos resultados da pesquisa
        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { background-color: transparent; color: #718096; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { color: #E53E3E; font-size: 15px; }
        """)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(lambda checked, id_c=id_cli, nome_c=nome_cli: deletar_pela_tabela(self, id_c, nome_c))

        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        self.tableWidgetClientes.setCellWidget(row_num, 5, container)


# =============================================================================
# 🎓 AULA 7: MODO SINAL DE EDIÇÃO ATIVO (Carregar por ID)
# Quando o usuário seleciona um cliente, esta função busca a linha completa e joga
# nos inputs. Ela armazena o id_cliente na janela, mudando o texto do botão para "Salvar Alterações".
# =============================================================================
def buscar_por_id(self, id_cliente):
    """Puxa a ficha cadastral completa do cliente selecionado no banco e preenche as caixas de texto"""
    conexao = conectar()
    cursor = conexao.cursor()

    sql = "SELECT nome, telefone, cpf, data_format, cep, rua, bairro, n, complemento, cidade, email, observcoes FROM cliente WHERE id = %s"
    cursor.execute(sql, (id_cliente,))
    resultado = cursor.fetchone()

    if resultado:
        self.txt_nome.setText(str(resultado[0]))
        self.txt_telefone.setText(str(resultado[1]))
        self.txt_cpf.setText(str(resultado[2]))

        # Converte o formato do banco (string 'AAAA-MM-DD') de volta para um objeto QDate nativo da tela
        data = resultado[3]
        if isinstance(data, str):
            self.dateEditNascimento.setDate(QDate.fromString(data, 'yyyy-MM-dd'))
        elif data:
            self.dateEditNascimento.setDate(QDate(data.year, data.month, data.day))

        self.txt_cep.setText(str(resultado[4]))
        self.txt_rua.setText(str(resultado[5]))
        self.txt_bairro.setText(str(resultado[6]))
        self.txt_n.setText(str(resultado[7]))
        self.txt_complemento.setText(str(resultado[8]))
        self.txt_cidade.setText(str(resultado[9]))
        self.txt_email.setText(str(resultado[10]))
        self.txt_obs.setPlainText(str(resultado[11]))

        # Salva o ID na memória da janela principal para travar o motor no modo UPDATE
        self.id_cliente = id_cliente
        self.btn_salvar.setText("Salvar Alterações")
        self.btn_limpar.setText("Limpar Formulário")


# =============================================================================
# 🎓 AULA 8: BLOQUEIO PROATIVO DE EVENTOS EM LOOP (.blockSignals)
# Quando mandamos limpar campos que possuem eventos vinculados (ex: .clear() dispara textChanged),
# os arquivos entram em loop e travam. blockSignals(True) desliga os alarmes da tela temporariamente,
# permitindo uma limpeza limpa, instantânea e segura, reativando os sinais no final.
# =============================================================================
def limpar(self):
    """Reseta de forma forçada e instantânea todos os inputs do formulário da esquerda"""
    self.tableWidgetClientes.blockSignals(True)
    
    # Limpa as caixas de digitação
    self.txt_nome.setText('')
    self.txt_telefone.setText('')
    self.dateEditNascimento.setDate(QDate.currentDate())
    self.txt_cpf.setText('')
    self.txt_cep.setText('')
    self.txt_rua.setText('')
    self.txt_bairro.setText('')
    self.txt_n.setText('')
    self.txt_complemento.setText('')
    self.txt_cidade.setText('')
    self.txt_email.setText('')
    self.txt_obs.clear()

    # Força o PyQt5 a redesenhar as caixas vazias na tela na mesma hora (.repaint)
    self.txt_nome.repaint()
    self.txt_telefone.repaint()
    self.txt_cpf.repaint()
    self.txt_obs.repaint()

    # Remove os estilos vermelhos de alertas antigos de erros
    self.txt_nome.setStyleSheet("")
    self.txt_telefone.setStyleSheet("")
    self.txt_cpf.setStyleSheet("")

    # Destrói a variável de ID de edição da memória para o formulário voltar a cadastrar novos clientes
    if hasattr(self, "id_cliente"):
        del self.id_cliente

    self.tableWidgetClientes.clearSelection()
    self.btn_salvar.setText("Cadastrar Cliente")
    self.btn_limpar.setText("Limpar Formulário")
    
    self.tableWidgetClientes.blockSignals(False)
