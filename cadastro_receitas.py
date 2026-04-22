from PyQt5 import uic, QtWidgets
from conexao import conectar

def salvar(self):
    nome = self.txt_nomeReceita.text()
    ingrediente = self.txt_ingredientes.text()
    preparo = self.txt_modoPreparo.text()


    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'INSERT INTO receitas(nome, ingrediente, preparo) VALUES (%s,%s,%s)'
    dados = (nome, ingrediente, preparo)

    conexao.commit()

    if cursor.rowcount > 0:
        print('Cadastro OK')
        QtWidgets.QMessageBox.information(self, 'Cadas', 'Cadastro realizado com sucesso!')

        self.txt_nomeReceita.setText('')
        self.txt_ingredientes.setText('')
        self.txt_modoPreparo.setText('')

    else:
        QtWidgets.QMessageBox.information(self, 'Erro', 'Usuário não cadastrado')