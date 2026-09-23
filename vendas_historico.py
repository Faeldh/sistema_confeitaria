from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from conexao import conectar

class HistoricoVendasWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📜 Relatório Detalhado de Vendas Concluídas")
        self.setMinimumSize(900, 600)
        self.resize(950, 650)
        
        # Estilo visual moderno baseado na identidade da Mira Confeitaria
        self.setStyleSheet("""
            QDialog {
                background-color: #F8FAFC;
            }
            QLabel {
                color: #3F4A2F;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #3F4A2F;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 13px;
                color: #1E293B;
            }
            QLineEdit:focus {
                border: 2px solid #E6D2A2;
                background-color: #FDFDFD;
            }
            QTreeWidget {
                background-color: white;
                border: 2px solid #3F4A2F;
                border-radius: 10px;
                alternate-background-color: #F8FAFC;
                selection-background-color: #3F4A2F;
                selection-color: #E6D2A2;
            }
            QTreeWidget::item {
                padding: 10px;
                color: #1E293B;
            }
            QTreeWidget::item:hover {
                background-color: #F1F5F9;
            }
            QHeaderView::section {
                background-color: #3F4A2F;
                color: #E6D2A2;
                padding: 8px;
                font-weight: bold;
                border: none;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3F4A2F;
                color: #E6D2A2;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2E3723;
            }
        """)
        
        self.inicializar_interface()
        self.carregar_relatorio_detalhado()

    def inicializar_interface(self):
        layout_principal = QtWidgets.QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(15)
        
        # Cabeçalho explicativo
        lbl_titulo = QtWidgets.QLabel("Relatório de Vendas (Clique nas linhas para expandir os produtos)")
        lbl_titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #3F4A2F;")
        layout_principal.addWidget(lbl_titulo)
        
        # 🟢 NOVA BARRA DE PESQUISA INTELIGENTE: Criada diretamente via código
        self.input_pesquisa = QtWidgets.QLineEdit()
        self.input_pesquisa.setPlaceholderText("🔍 Digite o nome do cliente ou o número do pedido para filtrar na hora...")
        # Conecta o evento 'textChanged': conforme você digita qualquer letra, o filtro roda em tempo real!
        self.input_pesquisa.textChanged.connect(self.filtrar_pesquisa_historico)
        layout_principal.addWidget(self.input_pesquisa)
        
        # Árvore de Relatório (TreeWidget)
        self.tree_relatorio = QtWidgets.QTreeWidget()
        self.tree_relatorio.setColumnCount(5)
        self.tree_relatorio.setHeaderLabels([
            "Nº Pedido", "Cliente", "Data Venda", "Forma Pagamento", "Total Faturado"
        ])
        
        self.tree_relatorio.setAlternatingRowColors(True)
        layout_principal.addWidget(self.tree_relatorio)
        
        # Rodapé com botão Fechar
        layout_rodape = QtWidgets.QHBoxLayout()
        layout_rodape.addStretch()
        
        btn_fechar = QtWidgets.QPushButton("Fechar Relatório")
        btn_fechar.clicked.connect(self.close)
        layout_rodape.addWidget(btn_fechar)
        
        layout_principal.addLayout(layout_rodape)


    def carregar_relatorio_detalhado(self):
        """Busca as vendas e cria sub-itens expansíveis trazendo o Nº do Pedido na primeira coluna"""
        conexao = conectar()
        cursor = conexao.cursor()
        
        try:
            # 1. Busca as vendas realizadas
            sql_vendas = """
                SELECT 
                    v.id_venda, 
                    v.id_pedido, 
                    COALESCE(c.nome, 'Cliente Balcão'), 
                    v.data_venda, 
                    v.forma_pagamento, 
                    v.valor_pago,
                    COALESCE(p.observacao, '')
                FROM venda v
                LEFT JOIN cliente c ON v.id_cliente = c.id
                LEFT JOIN pedido p ON v.id_pedido = p.id_pedido
                ORDER BY v.id_venda DESC
            """
            cursor.execute(sql_vendas)
            vendas = cursor.fetchall()
            
            # 2. Busca os itens detalhados de todos os pedidos
            sql_produtos = """
                SELECT ip.id_pedido, prod.nome, ip.quantidade, ip.preco_unitario, ip.subtotal
                FROM item_pedido ip
                INNER JOIN produto prod ON ip.id_produto = prod.id_produto
                ORDER BY ip.id_item ASC
            """
            cursor.execute(sql_produtos)
            todos_produtos = cursor.fetchall()
            
            # Agrupa os itens de venda por ID do pedido
            produtos_por_pedido = {}
            for id_ped, nome_prod, qtd, preco, sub in todos_produtos:
                if id_ped not in produtos_por_pedido:
                    produtos_por_pedido[id_ped] = []
                produtos_por_pedido[id_ped].append([nome_prod, qtd, preco, sub])
                
            self.tree_relatorio.clear()
            
                        # 3. Monta a árvore na tela jogando o Nº do Pedido na Coluna 0
            for v in vendas:
                id_venda_real = v[0]
                id_pedido_real = v[1]
                cliente = str(v[2])
                data_venda = v[3].strftime('%d/%m/%Y') if v[3] else "--/--/----"
                forma_pagto = str(v[4])
                valor_efetivamente_pago = float(v[5]) # Valor final em dinheiro que o cliente pagou
                total_pago_txt = f"R$ {valor_efetivamente_pago:.2f}".replace('.', ',')
                obs_pedido = v[6].strip()
                
                # Busca o total bruto gravado na tabela venda e o desconto dado
                # Nota: Se o seu banco salva o subtotal original na coluna 'total' de venda, lemos ele aqui
                subtotal_bruto_venda = float(v[5]) # Base inicial de checagem
                
                # Puxa o valor original que o pedido tinha antes de ir para o caixa
                cursor.execute("SELECT total FROM pedido WHERE id_pedido = %s", (id_pedido_real,))
                val_pedido_original = cursor.fetchone()
                total_original_pedido = float(val_pedido_original[0]) if val_pedido_original else valor_efetivamente_pago
                
                id_pedido_txt = f"Pedido #{id_pedido_real}"
                
                # Cria a linha pai (a venda principal organizada pelas 5 colunas limpas)
                item_pai = QtWidgets.QTreeWidgetItem(self.tree_relatorio)
                item_pai.setText(0, id_pedido_txt)   # Coluna 0: Nº Pedido
                item_pai.setText(1, cliente)        # Coluna 1: Cliente
                item_pai.setText(2, data_venda)      # Coluna 2: Data Venda
                item_pai.setText(3, forma_pagto)    # Coluna 3: Forma Pagamento
                item_pai.setText(4, total_pago_txt)  # Coluna 4: Total Faturado
                
                for col in range(5):
                    font = item_pai.font(col)
                    font.setBold(True)
                    item_pai.setFont(col, font)
                    item_pai.setTextAlignment(col, Qt.AlignCenter)
                
                # 4. Injeta os produtos daquela venda como sub-linhas
                itens_da_venda = produtos_por_pedido.get(id_pedido_real, [])
                
                if itens_da_venda:
                    item_tit_produtos = QtWidgets.QTreeWidgetItem(item_pai)
                    item_tit_produtos.setText(0, "🛒 PRODUTOS COMPRADOS:")
                    item_tit_produtos.setText(1, "QTD:")
                    item_tit_produtos.setText(2, "VALOR UNIT:")
                    item_tit_produtos.setText(3, "SUBTOTAL:")
                    
                    for col in range(5):
                        font = item_tit_produtos.font(col)
                        font.setPointSize(10)
                        font.setItalic(True)
                        item_tit_produtos.setFont(col, font)
                        item_tit_produtos.setTextAlignment(col, Qt.AlignCenter)
                    
                    # 🟢 BALANÇA INTELIGENTE RECALIBRADA: O saldo de checagem começa com o valor pago. 
                    # Se o item couber dentro do que foi pago, ele entra ativo. Se o saldo acabar, ele entra cancelado!
                    saldo_restante_da_venda = valor_efetivamente_pago
                    
                    for nome_p, qtd, preco, subtotal_p in itens_da_venda:
                        item_filho = QtWidgets.QTreeWidgetItem(item_pai)
                        
                        # Margem de tolerância de centavos para não bugar com arredondamentos do MySQL
                        if saldo_restante_da_venda >= round(subtotal_p, 2) - 0.05:
                            item_filho.setText(0, f"  • {nome_p}")
                            saldo_restante_da_venda -= subtotal_p
                            cor_texto = QtCore.Qt.black
                            deve_riscar = False
                        else:
                            # 🟢 CORREÇÃO DEFINITIVA: Se o valor pago não cobre o produto, carimba como CANCELADO!
                            item_filho.setText(0, f"  • 🚫 (CANCELADO) - {nome_p}")
                            cor_texto = QtCore.Qt.gray
                            deve_riscar = True
                            
                        item_filho.setText(1, f"{qtd} un")
                        item_filho.setText(2, f"R$ {preco:.2f}".replace('.', ','))
                        item_filho.setText(3, f"R$ {subtotal_p:.2f}".replace('.', ','))
                        
                        for col in range(5):
                            item_filho.setTextAlignment(col, Qt.AlignCenter)
                            item_filho.setForeground(col, cor_texto)
                            
                            if deve_riscar:
                                font_filho = item_filho.font(col)
                                font_filho.setStrikeOut(True)
                                item_filho.setFont(col, font_filho)
                
                if obs_pedido:
                    item_obs = QtWidgets.QTreeWidgetItem(item_pai)
                    item_obs.setText(0, f"💡 Observação: {obs_pedido}")
                    item_obs.setFirstColumnSpanned(True)
                    
                    font = item_obs.font(0)
                    font.setItalic(True)
                    item_obs.setFont(0, font)
            
            # Dimensionamento proporcional perfeito das colunas
            header_tree = self.tree_relatorio.header()
            header_tree.setDefaultAlignment(Qt.AlignCenter)
            header_tree.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header_tree.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            header_tree.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            header_tree.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
            header_tree.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro no Relatório", f"Erro ao construir relatório sanfona: {e}")


    # 🟢 MOTOR DE FILTRO INSTANTÂNEO DA ARVORE: Mostra ou oculta as linhas em tempo real
    def filtrar_pesquisa_historico(self):
        """Varre as linhas pai da árvore e oculta as que não batem com o texto digitado"""
        texto_pesquisa = self.input_pesquisa.text().lower().strip()
        
        # Pega todas as linhas principais (vendas) da nossa árvore
        for i in range(self.tree_relatorio.topLevelItemCount()):
            item_venda = self.tree_relatorio.topLevelItem(i)
            
            # Captura o texto da coluna do Pedido e da coluna do Nome do Cliente
            texto_pedido = item_venda.text(0).lower()   # Ex: "pedido #29"
            texto_cliente = item_venda.text(1).lower()  # Ex: "jose"
            
            # Se a pesquisa estiver vazia OU se o texto bater com o cliente ou o número do pedido, exibe a linha
            if not texto_pesquisa or (texto_pesquisa in texto_pedido) or (texto_pesquisa in texto_cliente):
                item_venda.setHidden(False)
            else:
                # Caso contrário, oculta a linha da tela de forma invisível
                item_venda.setHidden(True)

