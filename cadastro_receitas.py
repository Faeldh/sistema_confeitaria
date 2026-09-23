from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from conexao import conectar

# =============================================================================
# 🎓 TRATAMENTO DE ERROS DINÂMICO
# =============================================================================
def configurar_campos(self):
    """Vincula limpadores de bordas vermelhas de erro ao digitar"""
    self.txt_nomeReceita.textChanged.connect(lambda: self.txt_nomeReceita.setStyleSheet(""))
    self.txt_ingredientes.textChanged.connect(lambda: self.txt_ingredientes.setStyleSheet(""))
    self.txt_modoPreparo.textChanged.connect(lambda: self.txt_modoPreparo.setStyleSheet(""))


# =============================================================================
# 🎓 OPERAÇÃO UNIFICADA DE GRAVAÇÃO (INSERT OU UPDATE)
# =============================================================================
def salvar(self):
    nome = self.txt_nomeReceita.text().strip()
    ingrediente = self.txt_ingredientes.toPlainText().strip()
    preparo = self.txt_modoPreparo.toPlainText().strip()

    self.txt_nomeReceita.setStyleSheet("")
    self.txt_ingredientes.setStyleSheet("")
    self.txt_modoPreparo.setStyleSheet("")

    erros = []
    if not nome:
        erros.append("Nome da receita é obrigatório")
        self.txt_nomeReceita.setStyleSheet("border: 2px solid #DC2626;")
    if not ingrediente:
        erros.append("Ingredientes são obrigatórios")
        self.txt_ingredientes.setStyleSheet("border: 2px solid #DC2626;")
    if not preparo:
        erros.append("Modo de preparo é obrigatório")
        self.txt_modoPreparo.setStyleSheet("border: 2px solid #DC2626;")

    if erros:
        QtWidgets.QMessageBox.warning(self, 'Erro', '\n'.join(erros))
        return

    conexao = conectar()
    cursor = conexao.cursor()

    if hasattr(self, 'id_receita') and self.id_receita:
        sql = 'UPDATE receitas SET nome=%s, ingrediente=%s, preparo=%s WHERE id=%s'
        dados = (nome, ingrediente, preparo, self.id_receita)
        cursor.execute(sql, dados)
        conexao.commit()
        
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Receita atualizada com sucesso!')
        atualizar(self)
        limpar(self)
        return

    sql = 'INSERT INTO receitas(nome, ingrediente, preparo) VALUES (%s,%s,%s)'
    dados = (nome, ingrediente, preparo)
    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso!')
        atualizar(self)
        limpar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível cadastrar a receita.')
# =============================================================================
# 🎓 EXIBIÇÃO ORGANIZADA COM BOTÃO INTERNO MINIMALISTA (Efeito Clean)
# =============================================================================
def atualizar(self):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT id, nome FROM receitas ORDER BY nome'
    cursor.execute(sql)
    resultado = cursor.fetchall()

    self.tableWidgetReceitas.setRowCount(0)
    self.tableWidgetReceitas.setColumnCount(3)
    self.tableWidgetReceitas.setHorizontalHeaderLabels(["ID", "Nome", ""])

    self.tableWidgetReceitas.setShowGrid(False)
    self.tableWidgetReceitas.setStyleSheet(self.tableWidgetReceitas.styleSheet() + "\nQTableWidget::item { border-bottom: 1px solid #3F4A2F; }")

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetReceitas.insertRow(row_num)

        id_rec = str(row_data[0])
        nome_rec = str(row_data[1])

        item_id = QtWidgets.QTableWidgetItem(id_rec)
        item_nome = QtWidgets.QTableWidgetItem(nome_rec)

        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetReceitas.setItem(row_num, 0, item_id)
        self.tableWidgetReceitas.setItem(row_num, 1, item_nome)

        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #718096;
                font-size: 13px; 
                font-weight: bold; 
                border: none;
                padding: 0px;
                margin: 0px;
            }
            QPushButton:hover { 
                color: #E53E3E;
                font-size: 15px;
            }
        """)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(
            lambda checked, id_r=id_rec, nome_r=nome_rec: deletar_pela_tabela(self, id_r, nome_r)
        )

        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        
        self.tableWidgetReceitas.setCellWidget(row_num, 2, container)

    header = self.tableWidgetReceitas.horizontalHeader()
    header.setDefaultAlignment(Qt.AlignCenter)
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
    header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)


# =============================================================================
# 🎓 DELETAR PELA TABELA E CONFIRMAÇÃO DE SEGURANÇA
# =============================================================================
def deletar_pela_tabela(self, id_receita, nome_receita):
    confirmacao = QtWidgets.QMessageBox.question(
        self, 'Confirmar exclusão',
        f'Tem certeza que deseja permanentemente excluir a receita "{nome_receita}"?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )

    if confirmacao == QtWidgets.QMessageBox.No:
        return

    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM receitas WHERE id = %s", (id_receita,))
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Receita removida com sucesso!')
        limpar(self)
        atualizar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível excluir do banco.')


# =============================================================================
# 🎓 CLÁUSULA "LIKE" PARA FILTRAGEM DINÂMICA (Pesquisa Rápida)
# =============================================================================
def pesquisar(self):
    pesquisa_texto = self.txt_pesquisaReceita.text().strip()

    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = 'SELECT id, nome FROM receitas WHERE id LIKE %s OR nome LIKE %s ORDER BY nome'
    like = f'%{pesquisa_texto}%'
    cursor.execute(sql, (like, like))
    resultado = cursor.fetchall()

    self.tableWidgetReceitas.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetReceitas.insertRow(row_num)
        
        id_rec = str(row_data[0])
        nome_rec = str(row_data[1])

        item_id = QtWidgets.QTableWidgetItem(id_rec)
        item_nome = QtWidgets.QTableWidgetItem(nome_rec)

        item_id.setTextAlignment(Qt.AlignCenter)
        item_nome.setTextAlignment(Qt.AlignCenter)

        self.tableWidgetReceitas.setItem(row_num, 0, item_id)
        self.tableWidgetReceitas.setItem(row_num, 1, item_nome)

        btn_excluir_linha = QtWidgets.QPushButton("X")
        btn_excluir_linha.setStyleSheet("""
            QPushButton { background-color: transparent; color: #718096; font-size: 13px; font-weight: bold; border: none; }
            QPushButton:hover { color: #E53E3E; font-size: 15px; }
        """)
        btn_excluir_linha.setFocusPolicy(Qt.NoFocus)
        btn_excluir_linha.clicked.connect(lambda checked, id_r=id_rec, nome_r=nome_rec: deletar_pela_tabela(self, id_r, nome_r))

        container = QtWidgets.QWidget()
        container.setStyleSheet("background-color: transparent; border: none;")
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(btn_excluir_linha)
        layout.addStretch()
        container.setLayout(layout)
        self.tableWidgetReceitas.setCellWidget(row_num, 2, container)


# =============================================================================
# 🎓 MODO SINAL DE EDIÇÃO ATIVO (Carregar por ID)
# Quando clica em uma cadastrada, muda o texto para "Salvar Alterações"
# =============================================================================
def buscar_por_id(self, id_receita):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT nome, ingrediente, preparo FROM receitas WHERE id = %s'
    cursor.execute(sql, (id_receita,))
    resultado = cursor.fetchone()

    if resultado:
        self.txt_nomeReceita.setText(str(resultado[0]))
        self.txt_ingredientes.setPlainText(str(resultado[1]) if resultado[1] else "")
        self.txt_modoPreparo.setPlainText(str(resultado[2]) if resultado[2] else "")

        # Guarda o estado na janela para o motor usar UPDATE ao salvar
        self.id_receita = id_receita
        
        # MUTAÇÃO VISUAL DO BOTÃO PRINCIPAL:
        self.btn_salvarReceitas.setText("Salvar Alterações")
        self.btn_limparReceita.setText("Limpar Formulário")


# =============================================================================
# 🎓 BLOQUEIO PROATIVO DE EVENTOS EM LOOP (.blockSignals)
# Quando limpa o formulário, o botão principal volta para "Cadastrar Receita"
# =============================================================================
def limpar(self):
    self.tableWidgetReceitas.blockSignals(True)
    
    self.txt_nomeReceita.setText('')
    self.txt_ingredientes.clear()
    self.txt_modoPreparo.clear()

    # Força redesenho limpo instantâneo dos componentes
    self.txt_nomeReceita.repaint()
    self.txt_ingredientes.repaint()
    self.txt_modoPreparo.repaint()

    self.txt_nomeReceita.setStyleSheet("")
    self.txt_ingredientes.setStyleSheet("")
    self.txt_modoPreparo.setStyleSheet("")

    if hasattr(self, "id_receita"):
        del self.id_receita

    self.tableWidgetReceitas.clearSelection()
    
    # RESET VISUAL DOS BOTÕES (Voltando ao estado inicial):
    self.btn_salvarReceitas.setText("Cadastrar Receita")  # <-- CORRIGIDO AQUI
    self.btn_limparReceita.setText("Limpar Formulário")
    
    self.tableWidgetReceitas.blockSignals(False)



# =============================================================================
# 🎓 ADAPTADORES DE COMPATIBILIDADE
# =============================================================================
def editar(self):
    salvar(self)

def deletar(self):
    if hasattr(self, "id_receita"):
        nome = self.txt_nomeReceita.text()
        deletar_pela_tabela(self, self.id_receita, nome)
    else:
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione uma receita para excluir')
