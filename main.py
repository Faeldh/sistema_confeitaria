import sys
from PyQt5 import QtWidgets
from login import Login

app = QtWidgets.QApplication(sys.argv)

janela = Login()
janela.show()

sys.exit(app.exec())