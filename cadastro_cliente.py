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
        data = self.dateEditNascimento.date()
        data_format = data.toString()
        cpf = self.txt_cpf.text().replace(".", "").replace("-", "")
        cep = self.txt_cep.text().replace(".", "").replace("-", "")
        rua = self.txt_rua.text()
        bairro = self.txt_bairro.text()
        n = self.txt_n.text()
        complemento = self.txt_complemento.text()
        cidade = self.txt_cidade.text()
        email = self.txt_email.text()
        observacoes = self.txt_obs.text()

        conexao = conectar()
        cursor = conexao.cursor()

        sql = 'INSERT INTO cliente(nome, telefone, data_format,cpf, cep, rua, bairro, n, complemento, cidade, email, observacoes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

        dados = (nome, telefone, data_format,cpf, cep, rua, bairro, n, complemento,cidade, email, observacoes)
        cursor.execute(sql, dados)
        resultado = cursor.fetchone()
        print("Resultado do banco:", resultado)

        if resultado:
            print("Login OK")
            QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso!')

            from menu import Menu

            self.menu = Menu()
            self.menu.show()

            self.close()

        else:
            QtWidgets.QMessageBox.information(self, 'Erro', 'Usuário não cadastrado')

        conexao.commit()
