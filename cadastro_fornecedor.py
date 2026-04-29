from PyQt5 import QtWidgets
from conexao import conectar


# ---------------- LIMPAR ----------------
def limpar(self):
    self.txt_nomeFornecedor.setText('')
    self.txt_cpfCnpj.setText('')
    self.txt_telefoneFornecedor.setText('')
    self.txt_emailFornecedor.setText('')
    self.txt_ruaFornecedor.setText('')
    self.txt_numFornecedor.setText('')
    self.txt_bairroFornecedor.setText('')
    self.txt_cidadeFornecedor.setText('')
    self.txt_complementoFornecedor.setText('')
    self.txt_infoAdicionais.clear()
    self.combo_tipoFornecedor.setCurrentIndex(0)


# ---------------- SALVAR ----------------
def salvar(self):
    nome = self.txt_nomeFornecedor.text()
    tipo = self.combo_tipoFornecedor.currentText()
    cpf_cnpj = self.txt_cpfCnpj.text()
    telefone = self.txt_telefoneFornecedor.text()
    email = self.txt_emailFornecedor.text()
    rua = self.txt_ruaFornecedor.text()
    numero = self.txt_numFornecedor.text()
    bairro = self.txt_bairroFornecedor.text()
    cidade = self.txt_cidadeFornecedor.text()
    complemento = self.txt_complementoFornecedor.text()
    info = self.txt_infoAdicionais.toPlainText()

    if not nome:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Nome é obrigatório')
        return

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    INSERT INTO fornecedor
    (nome, tipo, cpf_cnpj, telefone, email, rua, numero, bairro, cidade, complemento, informacoes)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    dados = (nome, tipo, cpf_cnpj, telefone, email, rua, numero, bairro, cidade, complemento, info)

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Fornecedor cadastrado!')
        limpar(self)
        atualizar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível salvar')


# ---------------- ATUALIZAR TABELA ----------------
def atualizar(self):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT id_fornecedor, nome, tipo, cpf_cnpj, telefone
    FROM fornecedor
    """
    cursor.execute(sql)

    resultado = cursor.fetchall()

    self.tableWidgetFornecedores.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetFornecedores.insertRow(row_num)
        for col_num, dado in enumerate(row_data):
            self.tableWidgetFornecedores.setItem(
                row_num, col_num,
                QtWidgets.QTableWidgetItem(str(dado))
            )

    self.tableWidgetFornecedores.resizeColumnsToContents()
    self.tableWidgetFornecedores.horizontalHeader().setStretchLastSection(True)


# ---------------- PESQUISA ----------------
def pesquisa(self):
    texto = self.lineEditPesquisaFornecedor.text()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT id_fornecedor, nome, tipo, cpf_cnpj, telefone
    FROM fornecedor
    WHERE nome LIKE %s OR cpf_cnpj LIKE %s
    """

    like = f"%{texto}%"
    cursor.execute(sql, (like, like))

    resultado = cursor.fetchall()

    self.tableWidgetFornecedores.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetFornecedores.insertRow(row_num)
        for col_num, dado in enumerate(row_data):
            self.tableWidgetFornecedores.setItem(
                row_num, col_num,
                QtWidgets.QTableWidgetItem(str(dado))
            )


# ---------------- BUSCAR POR ID ----------------
def buscar_por_id(self, id_fornecedor):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    SELECT nome, tipo, cpf_cnpj, telefone, email,
           rua, numero, bairro, cidade, complemento, informacoes
    FROM fornecedor
    WHERE id_fornecedor = %s
    """

    cursor.execute(sql, (id_fornecedor,))
    resultado = cursor.fetchone()

    if resultado:
        self.txt_nomeFornecedor.setText(resultado[0])
        self.combo_tipoFornecedor.setCurrentText(resultado[1])
        self.txt_cpfCnpj.setText(resultado[2])
        self.txt_telefoneFornecedor.setText(resultado[3])
        self.txt_emailFornecedor.setText(resultado[4])
        self.txt_ruaFornecedor.setText(resultado[5])
        self.txt_numFornecedor.setText(resultado[6])
        self.txt_bairroFornecedor.setText(resultado[7])
        self.txt_cidadeFornecedor.setText(resultado[8])
        self.txt_complementoFornecedor.setText(resultado[9])
        self.txt_infoAdicionais.setPlainText(resultado[10])

        self.id_fornecedor = id_fornecedor


# ---------------- EDITAR ----------------
def editar(self):
    if not hasattr(self, "id_fornecedor"):
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione um fornecedor')
        return

    nome = self.txt_nomeFornecedor.text()
    tipo = self.combo_tipoFornecedor.currentText()
    cpf_cnpj = self.txt_cpfCnpj.text()
    telefone = self.txt_telefoneFornecedor.text()
    email = self.txt_emailFornecedor.text()

    rua = self.txt_ruaFornecedor.text()
    numero = self.txt_numFornecedor.text()
    bairro = self.txt_bairroFornecedor.text()
    cidade = self.txt_cidadeFornecedor.text()
    complemento = self.txt_complementoFornecedor.text()

    info = self.txt_infoAdicionais.toPlainText()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = """
    UPDATE fornecedor
    SET nome=%s, tipo=%s, cpf_cnpj=%s, telefone=%s, email=%s, rua=%s,
        numero=%s, bairro=%s, cidade=%s, complemento=%s,informacoes=%s
        WHERE id_fornecedor=%s
    """

    dados = (
        nome, tipo, cpf_cnpj, telefone, email,
        rua, numero, bairro, cidade, complemento,
        info, self.id_fornecedor
    )

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Atualizado!')
        atualizar(self)
    else:
        QtWidgets.QMessageBox.warning(self, 'Aviso', 'Nenhuma alteração')


# ---------------- DELETAR ----------------
def deletar(self):
    if not hasattr(self, "id_fornecedor"):
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione um fornecedor')
        return

    confirm = QtWidgets.QMessageBox.question(
        self, 'Confirmar',
        'Deseja excluir este fornecedor?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )

    if confirm == QtWidgets.QMessageBox.No:
        return

    conexao = conectar()
    cursor = conexao.cursor()

    sql = "DELETE FROM fornecedor WHERE id_fornecedor = %s"
    cursor.execute(sql, (self.id_fornecedor,))
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Excluído!')
        limpar(self)
        atualizar(self)
        del self.id_fornecedor