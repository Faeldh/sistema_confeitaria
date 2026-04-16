from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar



def cadastrar(self):

    produto = self.txt_produto.text()
    categoria = self.comboBox
    tamanho = self.comboBox
    preco = self.txt_preco.text()
    sabores = self.txt_sabores.text()
    descricao = self.txt_descricao.text()
    status = self.txt_status.text()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO produtos( produto, categoria, tamanho, preco, sabores, descricao, status) VALUES (%s,%s,%s,%s,%s,%s,%s,)'
    dados = ( produto, categoria, tamanho, preco, sabores, descricao, status)
    cursor.excute(sql, dados)