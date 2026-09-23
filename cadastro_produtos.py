from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QCompleter, QPushButton, QHeaderView
from PyQt5.QtCore import Qt
from conexao import conectar

def gerenciar_botoes(self, modo_edicao=False):
    """Controla o texto dos botões dinamicamente entre Cadastro e Edição"""
    if not modo_edicao:
        self.btn_salvarProduto.setText("Cadastrar Produto")
        self.btn_limparProduto.setText("Limpar Formulário")
    else:
        self.btn_salvarProduto.setText("Atualizar Produto")
        self.btn_limparProduto.setText("Limpar Formulário")

def adicionar_sabor(self):
    """Pega o texto digitado e insere na listagem visual de sabores"""
    sabor = self.txt_novo_sabor.text().strip()
    if not sabor:
        QMessageBox.warning(self, 'Aviso', 'Digite um nome de sabor válido!')
        return
        
    itens_existentes = [self.list_sabores.item(i).text() for i in range(self.list_sabores.count())]
    if sabor in itens_existentes:
        QMessageBox.warning(self, 'Aviso', 'Este sabor já foi adicionado!')
        return
        
    self.list_sabores.addItem(sabor)
    self.txt_novo_sabor.clear()
    self.txt_novo_sabor.setFocus()

def adicionar_variacao(self):
    """Pega o tamanho (novo ou existente), valida o preço e insere na mini tabela de grade"""
    tamanho = ""
    
    if hasattr(self, 'comboTamanho'):
        widget_combo = self.comboTamanho
    else:
        QMessageBox.warning(self, 'Erro Técnico', 'O campo de seleção de tamanho não foi localizado na interface!')
        return

    # 🛡️ CAPTURA REFORÇADA: Tenta ler pelo lineEdit, se falhar, pega o texto atual do combo
    if widget_combo.lineEdit() and widget_combo.lineEdit().text().strip() != "":
        tamanho = widget_combo.lineEdit().text().strip()
    else:
        tamanho = widget_combo.currentText().strip()

    # Se mesmo assim o texto vier nulo ou o placeholder padrão do sistema, bloqueia
    if not tamanho or tamanho == "" or "Selecione ou digite" in tamanho:
        QMessageBox.warning(self, 'Aviso', 'Por favor, digite ou selecione um tamanho para a grade!')
        return

    # Validação do campo de preço
    if hasattr(self, 'txt_preco'):
        preco_texto = self.txt_preco.text().strip().replace(',', '.')
    else:
        QMessageBox.warning(self, 'Erro Técnico', 'O campo "txt_preco" não foi localizado na interface!')
        return
        
    try:
        preco = float(preco_texto)
        if preco <= 0: raise ValueError
    except ValueError:
        QMessageBox.warning(self, 'Aviso', 'Digite um preço numérico válido e maior que zero!')
        return

    # Evita duplicar o mesmo tamanho na mini tabela visível da grade
    linhas = self.tabela_tamanhos.rowCount()
    for row in range(linhas):
        if self.tabela_tamanhos.item(row, 0).text().lower() == tamanho.lower():
            QMessageBox.warning(self, 'Aviso', f"O tamanho '{tamanho}' já possui preço definido nesta grade!")
            return

    # =========================================================================
    # 🚀 BANCO DE DADOS: ADICIONA O TAMANHO SE ELE FOR INÉDITO
    # =========================================================================
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_tamanho FROM tamanho WHERE LOWER(nome) = LOWER(%s)", (tamanho,))
        res_tam = cursor.fetchone()
        
        if not res_tam:
            # Se digitou algo novo (ex: "XG", "2kg"), guarda imediatamente na tabela correta
            cursor.execute("INSERT INTO tamanho (nome) VALUES (%s)", (tamanho,))
            conexao.commit()
            
            # Atualiza a lista flutuante estilo chrome para já incluir o novo termo
            configurar_busca_chrome(self)
    except Exception as e:
        print(f"Erro ao verificar/salvar tamanho: {e}")
    finally:
        cursor.close()
        conexao.close()

    # Insere visualmente na tabela de tamanhos da esquerda
    self.tabela_tamanhos.insertRow(linhas)
    self.tabela_tamanhos.setItem(linhas, 0, QTableWidgetItem(tamanho))
    self.tabela_tamanhos.setItem(linhas, 1, QTableWidgetItem(f"{preco:.2f}"))
    
    # Reseta os campos para a próxima inserção
    self.txt_preco.clear()
    widget_combo.setCurrentIndex(-1)
    if widget_combo.lineEdit():
        widget_combo.lineEdit().setText("")


def limpar(self):
    """Reseta todos os campos do formulário esquerdo do produto"""
    self.txt_produto.clear()
    self.txt_descricao.clear()
    self.txt_novo_sabor.clear()
    self.list_sabores.clear()
    self.tabela_tamanhos.setRowCount(0)
    self.txt_preco.clear()
    self.combo_ativo.setCurrentIndex(0)
    self.tableViewProdutos.clearSelection()
    gerenciar_botoes(self, modo_edicao=False)
def salvar(self):
    """Grava ou atualiza o doce multiplicando os tamanhos e sabores no banco de dados"""
    nome_produto = self.txt_produto.text().strip()
    nome_categoria = self.combo_categoria.currentText().strip()
    descricao = self.txt_descricao.toPlainText().strip()
    ativo = 1 if self.combo_ativo.currentText() == "Sim" else 0

    if not nome_produto:
        QMessageBox.warning(self, 'Erro', 'O nome do produto é obrigatório!')
        return

    total_precos = self.tabela_tamanhos.rowCount()
    if total_precos == 0:
        QMessageBox.warning(self, 'Erro', 'Adicione pelo menos um tamanho e preço na tabela!')
        return

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id_categoria FROM categoria WHERE nome = %s", (nome_categoria,))
        res_cat = cursor.fetchone()
        id_categoria = res_cat[0] if res_cat else None
        if not id_categoria:
            cursor.execute("INSERT INTO categoria (nome) VALUES (%s)", (nome_categoria,))
            id_categoria = cursor.lastrowid

        linha_sel = self.tableViewProdutos.currentRow()
        if self.btn_salvarProduto.text() == "Atualizar Produto" and linha_sel != -1:
            id_produto = self.tableViewProdutos.item(linha_sel, 0).text()
            cursor.execute("UPDATE produto SET nome=%s, id_categoria=%s, descricao=%s, ativo=%s WHERE id_produto=%s",
                           (nome_produto, id_categoria, descricao, ativo, id_produto))
            cursor.execute("DELETE FROM produto_variacao WHERE id_produto = %s", (id_produto,))
            msg = 'Produto atualizado com sucesso!'
        else:
            cursor.execute("INSERT INTO produto (nome, id_categoria, descricao, ativo) VALUES (%s, %s, %s, %s)",
                           (nome_produto, id_categoria, descricao, ativo))
            id_produto = cursor.lastrowid
            msg = 'Produto cadastrado com sucesso!'

        sabores = [self.list_sabores.item(i).text() for i in range(self.list_sabores.count())]
        if not sabores: sabores = ["Tradicional"]

        ids_sabores = []
        for sab in sabores:
            cursor.execute("SELECT id_sabor FROM sabor WHERE nome = %s", (sab,))
            res_sab = cursor.fetchone()
            if res_sab: 
                ids_sabores.append(res_sab[0])
            else:
                cursor.execute("INSERT INTO sabor (nome) VALUES (%s)", (sab,))
                ids_sabores.append(cursor.lastrowid)

        for row in range(total_precos):
            nome_tam = self.tabela_tamanhos.item(row, 0).text()
            preco_venda = float(self.tabela_tamanhos.item(row, 1).text())

            cursor.execute("SELECT id_tamanho FROM tamanho WHERE nome = %s", (nome_tam,))
            res_tam = cursor.fetchone()
            id_tamanho = res_tam[0] if res_tam else None
            if not id_tamanho:
                cursor.execute("INSERT INTO tamanho (nome) VALUES (%s)", (nome_tam,))
                id_tamanho = cursor.lastrowid

            for id_sabor in ids_sabores:
                cursor.execute("""
                    INSERT INTO produto_variacao (id_produto, id_categoria, id_tamanho, id_sabor, preco, ativo)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (id_produto, id_categoria, id_tamanho, id_sabor, preco_venda, ativo))

        conexao.commit()
        QMessageBox.information(self, 'Sucesso', msg)
        listar(self)
        limpar(self)
        configurar_busca_chrome(self)
    except Exception as e:
        conexao.rollback()
        QMessageBox.critical(self, 'Erro', f'Erro ao salvar: {e}')
def listar(self):
    """Busca os produtos agregando as variações antigas e novas com preços em formato nacional"""
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        sql = """
            SELECT 
                p.id_produto, 
                p.nome, 
                c.nome as categoria, 
                COALESCE(GROUP_CONCAT(DISTINCT t.nome SEPARATOR ' / '), p.tamanho, 'Padrão') as tamanhos,
                MIN(pv.preco) as preco_min,
                COALESCE(GROUP_CONCAT(DISTINCT s.nome SEPARATOR ', '), 'Tradicional') as sabores,
                p.ativo,
                p.preco as preco_antigo
            FROM produto p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
            LEFT JOIN produto_variacao pv ON p.id_produto = pv.id_produto
            LEFT JOIN tamanho t ON pv.id_tamanho = t.id_tamanho
            LEFT JOIN sabor s ON pv.id_sabor = s.id_sabor
            GROUP BY p.id_produto ORDER BY p.id_produto DESC
        """
        cursor.execute(sql)
        produtos = cursor.fetchall()
        
        self.tableViewProdutos.setColumnCount(8)
        self.tableViewProdutos.setHorizontalHeaderLabels(["ID", "Produto", "Categoria", "Tamanho", "Preço", "Sabores", "Status", "Ação"])
        self.tableViewProdutos.setRowCount(0)
        
        # 🟢 Mantém o preenchimento das linhas exatamente como estava funcionando!
        for linha, dados in enumerate(produtos):
            self.tableViewProdutos.insertRow(linha)
            id_prod = str(dados[0])
            
            if dados[4] is not None:
                preco_val = f"A partir de R$ {dados[4]:.2f}".replace('.', ',')
            elif dados[7] is not None:
                preco_val = f"R$ {dados[7]:.2f}".replace('.', ',')
            else:
                preco_val = "Sob consulta"

            self.tableViewProdutos.setItem(linha, 0, QTableWidgetItem(id_prod))
            self.tableViewProdutos.setItem(linha, 1, QTableWidgetItem(str(dados[1])))
            self.tableViewProdutos.setItem(linha, 2, QTableWidgetItem(str(dados[2]) if dados[2] else "Geral"))
            self.tableViewProdutos.setItem(linha, 3, QTableWidgetItem(str(dados[3])))
            self.tableViewProdutos.setItem(linha, 4, QTableWidgetItem(preco_val))
            self.tableViewProdutos.setItem(linha, 5, QTableWidgetItem(str(dados[5])))
            self.tableViewProdutos.setItem(linha, 6, QTableWidgetItem("Sim" if dados[6] == 1 else "Não"))
            
            btn_excluir = QPushButton("x")
            btn_excluir.setStyleSheet("background-color:transparent; color:#7F8C8D; font-size:14px; border:none; padding:0px;")
            btn_excluir.clicked.connect(lambda _, id_p=id_prod, n_p=str(dados[1]): excluir_direto_tabela(self, id_p, n_p))
            self.tableViewProdutos.setCellWidget(linha, 7, btn_excluir)

        # =====================================================================
        # 🎨 NOVO: CORES DO APP E ALINHAMENTO DAS COLUNAS (FIM DA BAGUNÇA!)
        # =====================================================================
        self.tableViewProdutos.verticalHeader().setVisible(False)
        self.tableViewProdutos.setShowGrid(False)
        
        css_cabecalho_produtos = """
            QHeaderView::section { 
                background-color: #3F4A2F; 
                color: #E6D2A2; 
                padding: 6px; 
                font-weight: bold; 
                border: none;
                font-size: 13px;
            }
        """
        if hasattr(self, 'tableViewProdutos'):
            self.tableViewProdutos.horizontalHeader().setStyleSheet(css_cabecalho_produtos)

        header = self.tableViewProdutos.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents) # ID curto
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Doce estica tudo
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Categoria curta
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Tamanho curto
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Preço justo
        header.setSectionResizeMode(5, QHeaderView.Stretch)          # Sabores estica tudo
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # Status curto
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # Botão X curto

    except Exception as e:
        print(f"Erro ao listar: {e}")



def pegar_dados(self):
    """Ao clicar na tabela geral, reconstrói a ficha técnica completa"""
    linha = self.tableViewProdutos.currentRow()
    if linha == -1: return
    id_produto = self.tableViewProdutos.item(linha, 0).text()
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            SELECT p.nome, c.nome, p.descricao, p.ativo 
            FROM produto p LEFT JOIN categoria c ON p.id_categoria = c.id_categoria WHERE p.id_produto = %s
        """, (id_produto,))
        prod = cursor.fetchone()
        if prod:
            self.txt_produto.setText(str(prod[0]))
            self.combo_categoria.setCurrentText(str(prod[1]) if prod[1] else "")
            self.txt_descricao.setText(str(prod[2]) if prod[2] else "")
            self.combo_ativo.setCurrentText("Sim" if prod[3] == 1 else "Não")

            self.list_sabores.clear()
            self.tabela_tamanhos.setRowCount(0)

            cursor.execute("""
                SELECT DISTINCT s.nome FROM produto_variacao pv 
                INNER JOIN sabor s ON pv.id_sabor = s.id_sabor WHERE pv.id_produto = %s
            """, (id_produto,))
            for sab in cursor.fetchall(): self.list_sabores.addItem(sab[0])

            cursor.execute("""
                SELECT DISTINCT t.nome, pv.preco FROM produto_variacao pv
                INNER JOIN tamanho t ON pv.id_tamanho = t.id_tamanho WHERE pv.id_produto = %s
            """, (id_produto,))
            for idx, var in enumerate(cursor.fetchall()):
                self.tabela_tamanhos.insertRow(idx)
                self.tabela_tamanhos.setItem(idx, 0, QTableWidgetItem(str(var[0])))
                self.tabela_tamanhos.setItem(idx, 1, QTableWidgetItem(f"{var[1]:.2f}"))
            gerenciar_botoes(self, modo_edicao=True)
    except Exception as e:
        print(f"Erro ao pegar dados: {e}")

def excluir_direto_tabela(self, id_produto, nome_produto):
    """Deleta o doce do MySQL removendo também as variações órfãs"""
    if QMessageBox.question(self, 'Confirmar', f'Deseja excluir "{nome_produto}"?', QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
        conexao = conectar()
        cursor = conexao.cursor()
        try:
            cursor.execute("DELETE FROM produto_variacao WHERE id_produto = %s", (id_produto,))
            cursor.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
            conexao.commit()
            listar(self)
            limpar(self)
        except Exception as e:
            QMessageBox.critical(self, 'Erro', f'Erro ao deletar: {e}')

def configurar_busca_chrome(self):
    """Busca as categorias e tamanhos no banco e gera a pesquisa inteligente estilo Chrome"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # =====================================================================
        # 1. CONFIGURAÇÃO DA CATEGORIA
        # =====================================================================
        cursor.execute("SELECT nome FROM categoria ORDER BY nome")
        categorias = [str(cat[0]) for cat in cursor.fetchall() if cat and cat[0]]
        
        self.combo_categoria.clear()
        self.combo_categoria.addItems(categorias)
        self.combo_categoria.setEditable(True)
        self.combo_categoria.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        
        comp_cat = QCompleter(categorias, self)
        comp_cat.setCaseSensitivity(Qt.CaseInsensitive)
        comp_cat.setFilterMode(Qt.MatchContains)
        self.combo_categoria.setCompleter(comp_cat)

        # =====================================================================
        # 2. CONFIGURAÇÃO DO TAMANHO (CORRIGIDO E GARANTIDO)
        # =====================================================================
        if hasattr(self, 'comboTamanho'):
            campo_tam = self.comboTamanho
            
            # 🔥 O SEGREDO: Força o combo box a ser editável para aceitar novos tamanhos digitados
            campo_tam.setEditable(True)
            campo_tam.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
            campo_tam.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            campo_tam.setMinimumHeight(28)
            
            # Busca estritamente da tabela correta informada no phpMyAdmin
            cursor.execute("SELECT nome FROM tamanho ORDER BY nome")
            tamanhos = [str(tam[0]) for tam in cursor.fetchall() if tam and tam[0]]
            
            campo_tam.clear()
            campo_tam.addItems(tamanhos)
            
            # Recria o motor de busca inteligente do Chrome
            comp_tam = QCompleter(tamanhos, self)
            comp_tam.setCaseSensitivity(Qt.CaseInsensitive)
            comp_tam.setFilterMode(Qt.MatchContains)
            comp_tam.setCompletionMode(QCompleter.PopupCompletion)
            campo_tam.setCompleter(comp_tam)
            
            # Mantém inicialmente limpo para digitação livre
            campo_tam.setCurrentIndex(-1)
            if campo_tam.lineEdit():
                campo_tam.lineEdit().setText("")
                campo_tam.lineEdit().setPlaceholderText("Selecione ou digite o tamanho...")
                
    except Exception as e:
        print(f"Erro no Chrome Completer de Produtos: {e}")
    finally:
        cursor.close()
        conexao.close()




