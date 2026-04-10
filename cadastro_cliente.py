from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar
    

def atualizar(self):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT id, nome, cpf, telefone, email  FROM cliente'
    cursor.execute(sql)
    resultado = cursor.fetchall()

    self.tableWidgetClientes.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetClientes.insertRow(row_num)

        for col_num, dado in enumerate(row_data):
            self.tableWidgetClientes.setItem(
                row_num,
                col_num,
                QtWidgets.QTableWidgetItem(str(dado))
            )




def validar_cpf(cpf):
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    # 1º dígito
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10

    # 2º dígito
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f"{dig1}{dig2}"

def configurar_campos(self):
    # máscara CPF
    self.txt_cpf.setInputMask("000.000.000-00")

    # remover borda vermelha ao digitar
    self.txt_nome.textChanged.connect(lambda: self.txt_nome.setStyleSheet(""))
    self.txt_cpf.textChanged.connect(lambda: self.txt_cpf.setStyleSheet(""))
    
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

    self.txt_nome.setStyleSheet("")
    self.txt_cpf.setStyleSheet("")

    erros = []

    if not nome:
        erros.append("Nome")
        self.txt_nome.setStyleSheet("border: 2px solid red;")

    if not cpf:
        erros.append("CPF")
        self.txt_cpf.setStyleSheet("border: 2px solid red;")

    elif not validar_cpf(cpf):
        QtWidgets.QMessageBox.warning(self, 'Erro', 'CPF inválido!')
        self.txt_cpf.setStyleSheet("border: 2px solid red;")
        self.txt_cpf.setFocus()
        return

    if erros:
        mensagem = "Preencha os campos obrigatórios:\n- " + "\n- ".join(erros)
        QtWidgets.QMessageBox.warning(self, 'Atenção', mensagem)

        if not nome:
            self.txt_nome.setFocus()
        elif not cpf:
            self.txt_cpf.setFocus()

        return

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
