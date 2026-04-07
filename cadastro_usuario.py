from PyQt5 import uic, QtWidgets
from conexao import conectar

class cadastro(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_salvar.clicked.connect(self.salvar)
        #self.btn_excluir.clicked.connect(self.excluir)
        #self.btn_editar.clicked.connect(self.editar)
    
    def salvar(self):
        nome = self.txt_nome.text()
        telefone = self.txt_telefone.text()
        data_nascimento = self.txt_data.text()
        cep = self.txt_cep.text()
        rua = self.txt_rua.text()
        bairro = self.txt_bairro.text()
        n = self.txt_n.text()
        complemento = self.txt_complemento.text()
        email = self.txt_email.text()
        observacoes = self.txt_obs.text()

        conexao = conectar()
        cursor = conexao.cursor()

        sql = 'INSERT INTO cliente(nome, telefone, cep, rua, bairro, n, complemento, email, observacoes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)'

        dados = (nome, telefone, cep, rua, bairro, n, complemento, email, observacoes)
        cursor.execute(sql, dados)

        conexao.commit()
