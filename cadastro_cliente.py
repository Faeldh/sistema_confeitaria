from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar


        #self.btn_salvar.clicked.connect(self.salvar)
        #self.btn_excluir.clicked.connect(self.excluir)
        #self.btn_editar.clicked.connect(self.editar)
    
def salvar(self):
    nome = self.txt_nome.text()
    telefone = self.txt_telefone.text()
    data = self.dateEditNascimento.date()
    data_format = data.toString('yyyy-MM-dd')
    cpf = self.txt_cpf.text().replace(".", "").replace("-", "")
    cep = self.txt_cep.text().replace(".", "").replace("-", "")
    rua = self.txt_rua.text()
    bairro = self.txt_bairro.text()
    n = self.txt_n.text()
    complemento = self.txt_complemento.text()
    cidade = self.txt_cidade.text()
    email = self.txt_email.text()
    observcoes = self.txt_obs.toPlainText()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO cliente(nome, telefone, data_format,cpf, cep, rua, bairro, n, complemento, cidade, email, observcoes) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    dados = (nome, telefone, data_format,cpf, cep, rua, bairro, n, complemento,cidade, email, observcoes)
    cursor.execute(sql, dados)

    conexao.commit()

    if cursor.rowcount > 0:
        print("Cadastro OK")
        QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso!')

        self.txt_nome.setText('')
        self.txt_telefone.setText('')
        self.dateEditNascimento.setDate(QDate.currentDate())
        self.txt_cpf.setText('')
        self.txt_cep.setText('')
        self.txt_rua.setText('')
        self.txt_bairro.setText('')
        self.txt_n.setText('')
        self.txt_complemento.setText('')
        self.txt_cidade.setText('')
        self.txt_email.setText('')
        self.txt_obs.clear()


    else:
        QtWidgets.QMessageBox.information(self, 'Erro', 'Usuário não cadastrado')
