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


        
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)

        cadastro_cliente.atualizar(self)

    def salvar_cliente(self):
        cadastro_cliente.salvar(self)
    
    def atualizar_lista(self):
        cadastro_cliente.atualizar(self)

    

    def carregar_cliente(self):
        linha = self.tableWidgetClientes.currentRow()

        if linha == -1:
            return
        
        id = self.tableWidgetClientes.item(linha, 0).text()
        nome = self.tableWidgetClientes.item(linha, 1).text()
        telefone = self.tableWidgetClientes.item(linha, 2).text()
        data_format = self.tableWidgetClientes.item(linha, 3).text()
        cpf = self.tableWidgetClientes.item(linha, 4).text()
        cep = self.tableWidgetClientes.item(linha, 5).text()
        rua = self.tableWidgetClientes.item(linha, 6).text()
        bairro = self.tableWidgetClientes.item(linha, 7).text()
        n = self.tableWidgetClientes.item(linha, 8).text()
        complemento = self.tableWidgetClientes.item(linha, 9).text()
        cidade = self.tableWidgetClientes.item(linha, 10).text()
        email = self.tableWidgetClientes.item(linha, 11).text()
        observcoes = self.tableWidgetClientes.item(linha, 12).text()

        self.txt_nome.setText(nome)
        self.txt_telefone.setText(telefone)
        self.dateEditNascimento.date(data_format)
        self.txt_cpf.setText(cpf)
        self.txt_cep.setText(cep)
        self.txt_rua.setText(rua)
        self.txt_bairro.setText(bairro)
        self.txt_n.setText(n)
        self.txt_complemento.setText(complemento)
        self.txt_cidade.setText(cidade)
        self.txt_email.setText(email)
        self.txt_observcoes.setText(observcoes)


        self.id = id