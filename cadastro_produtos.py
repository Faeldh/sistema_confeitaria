from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar


# ---------------- SALVAR ----------------
def salvar(self):

    produto = self.txt_produto.text()
    categoria = self.combo_categoria.currentText()
    tamanho = self.txt_tamanho.text()
    preco = self.txt_preco.text()
    sabores = self.txt_sabores.toPlainText()
    descricao = self.txt_descricao.toPlainText()
    status = self.combo_ativo.currentText()

    if not produto:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Produto é obrigatório')
        return

    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO produto( produto, categoria, tamanho, preco, sabores, descricao, status) VALUES (%s,%s,%s,%s,%s,%s,%s)'
    dados = ( produto, categoria, tamanho, preco, sabores, descricao, status)
    cursor.execute(sql, dados)

    cursor.commit()


    if cursor.rowcount > 0:
        print('cadastro OK')
        QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso')

        self.txt_produto.setText('')
        self.combo_categoria.currentText(0)
        self.txt_tamanho.setText('')
        self.txt_preco.setText()
        self.txt_sabores.seText()
        self.txt_descricao.stText()
        self.txt_status.text()

    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível salvar')    