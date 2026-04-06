import sys
from PyQt5 import QtWidgets
from login import Login
from menu import Menu

app = QtWidgets.QApplication(sys.argv)

login = Login()
menu = Menu()

# 🔥 função que troca de tela
def abrir_menu():
    login.hide()
    menu.show()

# conecta a função ao login
login.abrir_menu = abrir_menu

login.show()

sys.exit(app.exec())