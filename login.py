import os
import pymysql.cursors
from PyQt5 import QtWidgets, QtCore, QtGui
from conexao import conectar

class Login(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Mira Confeitaria - Login")
        self.setFixedSize(1000, 600)
        
        # --- ESTILIZAÇÃO COMPLETA: ULTRA CLEAN ---
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #FFFFFF; }
            
            QLineEdit {
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                padding: 12px;
                background-color: #FFFFFF;
                color: #1E293B;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3F4A2F;
                background-color: #FAFAFA;
            }
            
            QPushButton#btn_login {
                background-color: #3F4A2F;
                color: #FFFFFF;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: bold;
                text-transform: uppercase;
                border: none;
            }
            QPushButton#btn_login:hover {
                background-color: #2E3723;
            }
            QPushButton#btn_login:pressed {
                background-color: #1F2518;
            }
            
            QLabel#lbl_boas_vindas {
                color: #2E3723;
                font-family: 'Segoe UI';
                font-size: 26px;
                font-weight: bold;
            }
            QLabel {
                color: #4A5568;
                font-family: 'Segoe UI';
                font-size: 13px;
            }
        """)

        # --- LAYOUT PRINCIPAL ---
        widget_central = QtWidgets.QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QtWidgets.QHBoxLayout(widget_central)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # 1. METADE ESQUERDA: Painel da Logo
        self.painel_esquerda = QtWidgets.QWidget()
        layout_esquerda = QtWidgets.QVBoxLayout(self.painel_esquerda)
        layout_esquerda.setAlignment(QtCore.Qt.AlignCenter)

        self.container_imagem = QtWidgets.QLabel()
        self.container_imagem.setFixedSize(460, 460) 
        self.container_imagem.setAlignment(QtCore.Qt.AlignCenter)
        
        caminho_imagem = "imagens/logo_mira.png" 
        if os.path.exists(caminho_imagem):
            pixmap = QtGui.QPixmap(caminho_imagem)
            self.pixmap_redimensionado = pixmap.scaled(440, 440, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.container_imagem.setPixmap(self.pixmap_redimensionado)
        else:
            self.container_imagem.setText("Logo não encontrada")

        layout_esquerda.addWidget(self.container_imagem)
        layout_principal.addWidget(self.painel_esquerda, stretch=1)

        # 2. METADE DIREITA: Painel do Formulário
        self.painel_formulario = QtWidgets.QWidget()
        layout_form_vertical = QtWidgets.QVBoxLayout(self.painel_formulario)
        layout_form_vertical.setContentsMargins(60, 20, 60, 20)
        layout_form_vertical.setAlignment(QtCore.Qt.AlignVCenter)
        layout_form_vertical.setSpacing(15)

        lbl_boas_vindas = QtWidgets.QLabel("Bem-vindo de volta")
        lbl_boas_vindas.setObjectName("lbl_boas_vindas")
        layout_form_vertical.addWidget(lbl_boas_vindas)
        layout_form_vertical.addSpacing(10)

        layout_form_vertical.addWidget(QtWidgets.QLabel("Usuário:"))
        self.txt_nome = QtWidgets.QLineEdit()
        self.txt_nome.setPlaceholderText("Digite seu usuário")
        layout_form_vertical.addWidget(self.txt_nome)

        layout_form_vertical.addWidget(QtWidgets.QLabel("Senha:"))
        self.txt_senha = QtWidgets.QLineEdit()
        self.txt_senha.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txt_senha.setPlaceholderText("Digite sua senha")
        layout_form_vertical.addWidget(self.txt_senha)

        layout_form_vertical.addSpacing(15)

        self.btn_login = QtWidgets.QPushButton("Entrar")
        self.btn_login.setObjectName("btn_login")
        layout_form_vertical.addWidget(self.btn_login)

        layout_principal.addWidget(self.painel_formulario, stretch=1)

        # --- GATILHOS ---
        self.btn_login.clicked.connect(self.verificar_login)
        self.btn_login.setDefault(True)
        self.txt_senha.returnPressed.connect(self.verificar_login)
        self.txt_nome.setFocus()

        # --- LINHA DIVISÓRIA SUAVE ---
        sombra = QtWidgets.QGraphicsDropShadowEffect()
        sombra.setBlurRadius(20)
        sombra.setXOffset(-3)
        sombra.setYOffset(0)
        sombra.setColor(QtGui.QColor(0, 0, 0, 10))
        self.painel_formulario.setGraphicsEffect(sombra)

        # --- INICIAR APENAS ANIMAÇÃO DE ENTRADA SUAVE ---
        self.iniciar_animacao_slide_lento()

    def iniciar_animacao_slide_lento(self):
        """Faz a tela entrar em um slide de baixo para cima elegante e depois para, ficando ultra leve."""
        self.opacidade_esq = QtWidgets.QGraphicsOpacityEffect(self.painel_esquerda)
        self.painel_esquerda.setGraphicsEffect(self.opacidade_esq)
        
        self.opacidade_dir = QtWidgets.QGraphicsOpacityEffect(self.painel_formulario)
        self.painel_formulario.setGraphicsEffect(self.opacidade_dir)

        self.grupo_animacoes = QtCore.QParallelAnimationGroup()

        # Fade-in suave (Esmaecer aparecendo)
        fade_esq = QtCore.QPropertyAnimation(self.opacidade_esq, b"opacity")
        fade_esq.setDuration(900) # 0.9 segundos para entrada fluida
        fade_esq.setStartValue(0.0)
        fade_esq.setEndValue(1.0)
        
        fade_dir = QtCore.QPropertyAnimation(self.opacidade_dir, b"opacity")
        fade_dir.setDuration(900)
        fade_dir.setStartValue(0.0)
        fade_dir.setEndValue(1.0)

        # Slide subindo (Desloca apenas 40 pixels)
        slide_esq = QtCore.QPropertyAnimation(self.painel_esquerda, b"geometry")
        slide_esq.setDuration(900)
        slide_esq.setStartValue(QtCore.QRect(0, 40, 500, 600))
        slide_esq.setEndValue(QtCore.QRect(0, 0, 500, 600))
        slide_esq.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        slide_dir = QtCore.QPropertyAnimation(self.painel_formulario, b"geometry")
        slide_dir.setDuration(900)
        slide_dir.setStartValue(QtCore.QRect(500, 40, 500, 600))
        slide_dir.setEndValue(QtCore.QRect(500, 0, 500, 600))
        slide_dir.setEasingCurve(QtCore.QEasingCurve.OutCubic)

        self.grupo_animacoes.addAnimation(fade_esq)
        self.grupo_animacoes.addAnimation(fade_dir)
        self.grupo_animacoes.addAnimation(slide_esq)
        self.grupo_animacoes.addAnimation(slide_dir)
        
        self.grupo_animacoes.start()

    def animar_erro_tremor(self):
        self.animacao_shake = QtCore.QSequentialAnimationGroup()
        pos_original = self.pos()
        for i in range(3):
            d = QtCore.QPropertyAnimation(self, b"pos")
            d.setDuration(45)
            d.setEndValue(QtCore.QPoint(self.x() + 8, self.y()))
            e = QtCore.QPropertyAnimation(self, b"pos")
            e.setDuration(45)
            e.setEndValue(QtCore.QPoint(self.x() - 8, self.y()))
            self.animacao_shake.addAnimation(d)
            self.animacao_shake.addAnimation(e)
        v = QtCore.QPropertyAnimation(self, b"pos")
        v.setDuration(45)
        v.setEndValue(pos_original)
        self.animacao_shake.addAnimation(v)
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
            QtWidgets.QMessageBox.information(self, 'Login', f"Bem-vindo(a) de volta, {resultado['nome_completo']}!")
            from menu import Menu
            self.menu = Menu()
            self.menu.showMaximized()
            self.close()
        else:
            self.animar_erro_tremor()
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Usuário ou senha inválidos!')

        cursor.close()
        conexao.close()
