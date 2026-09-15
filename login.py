from PyQt5 import uic, QtWidgets, QtCore, QtGui
from conexao import conectar
import pymysql.cursors

tela_login = uic.loadUiType('telas/TELA_LOGIN_TESTE.ui')[0]

class Login(QtWidgets.QMainWindow, tela_login):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # --- MAQUIAGEM VISUAL PROFISSIONAL ---
        self.setStyleSheet("""
            QMainWindow { background-color: #F8FAFC; }
            
            /* Inputs elegantes e arredondados iguas à sua foto */
            QLineEdit {
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 12px;
                background-color: #FFFFFF;
                color: #1E293B;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3F4A2F; /* Realce com o verde oliva da sua logo */
                background-color: #FAFAFA;
            }
            
            /* Botão Entrar com transição suave (Hover) */
            QPushButton#btn_login {
                background-color: #3F4A2F;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: bold;
                text-transform: uppercase;
            }
            QPushButton#btn_login:hover {
                background-color: #2E3723; /* Escurece um pouco ao passar o mouse */
            }
            QPushButton#btn_login:pressed {
                background-color: #1F2518;
            }
        """)

        # --- CONFIGURAÇÃO DOS EVENTOS ---
        self.btn_login.clicked.connect(self.verificar_login)
        self.btn_login.setDefault(True)
        self.txt_senha.returnPressed.connect(self.verificar_login)

        # --- APERFEIÇOAMENTO: ANIMAÇÃO DE ENTRADA (Fade-In) ---
        self.setWindowOpacity(0.0)
        self.animacao_entrada = QtCore.QPropertyAnimation(self, b"windowOpacity")
        self.animacao_entrada.setDuration(350)
        self.animacao_entrada.setStartValue(0.0)
        self.animacao_entrada.setEndValue(1.0)
        self.animacao_entrada.start()

    def animar_erro_tremor(self):
        """Faz a janela inteira tremer na horizontal se o usuário errar os dados!"""
        self.animacao_shake = QtCore.QSequentialAnimationGroup()
        pos_original = self.pos()
        
        # Cria pequenos movimentos rápidos de vai e vem para os lados
        for i in range(3):
            mover_direita = QtCore.QPropertyAnimation(self, b"pos")
            mover_direita.setDuration(50)
            mover_direita.setStartValue(self.pos())
            mover_direita.setEndValue(QtCore.QPoint(self.x() + 10, self.y()))
            
            mover_esquerda = QtCore.QPropertyAnimation(self, b"pos")
            mover_esquerda.setDuration(50)
            mover_esquerda.setStartValue(QtCore.QPoint(self.x() + 10, self.y()))
            mover_esquerda.setEndValue(QtCore.QPoint(self.x() - 10, self.y()))
            
            self.animacao_shake.addAnimation(mover_direita)
            self.animacao_shake.addAnimation(mover_esquerda)
            
        # Retorna para a posição original no final
        voltar_origem = QtCore.QPropertyAnimation(self, b"pos")
        voltar_origem.setDuration(50)
        voltar_origem.setEndValue(pos_original)
        self.animacao_shake.addAnimation(voltar_origem)
        
        self.animacao_shake.start()

    def verificar_login(self):
        usuario = self.txt_nome.text().strip()
        senha = self.txt_senha.text()

        conexao = conectar()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)

        comando = 'SELECT * FROM usuario WHERE login=%s AND senha=%s'
        cursor.execute(comando, (usuario, senha))
        resultado = cursor.fetchone()

        if resultado:
            QtWidgets.QMessageBox.information(self, 'Login', f"Bem-vindo(a) de volta, {resultado['nome_completo']}! 🍰")
            from menu import Menu
            self.menu = Menu()
            self.menu.show()
            self.close()
        else:
            # Em vez de só abrir um aviso seco, a tela vai tremer fisicamente avisando do erro!
            self.animar_erro_tremor()
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválidos!')

        # --- FORÇAR HOVER NO BOTÃO (IGNORA O QT DESIGNER) ---
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3F4A2F; /* Verde oliva padrão */
                color: #FFFFFF;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: bold;
                text-transform: uppercase;
                border: none;
            }
            QPushButton:hover {
                background-color: #2E3723; /* Tom mais escuro quando o mouse passa por cima */
            }
            QPushButton:pressed {
                background-color: #1F2518; /* Tom bem escuro ao clicar */
            }
        """)

        # EXTRA: Faz o cursor do teclado já iniciar piscando direto no campo de Usuário
        self.txt_nome.setFocus()


        cursor.close()
        conexao.close()
