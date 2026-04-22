from PyQt5 import uic, QtWidgets
from conexao import conectar

def salvar(self):
    nome = self.txt_nome.text()
    ingrediente = self.txt_ingrediente.text()
    preparo = self.txt_preparo.text()


    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO receitas(nome, ingrediente, preparo) VALUES (%s,%s,%s)'
    dados = (nome, ingrediente, preparo)

    conexao.commit()

    if cursor.rowcount > 0:
        print('Cadastro OK')
        QtWidgets.QMessageBox.information(self, 'Cadas', 'Cadastro realizado com sucesso!')

        self.txt_nome.setText('')
        self.txt_ingrediente.setText('')
        self.txt_preparo.setText('')

    else:
        QtWidgets.QMessageBox.information(self, 'Erro', 'Usuário não cadastrado')