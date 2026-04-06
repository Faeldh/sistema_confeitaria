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
            print("Tentando conectar...")
            conexao = conectar()

            print("Criando cursor...")
            cursor = conexao.cursor()

            comando = 'SELECT * FROM usuario WHERE nome=%s AND senha=%s'
            dados = (nome, senha)

            print("Executando SQL...")
            cursor.execute(comando, dados)

            print("Buscando resultado...")
            resultado = cursor.fetchone()

            print("Resultado do banco:", resultado)

            if resultado:
                print("Login OK")
            else:
                print("Login falhou")

            conexao.close()

        except Exception as erro:
            print("🔥 ERRO COMPLETO:", erro)