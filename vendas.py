from PyQt5 import QtWidgets
from datetime import date
from conexao import conectar

# ---------------- INICIALIZAR VENDAS ----------------
def inicializar_vendas(self):
    """Prepara a tela de vendas ao iniciar o sistema"""
    self.tableVendas.setRowCount(0)
    atualizar_resumo_venda(self)

# ---------------- ADICIONAR PRODUTO (CARRINHO PDV) ----------------
def adicionar_produto_venda(self):
    """Busca o produto digitado e joga na tabela da venda"""
    pesquisa = self.txt_pedidoVendas.text().strip()
    if not pesquisa:
        return

    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Busca o produto pelo ID exato ou pelo Nome (Apenas produtos ativos)
        if pesquisa.isdigit():
            sql = "SELECT id_produto, nome, preco FROM produto WHERE id_produto = %s AND ativo = 1"
            cursor.execute(sql, (pesquisa,))
        else:
            sql = "SELECT id_produto, nome, preco FROM produto WHERE nome LIKE %s AND ativo = 1 LIMIT 1"
            cursor.execute(sql, (f"%{pesquisa}%",))
        
        produto = cursor.fetchone()
        
        if produto:
            id_prod = str(produto[0])
            nome = produto[1]
            preco = float(produto[2])
            
            # 1. Verifica se o produto já está na tabela
            linha_existente = -1
            for linha in range(self.tableVendas.rowCount()):
                if self.tableVendas.item(linha, 0).text() == id_prod:
                    linha_existente = linha
                    break
            
            if linha_existente >= 0:
                # Se já existe, apenas soma +1 na quantidade e atualiza o subtotal da linha
                qtd_atual = int(self.tableVendas.item(linha_existente, 2).text())
                nova_qtd = qtd_atual + 1
                novo_subtotal = nova_qtd * preco
                
                self.tableVendas.setItem(linha_existente, 2, QtWidgets.QTableWidgetItem(str(nova_qtd)))
                self.tableVendas.setItem(linha_existente, 4, QtWidgets.QTableWidgetItem(f"R$ {novo_subtotal:.2f}".replace('.', ',')))
            else:
                # Se não existe, adiciona uma nova linha
                linha_atual = self.tableVendas.rowCount()
                self.tableVendas.insertRow(linha_atual)
                
                self.tableVendas.setItem(linha_atual, 0, QtWidgets.QTableWidgetItem(id_prod))
                self.tableVendas.setItem(linha_atual, 1, QtWidgets.QTableWidgetItem(nome))
                self.tableVendas.setItem(linha_atual, 2, QtWidgets.QTableWidgetItem("1"))
                self.tableVendas.setItem(linha_atual, 3, QtWidgets.QTableWidgetItem(f"R$ {preco:.2f}".replace('.', ',')))
                self.tableVendas.setItem(linha_atual, 4, QtWidgets.QTableWidgetItem(f"R$ {preco:.2f}".replace('.', ',')))
                
                # Coloca a palavra "Remover" na coluna 5 (Ação)
                self.tableVendas.setItem(linha_atual, 5, QtWidgets.QTableWidgetItem("❌ Remover"))
            
            # Limpa a barra de pesquisa e atualiza a soma da lateral
            self.txt_pedidoVendas.setText("")
            atualizar_resumo_venda(self)
            
        else:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Produto não encontrado ou inativo!")
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao buscar produto: {e}")

# ---------------- ATUALIZAR RESUMO LATERAL ----------------
def atualizar_resumo_venda(self):
    """Soma todos os itens e aplica o desconto automaticamente"""
    subtotal = 0.0
    qtd_itens = 0
    
    # Soma a tabela inteira
    for linha in range(self.tableVendas.rowCount()):
        qtd = int(self.tableVendas.item(linha, 2).text())
        valor_str = self.tableVendas.item(linha, 4).text().replace("R$ ", "").replace(",", ".")
        subtotal += float(valor_str)
        qtd_itens += qtd

    # Pega o desconto digitado
    desconto_str = self.txt_descontoVenda.text().replace(",", ".")
    try:
        desconto = float(desconto_str) if desconto_str else 0.0
    except ValueError:
        desconto = 0.0

    # Aplica matemática final
    total = subtotal - desconto
    if total < 0: 
        total = 0.0

    # Atualiza as etiquetas na tela
    self.lblQtdItensResumo.setText(str(qtd_itens))
    self.lblValorSubtotal.setText(f"R$ {subtotal:.2f}".replace('.', ','))
    self.lblTotalVenda.setText(f"R$ {total:.2f}".replace('.', ','))

# ---------------- REMOVER ITEM DA TABELA ----------------
def remover_item_venda(self, row, column):
    """Se clicar na coluna 5 (Ação), exclui a linha"""
    if column == 5: 
        self.tableVendas.removeRow(row)
        atualizar_resumo_venda(self)

# ---------------- FINALIZAR VENDA (SALVAR NO BANCO) ----------------
def finalizar_venda(self):
    """Pega tudo que está na tela e envia pro banco de dados"""
    if self.tableVendas.rowCount() == 0:
        QtWidgets.QMessageBox.warning(self, "Aviso", "O carrinho está vazio!")
        return
        
    forma_pagamento = self.comboPagamento.currentText()
    total_str = self.lblTotalVenda.text().replace("R$ ", "").replace(",", ".")
    total = float(total_str)
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        hoje = date.today().strftime("%Y-%m-%d")
        
        # 1. Insere a Venda principal
        sql_venda = "INSERT INTO venda (data_venda, forma_pagamento, status_pagamento, total, valor_pago, valor_restante) VALUES (%s, %s, 'Pago', %s, %s, 0)"
        cursor.execute(sql_venda, (hoje, forma_pagamento, total, total))
        id_venda = cursor.lastrowid # Pega o ID da venda gerada
        
        # 2. Insere item a item
        sql_item = "INSERT INTO item_venda (id_venda, produto_nome, quantidade, preco, subtotal) VALUES (%s, %s, %s, %s, %s)"
        
        for linha in range(self.tableVendas.rowCount()):
            nome = self.tableVendas.item(linha, 1).text()
            qtd = int(self.tableVendas.item(linha, 2).text())
            preco = float(self.tableVendas.item(linha, 3).text().replace("R$ ", "").replace(",", "."))
            subtotal = float(self.tableVendas.item(linha, 4).text().replace("R$ ", "").replace(",", "."))
            
            cursor.execute(sql_item, (id_venda, nome, qtd, preco, subtotal))
            
        conexao.commit()
        QtWidgets.QMessageBox.information(self, "Sucesso", "Venda finalizada com sucesso!")
        
        # Reseta o sistema para o próximo cliente
        self.tableVendas.setRowCount(0)
        self.txt_descontoVenda.setText("0,00")
        atualizar_resumo_venda(self)
        self.txt_pedidoVendas.setFocus() # Devolve o cursor para o campo de pesquisa
        
    except Exception as e:
        conexao.rollback()
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao finalizar venda: {e}")