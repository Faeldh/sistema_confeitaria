import sys
from PyQt5 import uic, QtWidgets
from login import Login

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

app = QtWidgets.QApplication(sys.argv)
janela = Login()
janela.show()


sys.exit(app.exec())