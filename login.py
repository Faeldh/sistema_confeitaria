from PyQt5 import uic, QtWidgets


tela_login = uic.loadUiType('telas/tela_login.ui')[0]

class Login(QtWidgets.QMainWindow, tela_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #self.btn_confimar.clicked.connect(self.verifica_login)

