from PyQt5 import uic, QtWidgets

import cadastro_cliente 

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

               # 🔁 NAVEGAÇÃO ENTRE PÁGINAS
        '''self.btn_ir_cadastro.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_cadastro)
        )'''

        '''self.btn_voltar.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_home)
        )'''

        # 💾 SALVAR CADASTRO
        self.btn_salvar.clicked.connect(self.salvar_cliente)
        self.btn_atualizar.clicked.connect(self.atualizar_lista)

        cadastro_cliente.atualizar(self)

    def salvar_cliente(self):
        cadastro_cliente.salvar(self)
    
    def atualizar_lista(self):
        cadastro_cliente.atualizar(self)

    

    