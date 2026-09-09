from PyQt5 import QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar

# ---------------- CARREGAR CLIENTES ----------------
def inicializar_pedidos(self):
    """Função para rodar ao abrir o sistema: preenche os clientes e ajusta as datas"""
    # Seta a data atual para os campos de data do pedido
    self.datePedido.setDate(QDate.currentDate())
    self.dateEntrega.setDate(QDate.currentDate())
    
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        # Busca ID e Nome do cliente
        cursor.execute("SELECT id, nome FROM cliente ORDER BY nome")
        clientes = cursor.fetchall()
        
        self.comboCliente.clear()
        self.comboCliente.addItem("Selecione o Cliente...", None)
        
        for cliente in clientes:
            # Adiciona o nome do cliente para aparecer, e salva o ID (cliente[0]) nos bastidores (userData)
            self.comboCliente.addItem(cliente[1], cliente[0])
            
    except Exception as e:
        print(f"Erro ao carregar clientes: {e}")
# ---------------- LISTAR PEDIDOS (TABELA DA DIREITA) ----------------
def listar_pedidos(self):
    """Busca os pedidos no banco e preenche a tabela de detalhes na direita"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Configura as colunas da tabela, já que elas não foram definidas no Qt Designer
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "Cliente", "Data Pedido", "Entrega", "Total", "Status"])
        
        # Ajusta o tamanho das colunas para o conteúdo caber melhor
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # ID
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)          # Cliente
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents) # Data Pedido
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents) # Entrega
        
        # Faz um JOIN entre pedido e cliente para pegar o nome do cliente em vez do ID
        sql = '''
            SELECT p.id_pedido, c.nome, p.data_pedido, p.data_entrega, p.total, p.status 
            FROM pedido p
            LEFT JOIN cliente c ON p.id_cliente = c.id
            ORDER BY p.id_pedido DESC
        '''
        cursor.execute(sql)
        lista_pedidos = cursor.fetchall()
        
        # Zera a tabela antes de preencher
        self.tableWidget.setRowCount(0)
        
        for linha, dados in enumerate(lista_pedidos):
            self.tableWidget.insertRow(linha)
            
            # Tratamento dos dados retornados do banco
            id_pedido = str(dados[0])
            cliente = str(dados[1]) if dados[1] else "Cliente não encontrado"
            
            # Formatação de datas (DD/MM/YYYY)
            data_ped = dados[2].strftime('%d/%m/%Y') if dados[2] else ""
            data_ent = dados[3].strftime('%d/%m/%Y') if dados[3] else ""
            
            # Formatação do Total
            total = f"R$ {dados[4]:.2f}".replace('.', ',') if dados[4] else "R$ 0,00"
            status = str(dados[5])
            
            # Preenche cada coluna
            self.tableWidget.setItem(linha, 0, QtWidgets.QTableWidgetItem(id_pedido))
            self.tableWidget.setItem(linha, 1, QtWidgets.QTableWidgetItem(cliente))
            self.tableWidget.setItem(linha, 2, QtWidgets.QTableWidgetItem(data_ped))
            self.tableWidget.setItem(linha, 3, QtWidgets.QTableWidgetItem(data_ent))
            self.tableWidget.setItem(linha, 4, QtWidgets.QTableWidgetItem(total))
            self.tableWidget.setItem(linha, 5, QtWidgets.QTableWidgetItem(status))
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Erro', f'Erro ao carregar lista de pedidos: {e}')

# ---------------- BUSCAR PRODUTO (LUPA) ----------------
def buscar_produto(self):
    """Busca o produto no banco de dados pelo nome digitado e atualiza o preço"""
    # lineEdit_2 é o campo onde o usuário digita o nome do produto na sua interface
    nome_pesquisa = self.lineEdit_2.text().strip()
    
    if not nome_pesquisa:
        QtWidgets.QMessageBox.warning(self, "Aviso", "Digite o nome do produto para pesquisar!")
        return
        
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Usamos LIKE %...% para que se você digitar "bolo", ele ache "Bolo de Chocolate", por exemplo.
        # Também filtramos apenas para produtos que estão ativos (ativo = 1)
        sql = "SELECT nome, preco, tamanho FROM produto WHERE nome LIKE %s AND ativo = 1 LIMIT 1"
        cursor.execute(sql, (f"%{nome_pesquisa}%",))
        resultado = cursor.fetchone()
        
        if resultado:
            nome_db = resultado[0]
            preco_db = resultado[1]
            tamanho_db = resultado[2]
            
            # 1. Preenche o campo de texto com o nome exato que está no banco de dados
            self.lineEdit_2.setText(nome_db)
            
            # 2. Atualiza a etiqueta verde com o preço do produto
            self.lblPrecoProduto.setText(f"R$ {preco_db:.2f}".replace('.', ','))
            
            # 3. Preenche a caixa de seleção de tamanho com o tamanho salvo no banco
            self.comboTamanho.clear()
            if tamanho_db:
                self.comboTamanho.addItem(tamanho_db)
            else:
                self.comboTamanho.addItem("Único")
                
        else:
            QtWidgets.QMessageBox.warning(self, "Aviso", f"Nenhum produto ativo encontrado com o nome '{nome_pesquisa}'.")
            self.lblPrecoProduto.setText("R$ 0,00")
            self.comboTamanho.clear()
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao buscar produto: {e}")


# ---------------- ADICIONAR AO CARRINHO ----------------
def adicionar_carrinho(self):
    """Pega os dados digitados e joga na tabela do carrinho"""
    produto = self.lineEdit_2.text() # Nome do produto
    sabor = self.comboSabor.currentText()
    tamanho = self.comboTamanho.currentText()
    qtd_str = self.lineQuantidade.text()
    
    if not produto or not qtd_str:
        QtWidgets.QMessageBox.warning(self, "Aviso", "Preencha o nome do Produto e a Quantidade!")
        return
        
    try:
        quantidade = int(qtd_str)
        
        conexao = conectar()
        cursor = conexao.cursor()
        
        # Busca o preço do produto no banco de dados para calcular corretamente
        cursor.execute("SELECT preco FROM produto WHERE nome = %s LIMIT 1", (produto,))
        resultado = cursor.fetchone()
        
        if resultado:
            preco_unitario = resultado[0]
        else:
            # Se não encontrar no banco, pede pro usuário digitar o preço manualmente (ou avisa erro)
            QtWidgets.QMessageBox.warning(self, "Aviso", f'Produto "{produto}" não encontrado no banco de dados!')
            return
            
        subtotal = quantidade * preco_unitario
        
        # Adiciona uma nova linha na tabela de itens
        linha_atual = self.tableItens.rowCount()
        self.tableItens.insertRow(linha_atual)
        
        # Preenche as colunas da tabela Itens
        self.tableItens.setItem(linha_atual, 0, QtWidgets.QTableWidgetItem(produto))
        self.tableItens.setItem(linha_atual, 1, QtWidgets.QTableWidgetItem(sabor))
        self.tableItens.setItem(linha_atual, 2, QtWidgets.QTableWidgetItem(tamanho))
        self.tableItens.setItem(linha_atual, 3, QtWidgets.QTableWidgetItem(str(quantidade)))
        # Formatando para dinheiro brasileiro
        self.tableItens.setItem(linha_atual, 4, QtWidgets.QTableWidgetItem(f"R$ {subtotal:.2f}".replace('.', ',')))
        
        atualizar_total(self)
        
        # Limpa os campos para o próximo item
        self.lineEdit_2.setText("")
        self.lineQuantidade.setText("")
        self.inputObs.setText("")
        
    except ValueError:
        QtWidgets.QMessageBox.warning(self, "Erro", "A quantidade deve ser um número inteiro!")
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao adicionar: {e}")


# ---------------- ATUALIZAR TOTAL ----------------
def atualizar_total(self):
    """Soma o subtotal de todas as linhas da tabela e atualiza o label de Total"""
    total = 0.0
    for linha in range(self.tableItens.rowCount()):
        # Pega o texto da coluna de preço, remove o 'R$ ' e troca vírgula por ponto para o Python conseguir somar
        valor_str = self.tableItens.item(linha, 4).text().replace("R$ ", "").replace(",", ".")
        total += float(valor_str)
        
    self.lblTotal.setText(f"Total do pedido: R$ {total:.2f}".replace('.', ','))


# ---------------- GERAR PEDIDO (SALVAR NO BANCO) ----------------
def gerar_pedido(self):
    """Salva o pedido principal e os itens vinculados a ele no banco de dados"""
    if self.tableItens.rowCount() == 0:
        QtWidgets.QMessageBox.warning(self, "Aviso", "O carrinho está vazio! Adicione produtos primeiro.")
        return
        
    # Extrai o ID do cliente escondido no ComboBox usando currentData()
    id_cliente = self.comboCliente.currentData()
    if not id_cliente:
        QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, selecione um cliente da lista!")
        return
        
    data_pedido = self.datePedido.date().toString("yyyy-MM-dd")
    data_entrega = self.dateEntrega.date().toString("yyyy-MM-dd")
    status = self.comboStatus_Pedido.currentText()
    observacao = "" # Se quiser adicionar um campo geral de obs no futuro
    
    # Extrai o valor final total do lblTotal
    total_str = self.lblTotal.text().replace("Total do pedido: R$ ", "").replace(",", ".")
    total = float(total_str)
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # 1. SALVAR NA TABELA `pedido`
        sql_pedido = "INSERT INTO pedido (id_cliente, data_pedido, data_entrega, status, observacao, total) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(sql_pedido, (id_cliente, data_pedido, data_entrega, status, observacao, total))
        
        # Pega o ID (número) do pedido que acabou de ser gerado no banco de dados
        id_pedido_gerado = cursor.lastrowid 
        
        # 2. SALVAR OS ITENS NA TABELA `item_pedido`
        sql_item = "INSERT INTO item_pedido (id_pedido, id_produto, quantidade, preco_unitario, subtotal) VALUES (%s, %s, %s, %s, %s)"
        
        for linha in range(self.tableItens.rowCount()):
            nome_produto = self.tableItens.item(linha, 0).text()
            qtd = int(self.tableItens.item(linha, 3).text())
            subtotal = float(self.tableItens.item(linha, 4).text().replace("R$ ", "").replace(",", "."))
            preco_unitario = subtotal / qtd
            
            # Buscar o ID do produto usando o nome, pois o banco de dados exige o ID
            cursor.execute("SELECT id_produto FROM produto WHERE nome = %s LIMIT 1", (nome_produto,))
            resultado_produto = cursor.fetchone()
            
            # Se não achar o ID (o que é raro se passou pela adição), salva como nulo para evitar travamento
            id_produto = resultado_produto[0] if resultado_produto else None
            
            cursor.execute(sql_item, (id_pedido_gerado, id_produto, qtd, preco_unitario, subtotal))
            
        conexao.commit()
        QtWidgets.QMessageBox.information(self, "Sucesso", "Pedido registrado com sucesso!")
        
        # Limpa o carrinho e reseta a tela
        self.tableItens.setRowCount(0)
        atualizar_total(self)
        self.comboCliente.setCurrentIndex(0)
        listar_pedidos(self)
        
    except Exception as e:
        conexao.rollback() # Cancela a operação se deu erro no meio do caminho
        QtWidgets.QMessageBox.warning(self, "Erro", f"Ocorreu um erro ao gerar o pedido:\n{e}")