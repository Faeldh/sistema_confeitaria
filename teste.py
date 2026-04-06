import sys
from PyQt5 import uic, QtWidgets
from conexao import conectar

# Carregar telas
tela_menu = uic.loadUiType('telas/tela_menu.ui')[0]
tela_login = uic.loadUiType('telas/tela_login.ui')[0]

# Classe do MENU
class Menu(QtWidgets.QMainWindow, tela_menu):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


# Classe do LOGIN
class Login(QtWidgets.QMainWindow, tela_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Conectar botão
        self.btn_login.clicked.connect(self.verificar_login)
    
    def verificar_login(self):
        nome = self.txt_nome.text()
        senha = self.txt_senha.text()

        conexao = conectar()
        cursor = conexao.cursor()

        comando = 'SELECT * FROM usuario WHERE nome=%s AND senha=%s'
        dados = (nome, senha)

        cursor.execute(comando, dados)
        resultado = cursor.fetchone()

        if resultado:
            print("Login OK")
            QtWidgets.QMessageBox.information(self, 'Login', 'Login realizado com sucesso!')

            # 🔥 ABRIR MENU
            self.menu = Menu()
            self.menu.show()

            # ⚠️ NÃO FECHAR, apenas esconder
            self.hide()

        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválido')

        conexao.close()


# Inicialização do app
app = QtWidgets.QApplication(sys.argv)

janela = Login()
janela.show()

sys.exit(app.exec())