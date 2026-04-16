from PyQt5 import uic, QtWidgets

import cadastro_cliente 

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.tableWidgetClientes.verticalHeader().setVisible(False)
        self.tableWidgetClientes.itemSelectionChanged.connect(self.carregar_cliente)
        self.tableWidgetClientes.itemDoubleClicked.connect(self.carregar_cliente)
        self.tableWidgetClientes.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        

        self.btn_clientes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageClientes)
        )

        self.btn_pedidos.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pagePedidos)
        )

        self.btn_receitas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageReceitas)
        )

        #self.btn_producao.clicked.connect(
            #lambda: self.stackedWidget.setCurrentWidget(self.pageControleProducao)
        #)

        self.btn_produtos.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageProdutos)
        )

        self.btn_vendas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageVendas)
        )

        self.btn_controle_financeiro.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageControleProducao)
        )

        self.btn_fornecedores.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageFornecedores)
        )

        self.btn_editar.clicked.connect(
            lambda: cadastro_cliente.editar(self)
        )

        self.btn_excluir.clicked.connect(
            lambda: cadastro_cliente.deletar(self)
        )


        self.btn_pesquisa.clicked.connect(self.pesquisar)
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)
        self.btn_limpar.clicked.connect(self.limpar_info)
        

        cadastro_cliente.atualizar(self)

    def salvar_cliente(self):
        cadastro_cliente.salvar(self)
    
    def atualizar_lista(self):
        cadastro_cliente.atualizar(self)
    
    def pesquisar(self):
        cadastro_cliente.pesquisa(self)
    
    def limpar_info(self):
        cadastro_cliente.limpar(self)
    
    
    def carregar_cliente(self):
        linha = self.tableWidgetClientes.currentRow()

        if linha == -1:
            return

        id_cliente = self.tableWidgetClientes.item(linha, 0).text()

        cadastro_cliente.buscar_por_id(self, id_cliente)