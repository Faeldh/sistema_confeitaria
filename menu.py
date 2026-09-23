from PyQt5 import uic, QtWidgets
import dashboard

# =============================================================================
# 🎓 CARREGAMENTO VISUAL 
# Lê o arquivo XML da tela do sistema.
# =============================================================================
tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]


class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self) # Monta e renderiza os botões e tabelas na tela

        # --- ATIVAÇÃO DA DIVISÃO RESPONSIVA OPERACIONAL (PROTEGIDA) ---
        if hasattr(self, 'layoutGeralPedidos'):
            self.layoutGeralPedidos.setStretch(0, 4)
            self.layoutGeralPedidos.setStretch(1, 6)
        
        # --- ESTILIZAÇÃO DAS TABELAS DA ABA DE PEDIDOS (ESQUEMA MODERNO) ---
        self.tableItens.verticalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableItens.setShowGrid(False)
        self.tableWidget.setShowGrid(False)

        from PyQt5.QtWidgets import QHeaderView
        self.tableItens.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # --- ESTILIZAÇÃO DAS TABELAS (ESQUEMA MODERNO MIRA CONFEITARIA) ---
        estilo_tabelas = """
            QTableWidget, QTableView {
                background-color: white;
                border: 2px solid #3F4A2F;
                border-radius: 10px;
                alternate-background-color: #F9F9F9;
            }
            QTableWidget::item, QTableView::item { 
                padding: 6px; 
                border-bottom: 1px solid #E0E0E0; 
            }
            QHeaderView::section { 
                background-color: #3F4A2F; 
                color: #E6D2A2; 
                padding: 6px; 
                font-weight: bold; 
                border: none; 
            }
            
            /* ✨ TOQUE DE OURO: Faz a linha selecionada ficar verde e com letras douradas! */
            QTableWidget::item:selected, QTableView::item:selected {
                background-color: #3F4A2F;
                color: #E6D2A2;
            }
        """

        # 🎨 Aplicando o estilo de Pedidos em todas as tabelas do sistema
        tabelas_sistema = [
            self.tableItens, 
            self.tableWidget, 
            self.tableWidgetClientes, 
            self.tableWidgetReceitas, 
            self.tableWidgetFornecedores, 
            getattr(self, 'tableViewProdutos', None),
            getattr(self, 'tabela_tamanhos', None) 
        ]

                # 🎨 ESTILIZAÇÃO EXCLUSIVA PARA OS CABEÇALHOS DA TELA DE PEDIDOS
        css_cabecalho_pedidos = """
            QHeaderView::section { 
                background-color: #3F4A2F; 
                color: #E6D2A2; 
                padding: 6px; 
                font-weight: bold; 
                border: none;
                font-size: 13px; /* ⬅️ Aumentado para alinhar com o padrão do sistema */
            }
        """
        if hasattr(self, 'tableItens'):
            self.tableItens.horizontalHeader().setStyleSheet(css_cabecalho_pedidos)
        if hasattr(self, 'tableWidget'):
            self.tableWidget.horizontalHeader().setStyleSheet(css_cabecalho_pedidos)


        for tabela in tabelas_sistema:
            if tabela:
                tabela.verticalHeader().setVisible(False)
                tabela.setShowGrid(False)
                tabela.setStyleSheet(estilo_tabelas)

        # 🛡️ AJUSTE DE PROPORÇÃO RESPONSIVA DO CARRINHO DE PEDIDOS (LADO ESQUERDO)
        if hasattr(self, 'tableItens'):
            header_carrinho = self.tableItens.horizontalHeader()
            header_carrinho.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            header_carrinho.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)           # Produto estica tudo
            header_carrinho.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents) # Sabor justo
            header_carrinho.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents) # Tamanho justo
            header_carrinho.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents) # Quantidade curta
            header_carrinho.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents) # Subtotal justo
            header_carrinho.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents) # Botão X

        # 🛡️ AJUSTE DE PROPORÇÃO RESPONSIVA DA FILA DA COZINHA (LADO DIREITO)
        if hasattr(self, 'tableWidget'):
            header_cozinha = self.tableWidget.horizontalHeader()
            header_cozinha.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            header_cozinha.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents) # ID curto
            header_cozinha.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)           # Cliente estica tudo
            header_cozinha.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents) # Data Pedido
            header_cozinha.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents) # Entrega
            header_cozinha.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents) # Total justo

        # ✨ AJUSTE DE OURO: Faz a coluna "Tamanho" ocupar todo o espaço em branco da tabela de produtos
        if hasattr(self, 'tabela_tamanhos'):
            header_grade = self.tabela_tamanhos.horizontalHeader()
            header_grade.setSectionResizeMode(QtWidgets.QHeaderView.Interactive)
            header_grade.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch) # Estica o Tamanho
            header_grade.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents) # Preço justo

        # 🟢 FORÇA A SELEÇÃO DA LINHA INTEIRA SÓLIDA NAS TELAS PRINCIPAIS
        for tabela_tarja in [self.tableItens, self.tableWidget, getattr(self, 'tableViewProdutos', None)]:
            if tabela_tarja:
                tabela_tarja.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Configura o botão Atualizar na página de produtos
        self.btnAtualizarProduto.setText("Atualizar")
        self.btnAtualizarProduto.setMinimumWidth(80) 

        self.showMaximized()

        # Ocultação de Cabeçalhos Verticais das abas legadas
        self.tableWidgetClientes.verticalHeader().setVisible(False)
        self.tableWidgetReceitas.verticalHeader().setVisible(False)
        self.tableWidgetFornecedores.verticalHeader().setVisible(False)
        # Configurações de Cliques e Seleção das Tabelas Legadas
        self.tableWidgetClientes.itemSelectionChanged.connect(self.carregar_cliente)
        self.tableWidgetReceitas.itemSelectionChanged.connect(self.carregar_receita)
        self.tableWidgetFornecedores.itemSelectionChanged.connect(self.carregar_fornecedor)

        self.tableWidgetClientes.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.tableWidgetReceitas.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.tableWidgetFornecedores.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        self.tableWidgetClientes.itemDoubleClicked.connect(self.carregar_cliente)
        self.tableWidgetReceitas.itemDoubleClicked.connect(self.carregar_receita)

        self.stackedWidget.setCurrentWidget(self.pageControleFinanceiro)

        # --- MAPEAMENTO DOS BOTÕES DE NAVEGAÇÃO DO MENU SUPERIOR ---
        self.btn_clientes.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.pageClientes))
        self.btn_fornecedores.clicked.connect(lambda: (
            self.stackedWidget.setCurrentWidget(self.pageFornecedores),
            __import__('cadastro_fornecedor').configurar_campos(self),
            __import__('cadastro_fornecedor').atualizar(self)
        ))
        self.btn_produtos.clicked.connect(lambda: (
            __import__('cadastro_produtos').configurar_busca_chrome(self),
            __import__('cadastro_produtos').listar(self),
            self.stackedWidget.setCurrentWidget(self.pageProdutos)
         ))
        self.btn_receitas.clicked.connect(lambda: (
            __import__('cadastro_receitas').atualizar(self),
            self.stackedWidget.setCurrentWidget(self.pageReceitas)
        ))
        self.btn_pedidos.clicked.connect(lambda: (
            __import__('pedidos').inicializar_pedidos(self),
            self.stackedWidget.setCurrentWidget(self.pagePedidos)
        ))
        self.btn_vendas.clicked.connect(lambda: (
            __import__('vendas').inicializar_vendas(self),
            self.stackedWidget.setCurrentWidget(self.pageVendas)
        ))
        self.btn_controle_financeiro.clicked.connect(lambda: (
            self.stackedWidget.setCurrentWidget(self.pageControleFinanceiro),
            dashboard.atualizar_dashboard(self)
        ))

        self.actionCONGIGUR_ES.triggered.connect(lambda: (
            self.stackedWidget.setCurrentWidget(self.pageConfiguracoes),
            __import__('configuracoes').inicializar(self)
        ))
        # --- GATILHOS OPERACIONAIS DE CLIENTES ---
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_limpar.clicked.connect(self.limpar_info)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)
        self.txt_pesquisa.textChanged.connect(self.pesquisar)
        self.txt_pesquisaReceita.textChanged.connect(self.pesquisar_receita)
        
        if hasattr(self, 'txt_pedidoVendas'):
            self.txt_pedidoVendas.textChanged.connect(lambda: __import__('vendas').filtrar_pesquisa_vendas_pendentes(self))

        # --- GATILHOS OPERACIONAIS DE RECEITAS ---
        self.btn_salvarReceitas.clicked.connect(self.salvar_receitas)
        self.btn_AtualizarReceita.clicked.connect(self.atualizar_receitas)
        self.btn_limparReceita.clicked.connect(self.limpar_rceita)
        self.btn_excluirReceita.clicked.connect(self.deletar_receita)
        self.btn_editarReceita.clicked.connect(self.editar_receita)
        
        # --- GATILHOS OPERACIONAIS DE FORNECEDORES ---
        self.btn_salvarFornecedor.clicked.connect(self.salvar_fornecedor)
        self.btn_limparFornecedor.clicked.connect(lambda: __import__('cadastro_fornecedor').limpar(self))
        self.btn_atualizarFornecedor.clicked.connect(self.atualizar_fornecedores)
        self.lineEditPesquisaFornecedor.textChanged.connect(self.pesquisar_fornecedor)
        
        # --- GATILHOS OPERACIONAIS DE PRODUTOS ---
        if hasattr(self, 'btn_salvarProduto'):
            self.btn_salvarProduto.clicked.connect(lambda: __import__('cadastro_produtos').salvar(self))
        if hasattr(self, 'btn_limparProduto'):
            self.btn_limparProduto.clicked.connect(lambda: __import__('cadastro_produtos').limpar(self))
        if hasattr(self, 'btn_add_sabor'):
            self.btn_add_sabor.clicked.connect(lambda: __import__('cadastro_produtos').adicionar_sabor(self))
        if hasattr(self, 'btn_add_variacao'):
            self.btn_add_variacao.clicked.connect(lambda: __import__('cadastro_produtos').adicionar_variacao(self))
        if hasattr(self, 'txt_novo_sabor'):
            self.txt_novo_sabor.returnPressed.connect(lambda: __import__('cadastro_produtos').adicionar_sabor(self))
        
        if hasattr(self, 'btn_editarProduto'):
            self.btn_editarProduto.clicked.connect(lambda: __import__('cadastro_produtos').editar(self))
        if hasattr(self, 'btn_excluirProduto'):
            self.btn_excluirProduto.clicked.connect(lambda: __import__('cadastro_produtos').excluir_direto_tabela(self))
        
        if hasattr(self, 'btnAtualizarProduto'):
            self.btnAtualizarProduto.clicked.connect(lambda: __import__('cadastro_produtos').listar(self))
        if hasattr(self, 'tableViewProdutos'):
            self.tableViewProdutos.itemSelectionChanged.connect(lambda: __import__('cadastro_produtos').pegar_dados(self))

        # --- GATILHOS OPERACIONAIS DE VENDAS E CARRINHO DE PEDIDOS ---
        if hasattr(self, 'tableVendas'):
            self.tableVendas.cellClicked.connect(lambda row, col: __import__('vendas').acao_tabela_vendas(self, row, col))
        if hasattr(self, 'txt_descontoVenda'):
            self.txt_descontoVenda.textChanged.connect(lambda: __import__('vendas').calcular_total_com_desconto(self))
        if hasattr(self, 'btnSalvarVenda'):
            self.btnSalvarVenda.clicked.connect(lambda: __import__('vendas').finalizar_venda(self))
            
        self.listWidgetCupom.setWordWrap(True)
        self.btnBuscaClienteVenda.clicked.connect(self.abrir_historico_vendas)
        
        self.btnAddCarrinho.clicked.connect(lambda: __import__('pedidos').adicionar_carrinho(self))
        self.btnExcluirPedido.clicked.connect(lambda: __import__('pedidos').gerar_pedido(self))
        self.btnFinalizar.clicked.connect(lambda: __import__('pedidos').acao_botao_finalizar_pedido(self))

        self.actionSAIR_DO_APLICATIVO.triggered.connect(self.voltar_para_login)
        self.btnSalvarAlteracoes.clicked.connect(lambda: __import__('configuracoes').salvar(self))
        self.btnGerenciarUsuarios.clicked.connect(lambda: __import__('configuracoes').gerenciar_usuarios(self))
        self.btnBaixarBanco.clicked.connect(lambda: __import__('configuracoes').fazer_backup_banco(self))
        self.btnVerInformacoes.clicked.connect(lambda: __import__('configuracoes').exibir_sobre_sistema(self))

        # --- CARGA INICIAL AUTOMÁTICA DO BANCO DE DADOS ---
        __import__('configuracoes').inicializar(self)
        __import__('cadastro_cliente').atualizar(self)
        __import__('cadastro_fornecedor').atualizar(self)
        __import__('cadastro_receitas').atualizar(self)
        if hasattr(self, 'combo_categoria'): __import__('cadastro_produtos').configurar_busca_chrome(self)
        __import__('cadastro_produtos').listar(self)
        __import__('pedidos').inicializar_pedidos(self)
        if hasattr(self, 'pageVendas'): __import__('vendas').inicializar_vendas(self)
        dashboard.atualizar_dashboard(self)

        botoes_para_esconder = ["btn_editar", "btn_excluir", "btn_editarFornecedor", "btn_excluirFornecedor", "btn_editarReceita", "btn_excluirReceita"]
        for botao in botoes_para_esconder:
            if hasattr(self, botao): getattr(self, botao).hide()

        __import__('cadastro_cliente').configurar_campos(self)
        __import__('cadastro_fornecedor').configurar_campos(self)
        __import__('cadastro_receitas').configurar_campos(self)

    # === REPASSES INTERNOS PARA AS ABAS ORIGINAIS ===
    def editar_receita(self): __import__('cadastro_receitas').editar(self)
    def atualizar_receitas(self): __import__('cadastro_receitas').atualizar(self)
    def limpar_rceita(self): __import__('cadastro_receitas').limpar(self)
    def salvar_cliente(self): __import__('cadastro_cliente').salvar(self)
    def atualizar_lista(self): __import__('cadastro_cliente').atualizar(self)
    def pesquisar(self): __import__('cadastro_cliente').pesquisa(self)
    def limpar_info(self): __import__('cadastro_cliente').limpar(self)
    def salvar_receitas(self): __import__('cadastro_receitas').salvar(self)
    def pesquisar_receita(self): __import__('cadastro_receitas').pesquisar(self)
    def deletar_receita(self): __import__('cadastro_receitas').deletar(self)
    def salvar_fornecedor(self): __import__('cadastro_fornecedor').salvar(self)
    def atualizar_fornecedores(self): __import__('cadastro_fornecedor').atualizar(self)
    def pesquisar_fornecedor(self): __import__('cadastro_fornecedor').pesquisa(self)
    def deletar_fornecedor(self): __import__('cadastro_fornecedor').deletar(self)

    def carregar_cliente(self):
        linha = self.tableWidgetClientes.currentRow()
        if linha == -1: return
        id_cliente = self.tableWidgetClientes.item(linha, 0).text()
        __import__('cadastro_cliente').buscar_por_id(self, id_cliente)

    def carregar_receita(self):
        linha = self.tableWidgetReceitas.currentRow()
        if linha == -1: return
        id_receita = self.tableWidgetReceitas.item(linha, 0).text()
        __import__('cadastro_receitas').buscar_por_id(self, id_receita)

    def carregar_fornecedor(self):
        linha = self.tableWidgetFornecedores.currentRow()
        if linha == -1: return
        id_fornecedor = self.tableWidgetFornecedores.item(linha, 0).text()
        __import__('cadastro_fornecedor').buscar_por_id(self, id_fornecedor)

    def voltar_para_login(self):
        from login import Login
        self.tela_de_login = Login()
        self.tela_de_login.show()
        self.close()

    def abrir_historico_vendas(self):
        from vendas_historico import HistoricoVendasWindow
        self.janela_historico = HistoricoVendasWindow(self)
        self.janela_historico.exec_()
