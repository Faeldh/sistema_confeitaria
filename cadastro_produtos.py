from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar



def cadastrar(self):

    produto = self.txt_produto.text()
    categoria = self.comboBox.currentText()
    tamanho = self.comboBox.currentText()
    preco = self.txt_preco.text()
    sabores = self.txt_sabores.text()
    descricao = self.txt_descricao.text()
    status = self.txt_status.text()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO produtos( produto, categoria, tamanho, preco, sabores, descricao, status) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    dados = ( produto, categoria, tamanho, preco, sabores, descricao, status)
    cursor.execute(sql, dados)

    cursor.commit()


    if cursor.rowcount > 0:
        print('cadastro OK')
        QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso')

        self.txt_produto.setText('')
        self.comboBox.currentText(0)
        self.comboBoxcurrentText(0)
        self.txt_preco.setText()
        self.txt_sabores.seText()
        self.txt_descricao.stText()
        self.txt_status.text()