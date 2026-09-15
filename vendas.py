from PyQt5 import QtWidgets, QtCore
from datetime import date
from conexao import conectar

# ---------------- INICIALIZAR VENDAS ----------------
def inicializar_vendas(self):
    """Prepara a tela de vendas ao iniciar o sistema"""
    self.pedido_selecionado = None # Variável para guardar qual pedido está sendo pago
    carregar_pedidos_venda(self)
    resetar_resumo_venda(self)

# ---------------- CARREGAR PEDIDOS NA TABELA ----------------
def carregar_pedidos_venda(self):
    """Busca pedidos que ainda não foram pagos e joga na tabela"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Busca pedidos que não estão marcados como 'Pago'
        sql = '''
            SELECT 
                p.id_pedido, 
                c.id,
                c.nome, 
                p.data_entrega, 
                p.total, 
                p.status,
                (SELECT COALESCE(SUM(quantidade), 1) FROM item_pedido WHERE id_pedido = p.id_pedido) as qtd_itens
            FROM pedido p
            LEFT JOIN cliente c ON p.id_cliente = c.id
            WHERE p.status != 'Pago'
            ORDER BY p.data_entrega ASC
        '''
        cursor.execute(sql)
        pedidos = cursor.fetchall()
        
        self.tableVendas.setRowCount(0) # Limpa a tabela
        
        for linha, dados in enumerate(pedidos):
            self.tableVendas.insertRow(linha)
            
            id_pedido = dados[0]
            id_cliente = dados[1]
            nome_cliente = dados[2] if dados[2] else "Cliente Balcão"
            data_entrega = dados[3].strftime('%d/%m/%Y') if dados[3] else "--/--/----"
            total = float(dados[4]) if dados[4] else 0.0
            status = dados[5] if dados[5] else "PRONTO"
            qtd_itens = int(dados[6])
            
            # Formatando os textos das colunas para ficar igual ao seu design
            col_codigo = f"#{id_pedido}"
            col_produto = f"👤 {nome_cliente}   📅 Entrega: {data_entrega}"
            col_qtd = f"{qtd_itens} item(ns)"
            col_vlr_unit = f"R$ {total:.2f}".replace('.', ',')
            col_subtotal = str(status).upper() 
            
            # Preenchendo a tabela
            item_codigo = QtWidgets.QTableWidgetItem(col_codigo)
            
            # Escondemos os IDs do banco de dados na primeira coluna para usar na hora de salvar
            item_codigo.setData(QtCore.Qt.UserRole, id_pedido) 
            item_codigo.setData(QtCore.Qt.UserRole + 1, id_cliente) 
            
            self.tableVendas.setItem(linha, 0, item_codigo)
            self.tableVendas.setItem(linha, 1, QtWidgets.QTableWidgetItem(col_produto))
            self.tableVendas.setItem(linha, 2, QtWidgets.QTableWidgetItem(col_qtd))
            self.tableVendas.setItem(linha, 3, QtWidgets.QTableWidgetItem(col_vlr_unit))
            self.tableVendas.setItem(linha, 4, QtWidgets.QTableWidgetItem(col_subtotal))
            self.tableVendas.setItem(linha, 5, QtWidgets.QTableWidgetItem("💵 Cobrar"))
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao listar pedidos aguardando pagamento: {e}")

# ---------------- AÇÃO AO CLICAR EM "COBRAR" ----------------
def acao_tabela_vendas(self, row, column):
    """Disparado quando o usuário clica em alguma célula da tabela"""
    if column == 5: # Verifica se clicou na coluna "Ação"
        try:
            item_codigo = self.tableVendas.item(row, 0)
            if not item_codigo:
                return # Se a linha estiver vazia, não faz nada
                
            # Puxa os dados da linha clicada
            id_pedido = item_codigo.data(QtCore.Qt.UserRole)
            id_cliente = item_codigo.data(QtCore.Qt.UserRole + 1)
            
            nome_cliente = self.tableVendas.item(row, 1).text().split('📅')[0].replace('👤', '').strip()
            qtd_itens = int(self.tableVendas.item(row, 2).text().split()[0])
            total_str = self.tableVendas.item(row, 3).text().replace("R$ ", "").replace(",", ".")
            total = float(total_str)
            
            # Salva o pedido selecionado na memória da tela para usar depois
            self.pedido_selecionado = {
                'id_pedido': id_pedido,
                'id_cliente': id_cliente,
                'total': total
            }
            
            # Atualiza o quadro de "Resumo da Compra" na lateral direita
            self.txt_pedidoVendas.setText(f"Recebendo Pedido #{id_pedido} - {nome_cliente}")
            self.lblQtdItensResumo.setText(str(qtd_itens))
            self.lblValorSubtotal.setText(f"R$ {total:.2f}".replace('.', ','))
            
            # Calcula total com desconto se houver
            calcular_total_com_desconto(self)
            
        except Exception as e:
            # Se der algum erro aqui, o sistema mostra esse aviso EM VEZ de fechar sozinho
            QtWidgets.QMessageBox.critical(self, "Erro Fatal", f"Ocorreu um erro ao ler a linha da tabela: {e}")

# ---------------- CÁLCULO DE DESCONTO ----------------
def calcular_total_com_desconto(self):
    """Calcula o desconto em cima do pedido selecionado em tempo real"""
    try:
        if getattr(self, 'pedido_selecionado', None) is None:
            return
            
        subtotal = self.pedido_selecionado['total']
        desconto_str = self.txt_descontoVenda.text().replace(",", ".")
        
        try:
            desconto = float(desconto_str) if desconto_str else 0.0
        except ValueError:
            desconto = 0.0
            
        total = subtotal - desconto
        if total < 0:
            total = 0.0
            
        self.lblTotalVenda.setText(f"R$ {total:.2f}".replace('.', ','))
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro no desconto: {e}")

# ---------------- RESETAR RESUMO ----------------
def resetar_resumo_venda(self):
    """Limpa a lateral direita após uma venda"""
    self.pedido_selecionado = None
    self.txt_pedidoVendas.setText("")
    self.lblQtdItensResumo.setText("0")
    self.lblValorSubtotal.setText("R$ 0,00")
    self.txt_descontoVenda.setText("0,00")
    self.lblTotalVenda.setText("R$ 0,00")

# ---------------- FINALIZAR VENDA (SALVAR NO BANCO) ----------------
def finalizar_venda(self):
    """Muda o status do pedido para 'Pago' e gera o registro da Venda"""
    if getattr(self, 'pedido_selecionado', None) is None:
        QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um pedido clicando em '💵 Cobrar' na tabela!")
        return
        
    forma_pagamento = self.comboPagamento.currentText()
    total_str = self.lblTotalVenda.text().replace("R$ ", "").replace(",", ".")
    total_pago = float(total_str)
    
    id_pedido = self.pedido_selecionado['id_pedido']
    id_cliente = self.pedido_selecionado['id_cliente']
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        hoje = date.today().strftime("%Y-%m-%d")
        
        # 1. Registra a venda na tabela 'venda'
        sql_venda = "INSERT INTO venda (id_pedido, id_cliente, data_venda, forma_pagamento, status_pagamento, total, valor_pago, valor_restante) VALUES (%s, %s, %s, %s, 'Pago', %s, %s, 0)"
        cursor.execute(sql_venda, (id_pedido, id_cliente, hoje, forma_pagamento, self.pedido_selecionado['total'], total_pago))
        
        # 2. Atualiza o status do pedido para 'Pago' para que ele saia da tabela
        sql_update_pedido = "UPDATE pedido SET status = 'Pago' WHERE id_pedido = %s"
        cursor.execute(sql_update_pedido, (id_pedido,))
        
        conexao.commit()
        QtWidgets.QMessageBox.information(self, "Sucesso", "Pagamento registrado e venda finalizada!")
        
        resetar_resumo_venda(self)
        carregar_pedidos_venda(self) # Recarrega a tabela (o pedido pago vai sumir)
        
    except Exception as e:
        conexao.rollback()
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao finalizar venda: {e}")