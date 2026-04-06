from PyQt5 import uic, QtWidgets
from conexao import conectar
from menu import Menu


tela_login = uic.loadUiType('telas/tela_login.ui')[0]

class Login(QtWidgets.QMainWindow, tela_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_login.clicked.connect(self.verificar_login)
    
    def verificar_login(self):
        
        print("CLICOU NO BOTÃO")
        nome = self.txt_nome.text().strip()
        senha = self.txt_senha.text().strip()

        print("Nome digitado:", nome)
        print("Senha digitada:", senha)

        try:
            conexao = conectar()
            cursor = conexao.cursor()

            comando = 'SELECT * FROM usuario WHERE nome=%s AND senha=%s'
            dados = (nome, senha)

            cursor.execute(comando, dados)
            resultado = cursor.fetchone()

            print("Resultado do banco:", resultado)

            if resultado:
                print("Login OK")
                QtWidgets.QMessageBox.information(self, 'login', 'Login realizado com sucesso!')

                from menu import Menu
                self.menu = Menu()
                self.menu.show()
                self.hide()
            else:
                print("Login falhou")
                QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválido')

            conexao.close()

        except Exception as erro:
            print("ERRO:", erro)
            QtWidgets.QMessageBox.critical(self, 'Erro', f'Erro ao conectar:\n{erro}')
