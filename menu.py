from PyQt5 import uic, QtWidgets

import cadastro_cliente 

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_clientes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageClientes)
        )

        self.btn_pedidos.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pagePedidos)
        )

        self.btn_receitas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageReceitas)
        )

        self.btn_producao.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageControleProducao)
        )

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

        '''self.btn_clientes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_clientes)
        )'''

        
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)

        cadastro_cliente.atualizar(self)

    def salvar_cliente(self):
        cadastro_cliente.salvar(self)
    
    def atualizar_lista(self):
        cadastro_cliente.atualizar(self)

    

    