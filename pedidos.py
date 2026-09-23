from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QCompleter
from PyQt5.QtCore import QDate, Qt
from conexao import conectar

# ---------------- CARREGAR COMPONENTES E BUSCA CHROME ----------------
def inicializar_pedidos(self):
    """Configura os autocompletadores e datas na carga inicial da aba"""
    self.datePedido.setDate(QDate.currentDate())
    self.dateEntrega.setDate(QDate.currentDate())
    
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        # 1. Alimenta Clientes no ComboBox
        cursor.execute("SELECT id, nome FROM cliente ORDER BY nome")
        self.comboCliente.clear()
        self.comboCliente.addItem("Selecione o Cliente...", None)
        for cli in cursor.fetchall():
            self.comboCliente.addItem(cli[1], cli[0])
            
        # 2. Ativa Busca Estilo Chrome no campo Produto
        cursor.execute("SELECT DISTINCT nome FROM produto WHERE ativo = 1 ORDER BY nome")
        lista_prods = [str(p[0]) for p in cursor.fetchall()]
        
        completer = QCompleter(lista_prods, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.lineEdit_2.setCompleter(completer)
        
        # 🟢 GATILHOS CORRIGIDOS: Disparam a busca de atributos de forma precisa e sem travar
        self.lineEdit_2.editingFinished.connect(lambda: atualizar_variacoes_produto(self))
        self.comboTamanho.activated.connect(lambda: buscar_preco_grade(self))
        self.comboSabor.activated.connect(lambda: buscar_preco_grade(self))
        
        # Alinha as colunas do carrinho temporário
        self.tableItens.setColumnCount(6)
        self.tableItens.setHorizontalHeaderLabels(["Produto", "Sabor", "Tamanho", "Qtd", "Subtotal", "Ação"])
        self.tableItens.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.tableItens.horizontalHeader().setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        
        listar_pedidos(self)
    except Exception as e:
        print(f"Erro ao inicializar pedidos: {e}")

# ---------------- ATUALIZAR FILTROS DE SABOR/TAMANHO SELECIONADO ----------------
def atualizar_variacoes_produto(self):
    """Busca no banco apenas os sabores e tamanhos cadastrados para este produto específico"""
    produto_nome = self.lineEdit_2.text().strip()
    if not produto_nome: return

    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Busca variações válidas baseadas nos nomes exatos do seu dump SQL
        cursor.execute("""
            SELECT DISTINCT t.nome, s.nome 
            FROM produto_variacao pv
            INNER JOIN produto p ON pv.id_produto = p.id_produto
            LEFT JOIN tamanho t ON pv.id_tamanho = t.id_tamanho
            LEFT JOIN sabor s ON pv.id_sabor = s.id_sabor
            WHERE p.nome = %s AND pv.ativo = 1
        """, (produto_nome,))
        records = cursor.fetchall()
        
        # Isola os tamanhos e sabores cadastrados
        tamanhos = sorted(list(set([str(r[0]) for r in records if r[0]])))
        sabores = sorted(list(set([str(r[1]) for r in records if r[1]])))
        
        self.comboTamanho.clear()
        self.comboSabor.clear()
        
        if tamanhos: 
            self.comboTamanho.addItems(tamanhos)
        else: 
            self.comboTamanho.addItem("Padrão")
            
        if sabores: 
            self.comboSabor.addItems(sabores)
        else: 
            self.comboSabor.addItem("Tradicional")

        # Força a busca do preço inicial para a primeira combinação que apareceu
        buscar_preco_grade(self)

    except Exception as e:
        print(f"Erro ao filtrar atributos da grade: {e}")

# ---------------- ATUALIZAR PREÇO DO CARD EM TEMPO REAL ----------------
def buscar_preco_grade(self):
    """Busca o preço exato da combinação na tabela produto_variacao"""
    produto = self.lineEdit_2.text().strip()
    tamanho = self.comboTamanho.currentText().strip()
    sabor = self.comboSabor.currentText().strip()
    
    if not produto: return
    
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        sql = """
            SELECT pv.preco FROM produto_variacao pv
            INNER JOIN produto p ON pv.id_produto = p.id_produto
            LEFT JOIN tamanho t ON pv.id_tamanho = t.id_tamanho
            LEFT JOIN sabor s ON pv.id_sabor = s.id_sabor
            WHERE p.nome = %s AND (t.nome = %s OR t.nome IS NULL) AND (s.nome = %s OR s.nome IS NULL) AND pv.ativo = 1
            LIMIT 1
        """
        cursor.execute(sql, (produto, tamanho, sabor))
        res = cursor.fetchone()
        if res:
            self.lblPrecoProduto.setText(f"R$ {float(res[0]):.2f}".replace('.', ','))
        else:
            self.lblPrecoProduto.setText("R$ 0,00")
    except Exception as e:
        print(f"Erro ao buscar preço da variação: {e}")

# ---------------- ADICIONAR ITEM AO CARRINHO ----------------
def adicionar_carrinho(self):
    """Pega as seleções da tela e injeta uma linha no carrinho"""
    produto = self.lineEdit_2.text().strip()
    sabor = self.comboSabor.currentText()
    tamanho = self.comboTamanho.currentText()
    qtd_str = self.lineQuantidade.text().strip()
    
    # Remove o R$ e padroniza o ponto decimal para conversão numérica
    texto_preco = self.lblPrecoProduto.text()
    preco_str = texto_preco.replace("R$ ", "").replace(",", ".")

    if not produto or not qtd_str or preco_str == "0.00":
        QMessageBox.warning(
            self, "Aviso", 
            "Preencha a quantidade e garanta que o item possua preço cadastrado!"
        )
        return

    try:
        quantidade = int(qtd_str)
        preco_unitario = float(preco_str)
        subtotal = quantidade * preco_unitario

        linha = self.tableItens.rowCount()
        self.tableItens.insertRow(linha)

        # Insere os dados organizados coluna por coluna na tabela
        self.tableItens.setItem(linha, 0, QTableWidgetItem(produto))
        self.tableItens.setItem(linha, 1, QTableWidgetItem(sabor))
        self.tableItens.setItem(linha, 2, QTableWidgetItem(tamanho))
        self.tableItens.setItem(linha, 3, QTableWidgetItem(str(quantidade)))
        
        texto_subtotal = f"R$ {subtotal:.2f}".replace(".", ",")
        self.tableItens.setItem(linha, 4, QTableWidgetItem(texto_subtotal))

    except ValueError:
        QMessageBox.warning(self, "Aviso", "A quantidade digitada precisa ser um número inteiro!")
        

def remover_item_carrinho(self, linha_index):
    """Remove a linha específica do carrinho e recalcula os índices das lixeiras"""
    self.tableItens.removeRow(self.tableItens.currentRow())
    atualizar_total(self)
    
    # Reconecta as funções de clique para remapear os índices corretos após a exclusão
    for r in range(self.tableItens.rowCount()):
        btn = self.tableItens.cellWidget(r, 5)
        if btn:
            btn.clicked.disconnect()
            btn.clicked.connect(lambda _, current_r=r: remover_item_carrinho(self, current_r))

def atualizar_total(self):
    """Soma os valores de cada linha do carrinho e atualiza o rodapé"""
    total = 0.0
    for l in range(self.tableItens.rowCount()):
        total += float(self.tableItens.item(l, 4).text().replace("R$ ", "").replace(",", "."))
    self.lblTotal.setText(f"Total do pedido: R$ {total:.2f}".replace('.', ','))
# ---------------- FILA DA COZINHA (DIREITA) ----------------
def listar_pedidos(self):
    """Busca e preenche a tabela da cozinha trazendo APENAS os registros na fila 'Pendente'"""
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Cliente", "Data Pedido", "Entrega", "Total"])
        self.tableWidget.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        
        cursor.execute("""
            SELECT id_pedido, (SELECT nome FROM cliente WHERE id = id_cliente), data_pedido, data_entrega, total 
            FROM pedido WHERE status = 'Pendente' ORDER BY id_pedido DESC
        """)
        pedidos = cursor.fetchall()
        self.tableWidget.setRowCount(0)
        
        for idx, dados in enumerate(pedidos):
            self.tableWidget.insertRow(idx)
            self.tableWidget.setItem(idx, 0, QTableWidgetItem(str(dados[0])))
            self.tableWidget.setItem(idx, 1, QTableWidgetItem(str(dados[1]) if dados[1] else "Balcão"))
            self.tableWidget.setItem(idx, 2, QTableWidgetItem(dados[2].strftime('%d/%m/%Y') if dados[2] else ""))
            self.tableWidget.setItem(idx, 3, QTableWidgetItem(dados[3].strftime('%d/%m/%Y') if dados[3] else ""))
            self.tableWidget.setItem(idx, 4, QTableWidgetItem(f"R$ {dados[4]:.2f}".replace('.', ',')))
    except Exception as e:
        print(f"Erro ao listar fila da cozinha: {e}")

# ---------------- ENVIAR DO CARRINHO PARA A PRODUÇÃO ----------------
def gerar_pedido(self):
    """Salva o carrinho temporário como um pedido ativo pendente na produção"""
    if self.tableItens.rowCount() == 0:
        QMessageBox.warning(self, "Aviso", "O carrinho está vazio! Adicione doces primeiro.")
        return
    id_cliente = self.comboCliente.currentData()
    if not id_cliente:
        QMessageBox.warning(self, "Aviso", "Por favor, selecione um cliente da lista!")
        return
        
    dt_ped = self.datePedido.date().toString("yyyy-MM-dd")
    dt_ent = self.dateEntrega.date().toString("yyyy-MM-dd")
    tot = float(self.lblTotal.text().replace("Total do pedido: R$ ", "").replace(",", "."))
    
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        # Insere o pedido principal na fila da produção
        cursor.execute("INSERT INTO pedido (id_cliente, data_pedido, data_entrega, status, total) VALUES (%s, %s, %s, 'Pendente', %s)",
                       (id_cliente, dt_ped, dt_ent, tot))
        id_ped = cursor.lastrowid
        
        # Percorre o carrinho inserindo os itens associados
        for l in range(self.tableItens.rowCount()):
            prod = self.tableItens.item(l, 0).text()
            qtd = int(self.tableItens.item(l, 3).text())
            sub = float(self.tableItens.item(l, 4).text().replace("R$ ", "").replace(",", "."))
            
            cursor.execute("SELECT id_produto FROM produto WHERE nome = %s LIMIT 1", (prod,))
            id_p = cursor.fetchone()
            id_produto_real = id_p[0] if id_p else None
            
            cursor.execute("INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)",
                           (id_ped, id_produto_real, qtd, (sub/qtd), sub))
                           
        conexao.commit()
        QMessageBox.information(self, "Sucesso", "Pedido enviado com sucesso para a fila de Produção!")
        
        # Reseta os controles visuais
        self.tableItens.setRowCount(0)
        atualizar_total(self)
        self.comboCliente.setCurrentIndex(0)
        listar_pedidos(self)
    except Exception as e:
        conexao.rollback()
        QMessageBox.critical(self, "Erro", f"Erro ao salvar pedido na cozinha: {e}")

# ---------------- DESPACHAR DA COZINHA PARA O CAIXA DE VENDAS ----------------
def acao_botao_finalizar_pedido(self):
    """Despacha o doce finalizado da produção direto para a tela de vendas do Caixa"""
    linha = self.tableWidget.currentRow()
    if linha == -1:
        QMessageBox.warning(self, "Aviso", "Selecione o pedido finalizado na tabela da direita para despachar!")
        return
        
    id_pedido = self.tableWidget.item(linha, 0).text()
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        # Altera o status liberando a cobrança no PDV de vendas
        cursor.execute("UPDATE pedido SET status = 'Pronto para Cobrar' WHERE id_pedido = %s", (id_pedido,))
        conexao.commit()
        
        QMessageBox.information(self, "Sucesso", f"Pedido #{id_pedido} enviado com sucesso para o Caixa de Vendas!")
        listar_pedidos(self)
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao despachar pedido: {e}")
