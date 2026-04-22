from PyQt5 import uic, QtWidgets
from conexao import conectar

def salvar(self):
    nome = self.txt_nomeReceita.text()
    ingrediente = self.txt_ingredientes.toPlainText()
    preparo = self.txt_modoPreparo.toPlainText()


    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO receitas(nome, ingrediente, preparo) VALUES (%s,%s,%s)'
    dados = (nome, ingrediente, preparo)

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        print('Cadastro OK')
        QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso!')

        self.txt_nomeReceita.setText('')
        self.txt_ingredientes.setText('')
        self.txt_modoPreparo.setText('')

    else:
        QtWidgets.QMessageBox.information(self, 'Erro', 'Usuário não cadastrado')