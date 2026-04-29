from PyQt5 import uic, QtWidgets

import cadastro_cliente 
import cadastro_receitas
import cadastro_fornecedor

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #Esconde a coluna lateral da tabela (números das linhas)
        self.tableWidgetClientes.verticalHeader().setVisible(False)
        self.tableWidgetReceitas.verticalHeader().setVisible(False)
        self.tableWidgetFornecedores.verticalHeader().setVisible(False)


        #SELECIONAR NA TABELA
        self.tableWidgetClientes.itemSelectionChanged.connect(self.carregar_cliente)
        self.tableWidgetReceitas.itemSelectionChanged.connect(self.carregar_receita)
        self.tableWidgetFornecedores.itemSelectionChanged.connect(self.carregar_fornecedor)



        self.tableWidgetClientes.itemDoubleClicked.connect(self.carregar_cliente)
        self.tableWidgetClientes.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)

        
        self.tableWidgetFornecedores.itemSelectionChanged.connect(self.carregar_fornecedor)
        self.tableWidgetFornecedores.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)


        #Chamar as paginas
        self.btn_clientes.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageClientes)
        )

        self.btn_pedidos.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pagePedidos)
        )

        self.btn_receitas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageReceitas)
        )

        self.btn_produtos.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageProdutos)
        )

        self.btn_vendas.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageVendas)
        )

        self.btn_controle_financeiro.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.pageControleFinanceiro)
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

        #Botões
        self.btn_pesquisa.clicked.connect(self.pesquisar)
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)
        self.btn_limpar.clicked.connect(self.limpar_info)
        self.btn_salvarReceitas.clicked.connect(self.salvar_receitas)
        self.btn_AtualizarReceita.clicked.connect(self.atualizar_receitas)
        self.btn_pesquisarReceita.clicked.connect(self.pesquisar_receita)
        self.btn_excluirReceita.clicked.connect(self.deletar_receita)
        self.btn_salvarFornecedor.clicked.connect(self.salvar_fornecedor)
        self.btn_atualizarFornecedor.clicked.connect(self.atualizar_fornecedores)
        self.btn_pesquisaFornecedor.clicked.connect(self.pesquisar_fornecedor)
        self.btn_excluirFornecedor.clicked.connect(self.deletar_fornecedor)
        self.btn_editarFornecedor.clicked.connect(lambda: cadastro_fornecedor.editar(self))
        self.btn_limparFornecedor.clicked.connect(lambda: cadastro_fornecedor.limpar(self))

        cadastro_cliente.atualizar(self)
        cadastro_fornecedor.atualizar(self)

    def atualizar_receitas(self):
        cadastro_receitas.atualizar(self)

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

    def carregar_receita(self):
        linha = self.tableWidgetReceitas.currentRow()

        if linha == -1:
            return
        
        id_receita = self.tableWidgetReceitas.item(linha, 0).text()
        cadastro_receitas.buscar_por_id(self, id_receita)
    
    def salvar_receitas(self):
        cadastro_receitas.salvar(self)

    def pesquisar_receita(self):
        cadastro_receitas.pesquisar(self)
    
    def deletar_receita(self):
        cadastro_receitas.deletar(self)

    # Fornecedores
    def salvar_fornecedor(self):
        cadastro_fornecedor.salvar(self)

    def atualizar_fornecedores(self):
        cadastro_fornecedor.atualizar(self)

    def pesquisar_fornecedor(self):
        cadastro_fornecedor.pesquisa(self)

    def deletar_fornecedor(self):
        cadastro_fornecedor.deletar(self)

    def carregar_fornecedor(self):
        linha = self.tableWidgetFornecedores.currentRow()
        if linha == -1:
            return

        id_fornecedor = self.tableWidgetFornecedores.item(linha, 0).text()
        cadastro_fornecedor.buscar_por_id(self, id_fornecedor)