from PyQt5 import uic, QtWidgets
from conexao import conectar



def salvar(self):
    nome = self.txt_nomeReceita.text()
    ingrediente = self.txt_ingredientes.toPlainText()
    preparo = self.txt_modoPreparo.toPlainText()

    self.txt_nomeReceita.setStyleSheet("")
    self.txt_ingredientes.setStyleSheet("")
    self.txt_modoPreparo.setStyleSheet("")

    erros = []

    if not nome:
        erros.append("Nome da receita é obrigatório")
        self.txt_nomeReceita.setStyleSheet("border: 2px solid red;")

    if not ingrediente:
        erros.append("Ingredientes são obrigatórios")
        self.txt_ingredientes.setStyleSheet("border: 2px solid red;")

    if not preparo:
        erros.append("Modo de preparo é obrigatório")
        self.txt_modoPreparo.setStyleSheet("border: 2px solid red;")

    # Se tiver erro, para tudo aqui
    if erros:
        QtWidgets.QMessageBox.warning(self, 'Erro', '\n'.join(erros))
        self.txt_nomeReceita.setStyleSheet("border: 2px solid red;")
        self.txt_ingredientes.setStyleSheet("border: 2px solid red;")
        self.txt_modoPreparo.setStyleSheet("border: 2px solid red;")

        return

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

    dados = (nome, ingrediente, preparo, self.id_receita)

    cursor.execute(sql, dados)
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Receitas atualizado com sucesso')


        atualizar(self)
    
    else:
        QtWidgets.QMessageBox.warning(self, "Aviso", 'Nenhuma alteração foi feita')
    
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


    header = self.tableWidgetReceitas.horizontalHeader()

    #header.setStretchLastSection(True)
    # Coluna 0 = ID (pequena)
    header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
    # Coluna 1 = Nome (ocupa o resto)
    header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)    

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


def pesquisar(self):
    pesquisa = self.txt_pesquisaReceita.text().strip()
    
    conexao = conectar()
    cursor = conexao.cursor()

    sql = 'SELECT id, nome FROM receitas WHERE id LIKE %s OR nome LIKE %s'

    like = f'%{pesquisa}'
    cursor.execute(sql, (like, like))

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

def deletar(self):
    if not hasattr(self, "id_receita"):
        QtWidgets.QMessageBox.warning(self, 'Atenção', 'Selecione uma receita para excluir')
        return

    
    confirmacao = QtWidgets.QMessageBox.question(
        self,
        'Confirmar exclusão',
        'Tem certeza que deseja excluir este receita?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )

    if confirmacao == QtWidgets.QMessageBox.No:
        return

    conexao = conectar()
    cursor = conexao.cursor()

    sql = "DELETE FROM receitas WHERE id = %s"
    cursor.execute(sql, (self.id_receita,))
    conexao.commit()

    if cursor.rowcount > 0:
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Receita excluído com sucesso!')

        
        self.txt_nomeReceita.setText('')
        self.txt_ingredientes.setText('')
        self.txt_modoPreparo.setText('')


        # remove ID (IMPORTANTE)
        del self.id_receita

        
        atualizar(self)

    else:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível excluir')  


def limpar(self):
        self.txt_nomeReceita.setText('')
        self.txt_ingredientes.setText('')
        self.txt_modoPreparo.setText('')
    
def pesquisar(self):
    pesquisa = self.txt_pesquisaReceita.text().strip()
    like = f"%{pesquisa.lower()}%"

    conexao = conectar()
    cursor = conexao.cursor()

    sql =  'SELECT id, nome FROM receitas WHERE id LIKE %s OR nome LIKE %s'
    cursor.execute(sql, (like, like))

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