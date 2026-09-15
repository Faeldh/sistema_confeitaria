import pymysql.cursors
from PyQt5 import QtWidgets, QtCore
from conexao import conectar  # Usa a sua conexão padrão do PyMySQL

class ModalUsuarios(QtWidgets.QDialog):
    def __init__(self, pai):
        super().__init__(pai)
        self.tela_principal = pai
        self.id_usuario_selecionado = None # Controla se é Novo (None) ou Edição (ID)
        
        self.setWindowTitle("Gerenciar Usuários")
        self.setFixedSize(760, 480)
        self.setModal(True) # Bloqueia a tela de trás
        
        # --- ESTILO VISUAL PADRONIZADO ---
        self.setStyleSheet("""
            QDialog { background-color: #FFFFFF; }
            QLabel { color: #2E3723; font-family: 'Segoe UI'; font-size: 12px; }
            QLineEdit, QComboBox { border: 2px solid #3F4A2F; border-radius: 8px; padding: 6px; background-color: white; }
            QPushButton#btnSalvar { background-color: #3F4A2F; color: #E6D2A2; border-radius: 8px; padding: 10px; font-weight: bold; }
            QPushButton#btnSalvar:hover { background-color: #2E3723; }
            QPushButton#btnLimpar { background-color: #E2E8F0; color: #4A5568; border: 2px solid #CBD5E0; border-radius: 8px; padding: 10px; font-weight: bold; }
            QPushButton#btnLimpar:hover { background-color: #CBD5E0; }
            QTableWidget { background-color: white; border: 2px solid #3F4A2F; border-radius: 10px; gridline-color: #E2E8F0; }
            QHeaderView::section { background-color: #3F4A2F; color: #E6D2A2; font-weight: bold; padding: 6px; border: none; }
        """)
        
        self.init_ui()
        self.listar_usuarios()

    def init_ui(self):
        layout_principal = QtWidgets.QHBoxLayout(self)
        layout_principal.setSpacing(25)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        # --- COLUNA ESQUERDA: FORMULÁRIO ---
        col_esquerda = QtWidgets.QVBoxLayout()
        col_esquerda.setSpacing(7)
        
        lbl_titulo_form = QtWidgets.QLabel("Salvar / Atualizar Dados")
        lbl_titulo_form.setStyleSheet("font-size: 15px; font-weight: bold; color: #3F4A2F; margin-bottom: 5px;")
        col_esquerda.addWidget(lbl_titulo_form)
        
        col_esquerda.addWidget(QtWidgets.QLabel("Nome Completo:"))
        self.txt_nome = QtWidgets.QLineEdit()
        self.txt_nome.setPlaceholderText("Digite o nome")
        col_esquerda.addWidget(self.txt_nome)
        
        col_esquerda.addWidget(QtWidgets.QLabel("Usuário de Acesso (Login):"))
        self.txt_login = QtWidgets.QLineEdit()
        self.txt_login.setPlaceholderText("Ex: admin ou atendente01")
        col_esquerda.addWidget(self.txt_login)
        
        col_esquerda.addWidget(QtWidgets.QLabel("Senha de Acesso:"))
        self.txt_senha = QtWidgets.QLineEdit()
        self.txt_senha.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_senha.setPlaceholderText("Digite uma senha segura")
        col_esquerda.addWidget(self.txt_senha)
        
        col_esquerda.addWidget(QtWidgets.QLabel("Nível de Acesso:"))
        self.cb_nivel = QtWidgets.QComboBox()
        self.cb_nivel.addItems(["Colaborador", "Proprietário", "Administrador"])
        col_esquerda.addWidget(self.cb_nivel)
        
        col_esquerda.addSpacing(10)
        
        # Layout Lado a Lado para os Botões
        layout_botoes = QtWidgets.QHBoxLayout()
        
        self.btn_salvar = QtWidgets.QPushButton("💾 Salvar Usuário")
        self.btn_salvar.setObjectName("btnSalvar")
        self.btn_salvar.clicked.connect(self.salvar_usuario)
        layout_botoes.addWidget(self.btn_salvar)
        
        self.btn_limpar = QtWidgets.QPushButton("🧹 Limpar / Novo")
        self.btn_limpar.setObjectName("btnLimpar")
        self.btn_limpar.clicked.connect(self.limpar_campos)
        layout_botoes.addWidget(self.btn_limpar)
        
        col_esquerda.addLayout(layout_botoes)
        col_esquerda.addStretch()
        
        # --- COLUNA DIREITA: TABELA ---
        col_direita = QtWidgets.QVBoxLayout()
        
        lbl_titulo_tab = QtWidgets.QLabel("Usuários Cadastrados")
        lbl_titulo_tab.setStyleSheet("font-size: 15px; font-weight: bold; color: #3F4A2F; margin-bottom: 5px;")
        col_direita.addWidget(lbl_titulo_tab)
        
        self.tabela = QtWidgets.QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome / Usuário", "Nível", "Ações"])
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.tabela.cellClicked.connect(self.selecionar_linha)
        
        header = self.tabela.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        
        col_direita.addWidget(self.tabela)
        
        layout_principal.addLayout(col_esquerda, stretch=2)
        layout_principal.addLayout(col_direita, stretch=3)
    def listar_usuarios(self):
        try:
            conexao = conectar()
            cursor = conexao.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT id_usuario, nome_completo, login, nivel_acesso FROM usuario")
            usuarios = cursor.fetchall()
            
            self.tabela.setRowCount(0)
            for row_num, dados in enumerate(usuarios):
                self.tabela.insertRow(row_num)
                self.tabela.setItem(row_num, 0, QtWidgets.QTableWidgetItem(str(dados['id_usuario'])))
                
                texto_celula = f"{dados['nome_completo']}\n{dados['login']}"
                self.tabela.setItem(row_num, 1, QtWidgets.QTableWidgetItem(texto_celula))
                self.tabela.setItem(row_num, 2, QtWidgets.QTableWidgetItem(str(dados['nivel_acesso'])))
                
                btn_excluir = QtWidgets.QPushButton("Excluir")
                btn_excluir.setStyleSheet("color: red; background: transparent; font-weight: bold; border: none; cursor: pointer;")
                btn_excluir.clicked.connect(lambda ch, id_u=dados['id_usuario']: self.excluir_usuario(id_u))
                self.tabela.setCellWidget(row_num, 3, btn_excluir)
                
            cursor.close()
            conexao.close()
        except Exception as e:
            print("Erro ao listar:", e)

    def salvar_usuario(self):
        nome = self.txt_nome.text().strip()
        login = self.txt_login.text().strip()
        senha = self.txt_senha.text().strip()
        nivel = self.cb_nivel.currentText()
        
        if not nome or not login:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Nome Completo e Usuário são obrigatórios!")
            return
            
        try:
            conexao = conectar()
            cursor = conexao.cursor()
            
            if self.id_usuario_selecionado is None:
                if not senha:
                    QtWidgets.QMessageBox.warning(self, "Aviso", "A senha é obrigatória para novos usuários!")
                    return
                sql = "INSERT INTO usuario (nome_completo, login, senha, nivel_acesso) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nome, login, senha, nivel))
            else:
                if senha:
                    sql = "UPDATE usuario SET nome_completo=%s, login=%s, senha=%s, nivel_acesso=%s WHERE id_usuario=%s"
                    cursor.execute(sql, (nome, login, senha, nivel, self.id_usuario_selecionado))
                else:
                    sql = "UPDATE usuario SET nome_completo=%s, login=%s, nivel_acesso=%s WHERE id_usuario=%s"
                    cursor.execute(sql, (nome, login, nivel, self.id_usuario_selecionado))
            
            conexao.commit()
            cursor.close()
            conexao.close()
            
            QtWidgets.QMessageBox.information(self, "Sucesso", "Usuário processado com sucesso!")
            self.limpar_campos()
            self.listar_usuarios()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Erro", f"Falha ao salvar: {str(e)}")

    def selecionar_linha(self, row, col):
        if col == 3: return
        try:
            item_id = self.tabela.item(row, 0)
            if not item_id: return
            
            id_u = int(item_id.text())
            self.id_usuario_selecionado = id_u
            
            conexao = conectar()
            cursor = conexao.cursor(pymysql.cursors.DictCursor)
            cursor.execute("SELECT * FROM usuario WHERE id_usuario = %s", (id_u,))
            user = cursor.fetchone()
            
            if user:
                self.txt_nome.setText(str(user['nome_completo']))
                self.txt_login.setText(str(user['login']))
                self.txt_senha.setPlaceholderText("(Deixe em branco para manter)")
                self.txt_senha.setText("")
                self.cb_nivel.setCurrentText(str(user['nivel_acesso']))
                self.btn_salvar.setText("🔄 Atualizar Usuário")
            cursor.close()
            conexao.close()
        except Exception as e:
            print("Erro ao carregar dados:", e)

    def excluir_usuario(self, id_usuario):
        confirmacao = QtWidgets.QMessageBox.question(
            self, "Excluir", "Deseja realmente remover este usuário?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirmacao == QtWidgets.QMessageBox.Yes:
            try:
                conexao = conectar()
                cursor = conexao.cursor()
                cursor.execute("DELETE FROM usuario WHERE id_usuario = %s", (id_usuario,))
                conexao.commit()
                cursor.close()
                conexao.close()
                self.limpar_campos()
                self.listar_usuarios()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Erro", f"Não foi possível excluir: {str(e)}")

    def limpar_campos(self):
        self.txt_nome.clear()
        self.txt_login.clear()
        self.txt_senha.clear()
        self.txt_senha.setPlaceholderText("Digite uma senha segura")
        self.cb_nivel.setCurrentIndex(0)
        self.id_usuario_selecionado = None
        self.btn_salvar.setText("💾 Salvar Usuário")
