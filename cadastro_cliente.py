from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar


def pesquisa(self):

    pesquisa = self.txt_pesquisa.text().strip()

    conexao = conectar()
    cursor = conexao.cursor()
    
    sql = 'SELECT id, nome, cpf FROM cliente WHERE nome LIKE %s OR cpf LIKE %s'

    like = f'%{pesquisa}'
    cursor.execute(sql, (like, like))

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
    
def buscar_por_id(self, id_cliente):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT nome, telefone, cpf, data_format, cep, rua, bairro, n, complemento, cidade, email, observcoes
    FROM cliente
    WHERE id = %s
    """

    cursor.execute(sql, (id_cliente,))
    resultado = cursor.fetchone()

    if resultado:
        self.txt_nome.setText(resultado[0])
        self.txt_telefone.setText(resultado[1])
        self.txt_cpf.setText(resultado[2])

        from PyQt5.QtCore import QDate

        data = resultado[3]

        if isinstance(data, (str,)):
            data_convertida = QDate.fromString(data, 'yyyy-MM-dd')
            self.dateEditNascimento.setDate(data_convertida)

        elif data:  # datetime.date
            self.dateEditNascimento.setDate(
                QDate(data.year, data.month, data.day)
            )

        self.txt_cep.setText(resultado[4])
        self.txt_rua.setText(resultado[5])
        self.txt_bairro.setText(resultado[6])
        self.txt_n.setText(resultado[7])
        self.txt_complemento.setText(resultado[8])
        self.txt_cidade.setText(resultado[9])
        self.txt_email.setText(resultado[10])
        self.txt_obs.setPlainText(resultado[11])

        self.id_cliente = id_cliente

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
    self.tableWidgetClientes.resizeColumnsToContents()
    self.tableWidgetClientes.horizontalHeader().setStretchLastSection(True)

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

def editar(self):
    if not hasattr(self, "id_cliente"):
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione um cliente na tabela')
        return

    nome = self.txt_nome.text().strip()
    telefone = self.txt_telefone.text()
    cpf = self.txt_cpf.text().replace(".", "").replace("-", "")
    email = self.txt_email.text()
    cidade = self.txt_cidade.text()
    observcoes = self.txt_obs.toPlainText()

    # data
    data = self.dateEditNascimento.date()
    data_format = data.toString('yyyy-MM-dd')

    if not nome or not cpf:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Nome e CPF são obrigatórios')
        return

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE cliente
    SET nome=%s, telefone=%s, cpf=%s, data_format=%s,
        cidade=%s, email=%s, observcoes=%s
    WHERE id=%s
    """

    dados = (nome, telefone, cpf, data_format, cidade, email, observcoes, self.id_cliente)

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Cliente atualizado com sucesso!')

        # 🔥 atualiza tabela automaticamente
        atualizar(self)

    else:
        QtWidgets.QMessageBox.warning(self, 'Aviso', 'Nenhuma alteração foi feita')

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
