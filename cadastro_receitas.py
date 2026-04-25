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

    atualizar(self)


def editar(self):
    if not hasattr(self, 'id_receita'):
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione uma receita na tabela')
        return
    
    nome = self.txt_nomeReceita.text()
    ingrediente = self.txt_ingredientes.toPlainText()
    preparo = self.txt_modoPreparo.toPlainText()

    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'UPDATE receitas SET nome =%s, ingrediente=%s, preparo=%s WHERE id=%s'

    dados = (nome, ingrediente, preparo)

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Receitas atualizado com sucesso')


        atualizar(self)
    
    else:
        QtWidgets.QMessageBox.waning(self, "Aviso", 'Nenhuma alteração foi feita')
    
    atualizar(self)
    

def atualizar(self):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT id, nome FROM receitas'
    cursor.execute(sql)
    resultado = cursor.fetchall()

    self.tableWidgetReceitas.setRowCount(0)

    for row_num, row_data in enumerate(resultado):
        self.tableWidgetReceitas.insertRow(row_num)

        for col_num, dado in enumerate(row_data):
            self.tableWidgetReceitas.setItem(
                row_num,
                col_num,
                QtWidgets.QTableWidgetItem(str(dado))
            )
    self.tableWidgetClientes.resizeColumnsToContents()
    self.tableWidgetClientes.horizontalHeader().setStretchLastSection(True)      

def buscar_por_id(self, id_receita):
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT nome, ingrediente, preparo FROM receitas WHERE id = %s'

    cursor.execute(sql, (id_receita))
    resultado = cursor.fetchone()

    if resultado:
        nome = self.txt_nomeReceita.setText(resultado[0])
        ingrediente = self.txt_ingredientes.setText(resultado[1])
        preparo = self.txt_modoPreparo.setText(resultado[2])

        self.id_receita = id_receita

