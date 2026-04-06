import sys
from PyQt5 import uic, QtWidgets

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]
tela_login = uic.loadUiType('telas/tela_login.ui')[0]


class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class Login(QtWidgets.QMainWindow, tela_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_login.clicked.connect(self.verificar_login)
    
    def verificar_login(self):
        nome = self.txt_nome.text()
        senha = self.txt_senha.text()

        # 🔹 LOGIN FAKE (para testes)
        if nome == "admin" and senha == "123":
            QtWidgets.QMessageBox.information(self, 'Login', 'Login realizado com sucesso!')

            self.menu = Menu()
            self.menu.show()

            self.hide()
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválido')


# Inicialização do app
app = QtWidgets.QApplication(sys.argv)

janela = Login()
janela.show()

sys.exit(app.exec())