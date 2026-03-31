import sys
from PyQt5 import uic, QtWidgets

tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]

class menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)



app = QtWidgets.QApplication(sys.argv)
janela = menu()
janela.show()

sys.exit(app.exec())