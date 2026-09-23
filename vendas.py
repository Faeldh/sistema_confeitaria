from PyQt5 import QtWidgets, QtCore
from datetime import date
import webbrowser
import urllib.parse
import os
from conexao import conectar

# =============================================================================
# 🎓 INTERFACE FLUTUANTE DO COMPROVANTE (Ações reais de PDF e WhatsApp)
# =============================================================================
class JanelaOpcoesCupom(QtWidgets.QDialog):
    def __init__(self, parent, id_pedido, nome_cliente, telefone_cliente, total_venda, forma_pagamento, desconto, subtotal, itens_html):
        super().__init__(parent)
        self.parent_win = parent
        self.id_pedido = id_pedido
        self.nome_cliente = nome_cliente
        self.telefone_cliente = telefone_cliente
        self.total_venda = total_venda
        self.forma_pagamento = forma_pagamento
        self.desconto = desconto
        self.subtotal = subtotal
        self.itens_html = itens_html
        
        self.setWindowTitle("🎉 Venda Concluída com Sucesso!")
        self.setMinimumSize(450, 350)
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
        self.setStyleSheet("""
            QDialog { background-color: #F8FAFC; }
            QLabel { color: #3F4A2F; font-family: 'Segoe UI', Arial, sans-serif; }
            QPushButton { color: white; border-radius: 8px; padding: 14px; font-weight: bold; font-size: 13px; text-align: left; }
        """)
        
        self.inicializar_interface()

    def inicializar_interface(self):
        layout_principal = QtWidgets.QVBoxLayout(self)
        layout_principal.setContentsMargins(25, 25, 25, 25)
        layout_principal.setSpacing(15)
        
        lbl_sucesso = QtWidgets.QLabel("✨ Pagamento Confirmado!")
        lbl_sucesso.setStyleSheet("font-size: 20px; font-weight: bold; color: #15803D;")
        lbl_sucesso.setAlignment(QtCore.Qt.AlignCenter)
        layout_principal.addWidget(lbl_sucesso)
        
        lbl_sub = QtWidgets.QLabel(f"O que deseja fazer com o cupom do <b>Pedido #{self.id_pedido}</b>?")
        lbl_sub.setStyleSheet("font-size: 13px; color: #475569;")
        lbl_sub.setAlignment(QtCore.Qt.AlignCenter)
        layout_principal.addWidget(lbl_sub)
        
        self.btn_whats = QtWidgets.QPushButton("🟢  Enviar para o WhatsApp do Cliente")
        self.btn_whats.setStyleSheet("background-color: #25D366; color: white;")
        self.btn_whats.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_whats.clicked.connect(self.acao_enviar_whatsapp)
        layout_principal.addWidget(self.btn_whats)
        
        self.btn_pdf = QtWidgets.QPushButton("📄  Visualizar / Imprimir Recibo Completo")
        self.btn_pdf.setStyleSheet("background-color: #0284C7; color: white;")
        self.btn_pdf.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_pdf.clicked.connect(self.acao_visualizar_e_salvar_pdf)
        layout_principal.addWidget(self.btn_pdf)
        
        layout_principal.addSpacing(10)
        
        btn_fechar = QtWidgets.QPushButton("Concluir e Fechar")
        btn_fechar.setStyleSheet("background-color: #3F4A2F; color: #E6D2A2; text-align: center; font-size: 14px;")
        btn_fechar.setCursor(QtCore.Qt.PointingHandCursor)
        btn_fechar.clicked.connect(self.accept)
        layout_principal.addWidget(btn_fechar)
    def acao_enviar_whatsapp(self):
        """Monta o recibo em texto e abre o WhatsApp Web direto na conversa do cliente"""
        if not self.telefone_cliente or str(self.telefone_cliente).strip() == "":
            QtWidgets.QMessageBox.warning(self, "Aviso", "Este cliente não possui celular cadastrado no banco!")
            return
            
        fone_limpo = "".join([c for c in str(self.telefone_cliente) if c.isdigit()])
        if len(fone_limpo) == 11 and not fone_limpo.startswith("55"):
            fone_limpo = "55" + fone_limpo
            
        texto_mensagem = (
            f"Olá, *{self.nome_cliente}*! 🥰\n\n"
            f"Seu pagamento do *Pedido #{self.id_pedido}* foi confirmado! 🧾✨\n"
            f"Obrigado por comprar na *Mira Confeitaria*.\n\n"
            f"💰 *Valor Pago:* R$ {self.total_venda:.2f}\n"
            f"💳 *Forma de Pagamento:* {self.forma_pagamento}\n"
            f"📅 *Data de Emissão:* {date.today().strftime('%d/%m/%Y')}\n\n"
            f"Seus doces e bolos estão sendo preparados com muito carinho! ❤️🧁"
        ).replace('.', ',')
        
        texto_codificado = urllib.parse.quote(texto_mensagem)
        link_whatsapp = f"https://wa.me{fone_limpo}?text={texto_codificado}"
        webbrowser.open(link_whatsapp)

    def acao_visualizar_e_salvar_pdf(self):
        """Puxa os dados cadastrais da empresa e força a centralização idêntica a uma impressora térmica de caixa"""
        try:
            import base64
            pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            nome_arquivo = f"Recibo_Pedido_{self.id_pedido}.html"
            caminho_completo = os.path.join(pasta_downloads, nome_arquivo)
            
            conexao = conectar()
            cursor = conexao.cursor()
            cursor.execute("SELECT nome_empresa, cnpj, telefone, email, endereco, cidade FROM configuracao WHERE id_config = 1")
            conf = cursor.fetchone()
            
            if conf and isinstance(conf, (list, tuple)):
                empresa_nome = str(conf[0])
                empresa_cnpj = str(conf[1])
                empresa_tel = str(conf[2])
                empresa_end = str(conf[4])
            else:
                empresa_nome = "MIRA Confeitaria"
                empresa_cnpj = "00.000.000/0001-00"
                empresa_tel = "(31) 99876-5455"
                empresa_end = "Rua das Flores - Centro 111"
            
            logo_base64 = ""
            caminho_logo = os.path.abspath("imagens/logo_mira.png")
            if os.path.exists(caminho_logo):
                with open(caminho_logo, "rb") as image_file:
                    logo_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            if logo_base64:
                header_html = f'<img src="data:image/png;base64,{logo_base64}" width="75" style="display: block; margin: 0 auto 5px auto; border-radius: 50%;"><br><span class="titulo">{empresa_nome}</span>'
            else:
                header_html = f'<span class="titulo">{empresa_nome}</span>'
            
            # 🟢 Substitua a string tripla antiga do conteudo_html por esta versão com espaçamento flexível (Flexbox) no rodapé:
            conteudo_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Recibo Comercial #{self.id_pedido}</title>
                <style>
                    @page {{ size: auto; margin: 0mm; }}
                    @media print {{
                        body {{ background-color: #FFFFFF !important; padding: 0 !important; }}
                        .tabela-principal {{ width: 280px !important; min-height: 100vh !important; border: none !important; margin: 0 auto !important; padding: 0 !important; }}
                    }}
                    body {{ font-family: 'Arial', sans-serif; padding: 20px; background-color: #F1F5F9; margin: 0; }}
                    
                    /* 🟢 DESIGN FLEXBOX COM REFRESH: Transforma a tabela térmica em um container flexível de altura fixa */
                    .tabela-principal {{ 
                        background-color: #FFFFFF; 
                        width: 280px; 
                        min-height: 480px; /* Garante uma altura inicial elegante forçando o rodapé para baixo */
                        margin: 0 auto; 
                        border: 1px solid #000000; 
                        padding: 15px; 
                        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); 
                        border-radius: 6px;
                        display: flex;
                        flex-direction: column;
                        justify-content: space-between;
                    }}
                    .secao-conteudo {{ width: 100%; border-collapse: collapse; }}
                    .secao-rodape {{ width: 100%; border-collapse: collapse; margin-top: auto; padding-top: 15px; }}
                    
                    .centro {{ text-align: center !important; }}
                    .esquerda {{ text-align: left !important; }}
                    .direita {{ text-align: right !important; white-space: nowrap; }}
                    .negrito {{ font-weight: bold; }}
                    .titulo {{ font-size: 15px; font-weight: bold; text-transform: uppercase; color: #3F4A2F; margin-top: 3px; font-family: 'Arial Black', sans-serif; }}
                    .linha-info {{ font-size: 12px; height: 18px; text-align: left; }}
                    .divisor-tracejado {{ border-top: 1px dashed #000000; height: 4px; padding: 0; margin: 4px 0; }}
                    .divisor-duplo {{ border-top: 3px double #000000; height: 4px; padding: 0; margin: 4px 0; }}
                    .sub-item {{ font-size: 11px; color: #444444; font-style: italic; padding-top: 1px; text-align: left; }}
                </style>
            </head>
            <body>
                <center>
                    <div class="tabela-principal">
                        <!-- 🟢 BLOCO SUPERIOR: Dados da empresa e lista de produtos comprados -->
                        <table class="secao-conteudo">
                            <tr><td colspan="2" class="centro" style="padding-bottom: 5px;">{header_html}</td></tr>
                            <tr><td colspan="2" class="divisor-tracejado"></td></tr>
                            <tr class="linha-info"><td colspan="2" class="esquerda"><b>CNPJ:</b> {empresa_cnpj}</td></tr>
                            <tr class="linha-info"><td colspan="2" class="esquerda"><b>Contato:</b> {empresa_tel}</td></tr>
                            <tr class="linha-info"><td colspan="2" class="esquerda"><b>Endereço:</b> {empresa_end}</td></tr>
                            <tr><td colspan="2" class="divisor-tracejado"></td></tr>
                            <tr class="linha-info"><td colspan="2" class="esquerda"><b>Cliente:</b> {self.nome_cliente}</td></tr>
                            <tr class="linha-info"><td colspan="2" class="esquerda"><b>Venda (n: {self.id_pedido})</b></td></tr>
                            <tr><td colspan="2" class="divisor-duplo" style="height: 5px;"></td></tr>
                            <tr class="linha-info" style="font-weight: bold;"><td class="esquerda">Descrição / Qtd X Unitário</td><td class="direita">Total</td></tr>
                            <tr><td colspan="2" class="divisor-duplo"></td></tr>
                            {self.itens_html}
                        </table>
                        
                        <!-- 🟢 BLOCO INFERIOR (O SEU DESENHO): Empurrado automaticamente para o rodapé da nota -->
                        <table class="secao-rodape">
                            <tr class="linha-info"><td class="esquerda">Total Produtos</td><td class="direita negrito">R$ {self.subtotal:.2f}</td></tr>
                            <tr class="linha-info"><td class="esquerda">Desconto</td><td class="direita negrito" style="color: #C53030;">- R$ {self.desconto:.2f}</td></tr>
                            <tr class="linha-info"><td class="esquerda">Subtotal</td><td class="direita negrito">R$ {self.subtotal:.2f}</td></tr>
                            <tr><td colspan="2" class="divisor-tracejado"></td></tr>
                            <tr class="linha-info" style="font-size: 13px; font-weight: bold;"><td class="esquerda">Total a Pagar</td><td class="direita">R$ {self.total_venda:.2f}</td></tr>
                            <tr class="linha-info"><td class="esquerda">{self.forma_pagamento}</td><td class="direita negrito">R$ {self.total_venda:.2f}</td></tr>
                            <tr><td colspan="2" class="divisor-duplo"></td></tr>
                            <tr><td colspan="2" class="centro negrito" style="padding-top: 5px; font-size: 12px;">Volte sempre! ❤️</td></tr>
                        </table>
                    </div>
                </center>
                <script>window.print();</script>
            </body>
            </html>
            """.replace('.', ',')

            
            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write(conteudo_html)
            webbrowser.open(caminho_completo)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Erro", f"Não foi possível abrir o recibo: {e}")
# ---------------- INICIALIZAR VENDAS ----------------
def inicializar_vendas(self):
    """Prepara a tela de vendas ao iniciar o sistema amarrando a busca de forma blindada"""
    self.pedido_selecionado = None
    
    __import__('vendas').carregar_pedidos_venda(self)
    __import__('vendas').resetar_resumo_venda(self)
    
    # 🟢 CONEXÃO 1 (Clique na linha): cellClicked passa row e col de forma nativa e segura
    try:
        self.tableVendas.cellClicked.disconnect()
    except:
        pass
    self.tableVendas.cellClicked.connect(lambda row, col: __import__('vendas').acao_tabela_vendas(self, row, col))
    
    # 🟢 CONEXÃO 2 (Barra de Pesquisa Dinâmica): Isola o txt_pedidoVendas para evitar conflito de colisão!
    self.campo_pesquisa_vendas = None
    for nome_attr in ['lineEdit', 'lineEdit_pesquisa', 'txt_pesquisaVenda', 'txt_pesquisa_vendas']:
        if hasattr(self, nome_attr):
            self.campo_pesquisa_vendas = getattr(self, nome_attr)
            break
            
    if self.campo_pesquisa_vendas is not None:
        try:
            self.campo_pesquisa_vendas.textChanged.disconnect()
        except:
            pass
        self.campo_pesquisa_vendas.textChanged.connect(lambda: __import__('vendas').filtrar_pesquisa_vendas_pendentes(self))


# ---------------- CARREGAR PEDIDOS NA TABELA ----------------
def carregar_pedidos_venda(self):
    """Busca pedidos e renderiza mantendo as 6 colunas originais do Qt Designer intactas"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # SQL completo para trazer o faturamento e a soma física de doces
        sql = '''
            SELECT 
                p.id_pedido, 
                c.id,
                COALESCE(c.nome, 'Cliente Balcão') as nome_cliente, 
                p.data_entrega, 
                p.total, 
                p.status,
                COALESCE((SELECT SUM(quantidade) FROM item_pedido WHERE id_pedido = p.id_pedido), 0) as qtd_total_itens
            FROM pedido p
            LEFT JOIN cliente c ON p.id_cliente = c.id
            WHERE p.status = 'Pronto para Cobrar'
            ORDER BY p.id_pedido ASC
        '''
        cursor.execute(sql)
        pedidos = cursor.fetchall()
        
        self.tableVendas.setRowCount(0)
        self.tableVendas.setColumnCount(6)
        
        # 🟢 COR DAS DIVISÓRIAS SINCRONIZADA: Linha horizontal idêntica às outras tabelas do sistema
        self.tableVendas.setShowGrid(False)
        self.tableVendas.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #1E293B;
                border: 2px solid #3F4A2F;      /* Moldura externa Verde-Oliva */
                border-radius: 10px;            /* Cantos arredondados elegantes */
                gridline-color: transparent;
            }
            QTableWidget::item {
                border-bottom: 1px solid #D1D5DB; /* 🟢 AGORA SIM: Linha cinza padrão do resto do app! */
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #3F4A2F;       /* Realce verde-escuro ao selecionar */
                color: #E6D2A2;                  /* Letras douradas na seleção */
            }
            QHeaderView::section {
                background-color: #3F4A2F !important; /* Topo da planilha Verde-Oliva */
                color: #E6D2A2 !important;            /* Textos das colunas Dourados */
                font-weight: bold;
                padding: 6px;
                border: none;
            }
        """)
        
        self.tableVendas.verticalHeader().setVisible(False)

        header = self.tableVendas.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch) # Apenas o nome do cliente estica
        
        for linha, dados in enumerate(pedidos):
            self.tableVendas.insertRow(linha)
            
            id_pedido = int(dados[0])
            id_cliente = dados[1]
            nome_cliente = str(dados[2])
            data_entrega = dados[3].strftime('%d/%m/%Y') if dados[3] else "--/--/----"
            total_pedido = float(dados[4])
            status = str(dados[5]).upper()
            qtd_itens = int(dados[6])
            
            txt_codigo = f"#{id_pedido}"
            txt_cliente_data = f"👤 {nome_cliente}  |  Entrega: {data_entrega}"
            txt_qtd = f"{qtd_itens} item(ns)"
            txt_subtotal = f"R$ {total_pedido:.2f}".replace('.', ',')
            txt_status = f"{status}..."
            
            # Vincula metadados invisíveis de controle na primeira célula
            item_codigo = QtWidgets.QTableWidgetItem(txt_codigo)
            item_codigo.setData(QtCore.Qt.UserRole, id_pedido) 
            item_codigo.setData(QtCore.Qt.UserRole + 1, id_cliente) 
            item_codigo.setData(QtCore.Qt.UserRole + 2, nome_cliente)
            item_codigo.setData(QtCore.Qt.UserRole + 3, total_pedido)
            
            # Preenche as 6 colunas completas respeitando o grid original
            self.tableVendas.setItem(linha, 0, item_codigo)
            self.tableVendas.setItem(linha, 1, QtWidgets.QTableWidgetItem(txt_cliente_data))
            self.tableVendas.setItem(linha, 2, QtWidgets.QTableWidgetItem(txt_qtd)) 
            self.tableVendas.setItem(linha, 3, QtWidgets.QTableWidgetItem(txt_subtotal)) 
            self.tableVendas.setItem(linha, 4, QtWidgets.QTableWidgetItem(txt_status))
            self.tableVendas.setItem(linha, 5, QtWidgets.QTableWidgetItem("Cobrar"))
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao listar pedidos: {e}")


# ---------------- AÇÃO AO CLICAR EM QUALQUER LUGAR DA LINHA ----------------
def acao_tabela_vendas(self, row, column):
    """Disparado quando o usuário clica na linha. Exibe o resumo na label_5 sem quebrar a pesquisa"""
    try:
        item_codigo = self.tableVendas.item(row, 0)
        if not item_codigo:
            return
            
        id_pedido = item_codigo.data(QtCore.Qt.UserRole)
        id_cliente = item_codigo.data(QtCore.Qt.UserRole + 1)
        nome_cliente = item_codigo.data(QtCore.Qt.UserRole + 2)
        total_real_banco = item_codigo.data(QtCore.Qt.UserRole + 3)
        
        qtd_itens_txt = self.tableVendas.item(row, 2).text().split()[0]
        
        self.pedido_selecionado = {
            'id_pedido': id_pedido,
            'id_cliente': id_cliente,
            'total': total_real_banco
        }
        
        # 🟢 CORREÇÃO VISUAL: Atualiza a label_5 (o cabeçalho de texto verde) em vez do txt_pedidoVendas!
        self.label_5.setText(f"CLIENTE: {nome_cliente.upper()} | Recebendo Pedido #{id_pedido}\n 🛒 Itens da Compra")
        
        self.lblQtdItensResumo.setText(qtd_itens_txt)
        self.lblValorSubtotal.setText(f"R$ {total_real_banco:.2f}".replace('.', ','))
        
        if hasattr(self, 'listWidgetCupom') and self.listWidgetCupom is not None:
            self.listWidgetCupom.clear()
            self.listWidgetCupom.addItem("------ MIRA CONFEITARIA ------")
            self.listWidgetCupom.addItem(f"CUPOM PEDIDO #{id_pedido}")
            self.listWidgetCupom.addItem("------------------------------")
            __import__('vendas').imprimir_itens_no_cupom(self, id_pedido, row)
        
        __import__('vendas').calcular_total_com_desconto(self)
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(self, "Erro Fatal", f"Ocorreu um erro ao carregar os dados: {e}")


# ---------------- BUSCAR ITENS E IMPRIMIR NO CUPOM ----------------
def imprimir_itens_no_cupom(self, id_pedido, linha_tabela=None):
    """Busca os produtos do pedido atual no MySQL e injeta o texto limpo, sem ícones extras"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        sql = """
            SELECT p.nome, ip.quantidade, ip.preco_unitario, ip.subtotal
            FROM item_pedido ip
            INNER JOIN produto p ON ip.id_produto = p.id_produto
            WHERE ip.id_pedido = %s
        """
        cursor.execute(sql, (id_pedido,))
        itens = cursor.fetchall()
        
        try:
            self.listWidgetCupom.itemDoubleClicked.disconnect()
        except:
            pass
            
        self.listWidgetCupom.itemDoubleClicked.connect(lambda item: __import__('vendas').acao_cancelar_item_cupom(self, item))
        
        for item in itens:
            raw_nome = item[0]
            nome_prod = raw_nome.decode('utf-8') if isinstance(raw_nome, bytes) else str(raw_nome)
                
            qtd = int(item[1])
            preco_un = float(item[2])
            subtotal = float(item[3])
            
            # 🟢 VISUAL ULTRA CLEAN: Sem "❌", sem "[X]" e sem apertar o texto!
            linha_item = f"{qtd}un x {nome_prod}"
            linha_valores = f"   Un: R$ {preco_un:.2f} | Tot: R$ {subtotal:.2f}".replace('.', ',')
            
            # Injeta a primeira linha (Nome) guardando a referência e o preço de controle
            item_lista_nome = QtWidgets.QListWidgetItem(linha_item)
            item_lista_nome.setData(QtCore.Qt.UserRole, subtotal)
            item_lista_nome.setData(QtCore.Qt.UserRole + 1, "ativo")
            self.listWidgetCupom.addItem(item_lista_nome)
            
            # Injeta a segunda linha (Valores) vinculando-a ao mesmo controle de preço
            item_lista_valores = QtWidgets.QListWidgetItem(linha_valores)
            item_lista_valores.setData(QtCore.Qt.UserRole, subtotal)
            item_lista_valores.setData(QtCore.Qt.UserRole + 1, "ativo")
            self.listWidgetCupom.addItem(item_lista_valores)
            
            # Salva uma referência mútua na memória para uma linha saber quem é a sua parceira ao clicar
            item_lista_nome.setData(QtCore.Qt.UserRole + 2, item_lista_valores)
            item_lista_valores.setData(QtCore.Qt.UserRole + 2, item_lista_nome)
            
            self.listWidgetCupom.addItem(" . . . . . . . . . . . . . . .")
            
        
        self.listWidgetCupom.addItem("------------------------------")
        self.listWidgetCupom.addItem("💡 Dica: clique duas vezes sobre")
        self.listWidgetCupom.addItem("   qualquer produto para cancelá-lo")

        
    except Exception as e:
        self.listWidgetCupom.addItem(f"Erro ao carregar itens: {e}")


# ---------------- CÁLCULO DE DESCONTO ----------------
def calcular_total_com_desconto(self):
    """Calcula o desconto em tempo real e atualiza o faturamento verde"""
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
        if total < 0: total = 0.0
            
        self.lblTotalVenda.setText(f"R$ {total:.2f}".replace('.', ','))
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro no desconto: {e}")


# ---------------- RESETAR RESUMO ----------------
def resetar_resumo_venda(self):
    """Limpa os campos da direita após uma venda concluída"""
    self.pedido_selecionado = None
    self.txt_pedidoVendas.setText("")
    self.lblQtdItensResumo.setText("0")
    self.lblValorSubtotal.setText("R$ 0,00")
    self.txt_descontoVenda.setText("0,00")
    self.lblTotalVenda.setText("R$ 0,00")
    if hasattr(self, 'listWidgetCupom') and self.listWidgetCupom is not None:
        self.listWidgetCupom.clear()


# ---------------- FINALIZAR VENDA (SALVAR NO BANCO) CORRIGIDA ----------------
def finalizar_venda(self):
    """Grava a venda no MySQL e gera o cupom HTML com dados limpos e somas matemáticas reais"""
    if getattr(self, 'pedido_selecionado', None) is None:
        QtWidgets.QMessageBox.warning(self, "Aviso", "Selecione um pedido clicando na tabela!")
        return
        
    forma_pagamento = self.comboPagamento.currentText()
    
    subtotal = self.pedido_selecionado['total']
    desconto_str = self.txt_descontoVenda.text().replace(",", ".")
    desconto = float(desconto_str) if desconto_str else 0.0
    
    total_pago = subtotal - desconto
    if total_pago < 0: total_pago = 0.0
    
    id_pedido = self.pedido_selecionado['id_pedido']
    id_cliente = self.pedido_selecionado['id_cliente']
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # 🟢 BUSCA E DESEMPACOTA OS DADOS REAIS DO CLIENTE DO BANCO
        sql_cliente = "SELECT nome, telefone FROM cliente WHERE id = %s"
        cursor.execute(sql_cliente, (id_cliente,))
        dados_cliente = cursor.fetchone()
        
        if dados_cliente and isinstance(dados_cliente, (list, tuple)):
            nome_c = str(dados_cliente[0])
            tel_c = str(dados_cliente[1])
        else:
            nome_c = "Consumidor Final"
            tel_c = ""
            
        # 🛒 BUSCA OS ITENS ORIGINAIS DO PEDIDO NO BANCO
        sql_itens = """
            SELECT p.nome, ip.quantidade, ip.preco_unitario, ip.subtotal
            FROM item_pedido ip
            INNER JOIN produto p ON ip.id_produto = p.id_produto
            WHERE ip.id_pedido = %s
        """
        cursor.execute(sql_itens, (id_pedido,))
        itens_banco = cursor.fetchall()
        
        # Mapeia quais itens foram marcados como cancelados na interface (UserRole + 1)
        itens_ativos_na_tela = []
        for i in range(self.listWidgetCupom.count()):
            widget_item = self.listWidgetCupom.item(i)
            if widget_item.data(QtCore.Qt.UserRole) is not None:
                status = widget_item.data(QtCore.Qt.UserRole + 1)
                itens_ativos_na_tela.append(status)
        
        # Como cada doce gera duas linhas na tela (Nome e Valores), filtramos pegando apenas as posições pares
        status_filtrados_por_produto = itens_ativos_na_tela[::2]
        
        itens_html = ""
        soma_subtotal_real_produtos = 0.0 # 🟢 MOTOR DE SOMA FIXADO DO RECIBO
        
        for idx, item in enumerate(itens_banco):
            # Ignora o produto se ele estiver marcado como cancelado pelo duplo clique no caixa
            if idx < len(status_filtrados_por_produto) and status_filtrados_por_produto[idx] == "cancelado":
                continue
                
            nome_p = str(item[0])
            qtd = int(item[1])
            unidade = float(item[2])
            sub_prod = float(item[3])
            
            # Acumula o valor real de cada produto ativo que vai entrar na conta
            soma_subtotal_real_produtos += sub_prod
            
            itens_html += f"""
            <tr>
                <td style="padding: 6px 0;">
                    <div class="negrito">{nome_p}</div>
                    <div class="sub-item">{qtd} (Un) X R$ {unidade:.2f}</div>
                </td>
                <td class="direita negrito" style="vertical-align: middle; padding: 6px 0;">R$ {sub_prod:.2f}</td>
            </tr>
            <tr><td colspan="2" class="divisor-tracejado"></td></tr>
            """
            
        hoje = date.today().strftime("%Y-%m-%d")
        
        # 🟢 ATUALIZA O TOTAL DA VENDA COM A SOMA CORRETA E O DESCONTO REAL
        subtotal = soma_subtotal_real_produtos
        total_pago = subtotal - desconto
        if total_pago < 0: total_pago = 0.0
        
        sql_venda = """
            INSERT INTO venda (id_pedido, id_cliente, data_venda, forma_pagamento, status_pagamento, total, valor_pago, valor_restante) 
            VALUES (%s, %s, %s, %s, 'Pago', %s, %s, 0)
        """
        cursor.execute(sql_venda, (id_pedido, id_cliente, hoje, forma_pagamento, subtotal, total_pago))
        
        sql_update_pedido = "UPDATE pedido SET status = 'Pago' WHERE id_pedido = %s"
        cursor.execute(sql_update_pedido, (id_pedido,))
        
        conexao.commit()
        
        # Dispara o pop-up passando os valores e subtotais perfeitamente recalculados
        popup = JanelaOpcoesCupom(self, id_pedido, nome_c, tel_c, total_pago, forma_pagamento, desconto, subtotal, itens_html)
        popup.exec_()
        
        __import__('vendas').resetar_resumo_venda(self)
        __import__('vendas').carregar_pedidos_venda(self)
        
        if hasattr(self, 'parent_win') and hasattr(self.parent_win, 'janela_historico'):
            if self.parent_win.janela_historico and self.parent_win.janela_historico.isVisible():
                self.parent_win.janela_historico.carregar_relatorio_detalhado()
        
    except Exception as e:
        conexao.rollback()
        QtWidgets.QMessageBox.warning(self, "Erro", f"Erro ao finalizar venda: {e}")



# ---------------- AÇÃO DE CANCELAR ITEM NO CUPOM ----------------
def acao_cancelar_item_cupom(self, item):
    """Aplica o efeito riscado casado nas duas linhas do produto simultaneamente sem alterar o texto"""
    subtotal_item = item.data(QtCore.Qt.UserRole)
    if subtotal_item is None:
        return 
        
    status_atual = item.data(QtCore.Qt.UserRole + 1)
    item_parceiro = item.data(QtCore.Qt.UserRole + 2) # Puxa a outra linha do mesmo bolo
    
    if getattr(self, 'pedido_selecionado', None) is None:
        return
        
    subtotal_venda = float(self.pedido_selecionado['total'])
    
    # EXTRAÇÃO DA QUANTIDADE DA LINHA (Busca sempre na linha de texto do nome)
    try:
        texto_linha = item.text() if "un x" in item.text() else item_parceiro.text()
        qtd_item = int(texto_linha.split("un")[0].strip())
    except:
        qtd_item = 1
    
    try:
        qtd_total_atual = int(self.lblQtdItensResumo.text())
    except:
        qtd_total_atual = 0
    
    font_clicada = item.font()
    font_parceira = item_parceiro.font() if item_parceiro else font_clicada
    
    if status_atual == "ativo":
        # Aplica o risco cinza na linha clicada
        font_clicada.setStrikeOut(True)
        item.setFont(font_clicada)
        item.setForeground(QtCore.Qt.gray)
        item.setData(QtCore.Qt.UserRole + 1, "cancelado")
            
        # 🟢 COMPORTAMENTO CASADO: Risca a linha parceira junto automaticamente!
        if item_parceiro:
            font_parceira.setStrikeOut(True)
            item_parceiro.setFont(font_parceira)
            item_parceiro.setForeground(QtCore.Qt.gray)
            item_parceiro.setData(QtCore.Qt.UserRole + 1, "cancelado")
        
        novo_subtotal = subtotal_venda - subtotal_item
        nova_qtd_total = qtd_total_atual - qtd_item
        
    else:
        # Remove o risco e devolve a cor preta na linha clicada
        font_clicada.setStrikeOut(False)
        item.setFont(font_clicada)
        item.setForeground(QtCore.Qt.black)
        item.setData(QtCore.Qt.UserRole + 1, "ativo")
            
        # Restaura a linha parceira junto!
        if item_parceiro:
            font_parceira.setStrikeOut(False)
            item_parceiro.setFont(font_parceira)
            item_parceiro.setForeground(QtCore.Qt.black)
            item_parceiro.setData(QtCore.Qt.UserRole + 1, "ativo")
        
        novo_subtotal = subtotal_venda + subtotal_item
        nova_qtd_total = qtd_total_atual + qtd_item

    if novo_subtotal < 0: novo_subtotal = 0.0
    if nova_qtd_total < 0: nova_qtd_total = 0
    
    self.pedido_selecionado['total'] = novo_subtotal
    
    self.lblValorSubtotal.setText(f"R$ {novo_subtotal:.2f}".replace('.', ','))
    self.lblQtdItensResumo.setText(str(nova_qtd_total))
    
    __import__('vendas').calcular_total_com_desconto(self)

# ---------------- MOTOR DE FILTRO INSTANTÂNEO DE VENDAS ----------------
def filtrar_pesquisa_vendas_pendentes(self):
    """Varre a tabela de vendas pendentes e filtra os registros de forma instantânea"""
    # 🟢 Puxa o texto digitado direto da barra de pesquisa cinza do topo
    texto_pesquisa = self.txt_pedidoVendas.text().lower().strip()
    
    # Se o operador do caixa clicou na linha e o campo recebeu o texto descritivo interno, ignora o filtro
    if "recebendo pedido" in texto_pesquisa:
        return
        
    for linha in range(self.tableVendas.rowCount()):
        item_codigo = self.tableVendas.item(linha, 0)       
        item_cliente_data = self.tableVendas.item(linha, 1) 
        
        if not item_codigo or not item_cliente_data:
            continue
            
        texto_codigo = item_codigo.text().lower()
        texto_cliente = item_cliente_data.text().lower()
        
        if not texto_pesquisa or (texto_pesquisa in texto_codigo) or (texto_pesquisa in texto_cliente):
            self.tableVendas.setRowHidden(linha, False) 
        else:
            self.tableVendas.setRowHidden(linha, True)  
 
