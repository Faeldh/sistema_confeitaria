from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QDate
from conexao import conectar

# ---------------- SALVAR ----------------
def salvar(self):

    nome_produto = self.txt_produto.text()
    nome_categoria = self.combo_categoria.currentText() # Pega o texto da tela
    tamanho = self.txt_tamanho.text()
    preco = self.txt_preco.text().replace(',', '.') 
    descricao = self.txt_descricao.toPlainText()
    
    texto_ativo = self.combo_ativo.currentText()
    ativo = 1 if texto_ativo == "Sim" else 0

    if not nome_produto:
        QtWidgets.QMessageBox.warning(self, 'Erro', 'Produto é obrigatório')
        return

    conexao = conectar()
    cursor = conexao.cursor()

    try:
        # 1. BUSCAR O ID DA CATEGORIA NO BANCO DE DADOS
        cursor.execute("SELECT id_categoria FROM categoria WHERE nome = %s", (nome_categoria,))
        resultado_categoria = cursor.fetchone()

        # Verifica se a categoria foi encontrada
        if resultado_categoria:
            id_categoria = resultado_categoria[0] # Pega o número do ID
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', f'A categoria "{nome_categoria}" não está cadastrada no banco de dados!')
            return

        # 2. INSERIR O PRODUTO USANDO O ID DA CATEGORIA
        sql = 'INSERT INTO produto (nome, id_categoria, tamanho, preco, descricao, ativo) VALUES (%s, %s, %s, %s, %s, %s)'
        dados = (nome_produto, id_categoria, tamanho, preco, descricao, ativo)
        
        cursor.execute(sql, dados)
        conexao.commit()

        if cursor.rowcount > 0:
            print('cadastro OK')
            QtWidgets.QMessageBox.information(self, 'Cadastro', 'Cadastro realizado com sucesso')

            self.txt_produto.setText('')
            self.combo_categoria.setCurrentIndex(0)
            self.txt_tamanho.setText('')
            self.txt_preco.setText('')
            self.txt_sabores.clear()
            self.txt_descricao.clear()
            self.combo_ativo.setCurrentIndex(0)

        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', 'Não foi possível salvar') 
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Erro no Banco de Dados', str(e))

# ---------------- LIMPAR TELA ----------------
def limpar(self):
    """Limpa todos os campos do formulário e desmarca a tabela"""
    self.txt_produto.setText('')
    self.combo_categoria.setCurrentIndex(0)
    self.txt_tamanho.setText('')
    self.txt_preco.setText('')
    self.txt_sabores.clear()
    self.txt_descricao.clear()
    self.combo_ativo.setCurrentIndex(0)
    self.tableViewProdutos.clearSelection() # Remove seleção da tabela

# ---------------- LISTAR NA TABELA ----------------
def listar(self):
    """Busca os produtos no banco e preenche a tabela"""
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Faz um JOIN com a tabela de categorias para pegar o NOME da categoria e não apenas o ID
        sql = '''
            SELECT p.id_produto, p.nome, c.nome, p.tamanho, p.preco, p.ativo 
            FROM produto p
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria
        '''
        cursor.execute(sql)
        produtos = cursor.fetchall()
        
        # Zera a tabela antes de preencher
        self.tableViewProdutos.setRowCount(0)
        
        for linha, dados in enumerate(produtos):
            self.tableViewProdutos.insertRow(linha)
            
            # Tratamento dos dados para exibição
            id_prod = str(dados[0])
            nome = str(dados[1])
            categoria = str(dados[2]) if dados[2] else ""
            tamanho = str(dados[3]) if dados[3] else ""
            preco = f"R$ {dados[4]:.2f}".replace('.', ',') if dados[4] else ""
            sabores = "" # O banco usa uma tabela separada para sabores, deixaremos vazio na tabela por enquanto
            ativo = "Sim" if dados[5] == 1 else "Não"
            
            # Adiciona os itens nas colunas corretas (A coluna 5 é 'Sabores' e a 6 é 'Status')
            self.tableViewProdutos.setItem(linha, 0, QtWidgets.QTableWidgetItem(id_prod))
            self.tableViewProdutos.setItem(linha, 1, QtWidgets.QTableWidgetItem(nome))
            self.tableViewProdutos.setItem(linha, 2, QtWidgets.QTableWidgetItem(categoria))
            self.tableViewProdutos.setItem(linha, 3, QtWidgets.QTableWidgetItem(tamanho))
            self.tableViewProdutos.setItem(linha, 4, QtWidgets.QTableWidgetItem(preco))
            self.tableViewProdutos.setItem(linha, 5, QtWidgets.QTableWidgetItem(sabores))
            self.tableViewProdutos.setItem(linha, 6, QtWidgets.QTableWidgetItem(ativo))
            
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Erro', f'Erro ao carregar tabela: {e}')


# ---------------- PEGAR DADOS DA TABELA ----------------
def pegar_dados(self):
    """Ao clicar na tabela, preenche os campos da esquerda para edição"""
    linha = self.tableViewProdutos.currentRow()
    
    if linha != -1: # Verifica se há alguma linha selecionada
        id_produto = self.tableViewProdutos.item(linha, 0).text()
        
        conexao = conectar()
        cursor = conexao.cursor()
        
        # Busca os dados completos do produto específico, incluindo a descrição que não está na tabela
        sql = '''
            SELECT p.nome, c.nome, p.tamanho, p.preco, p.descricao, p.ativo 
            FROM produto p 
            LEFT JOIN categoria c ON p.id_categoria = c.id_categoria 
            WHERE p.id_produto = %s
        '''
        cursor.execute(sql, (id_produto,))
        produto = cursor.fetchone()
        
        if produto:
            self.txt_produto.setText(str(produto[0]))
            self.combo_categoria.setCurrentText(str(produto[1]) if produto[1] else "")
            self.txt_tamanho.setText(str(produto[2]) if produto[2] else "")
            self.txt_preco.setText(str(produto[3]).replace('.', ',') if produto[3] else "")
            self.txt_descricao.setText(str(produto[4]) if produto[4] else "")
            self.combo_ativo.setCurrentText("Sim" if produto[5] == 1 else "Não")


# ---------------- EDITAR ----------------
def editar(self):
    """Atualiza o produto selecionado"""
    linha = self.tableViewProdutos.currentRow()
    if linha == -1:
        QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um produto na tabela primeiro!')
        return
        
    id_produto = self.tableViewProdutos.item(linha, 0).text()
    
    nome_produto = self.txt_produto.text()
    nome_categoria = self.combo_categoria.currentText()
    tamanho = self.txt_tamanho.text()
    preco = self.txt_preco.text().replace(',', '.') 
    descricao = self.txt_descricao.toPlainText()
    ativo = 1 if self.combo_ativo.currentText() == "Sim" else 0
    
    conexao = conectar()
    cursor = conexao.cursor()
    
    try:
        # Busca ID da Categoria novamente
        cursor.execute("SELECT id_categoria FROM categoria WHERE nome = %s", (nome_categoria,))
        resultado_categoria = cursor.fetchone()
        
        if resultado_categoria:
            id_categoria = resultado_categoria[0]
        else:
            QtWidgets.QMessageBox.warning(self, 'Erro', f'Categoria "{nome_categoria}" não encontrada!')
            return
            
        sql = "UPDATE produto SET nome=%s, id_categoria=%s, tamanho=%s, preco=%s, descricao=%s, ativo=%s WHERE id_produto=%s"
        dados = (nome_produto, id_categoria, tamanho, preco, descricao, ativo, id_produto)
        
        cursor.execute(sql, dados)
        conexao.commit()
        
        QtWidgets.QMessageBox.information(self, 'Sucesso', 'Produto editado com sucesso!')
        listar(self) # Atualiza a tabela
        limpar(self) # Limpa os campos
        
    except Exception as e:
        QtWidgets.QMessageBox.warning(self, 'Erro', str(e))


# ---------------- EXCLUIR ----------------
def excluir(self):
    """Exclui o produto selecionado"""
    linha = self.tableViewProdutos.currentRow()
    if linha == -1:
        QtWidgets.QMessageBox.warning(self, 'Aviso', 'Selecione um produto na tabela primeiro!')
        return
        
    id_produto = self.tableViewProdutos.item(linha, 0).text()
    nome_produto = self.tableViewProdutos.item(linha, 1).text()
    
    # Pergunta de confirmação
    resposta = QtWidgets.QMessageBox.question(
        self, 'Confirmar Exclusão', 
        f'Tem certeza que deseja excluir o produto "{nome_produto}"?',
        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
    )
    
    if resposta == QtWidgets.QMessageBox.Yes:
        conexao = conectar()
        cursor = conexao.cursor()
        
        try:
            # Atenção: Se o produto estiver vinculado a itens de pedido, o banco pode dar erro de FK.
            cursor.execute("DELETE FROM produto WHERE id_produto = %s", (id_produto,))
            conexao.commit()
            
            QtWidgets.QMessageBox.information(self, 'Sucesso', 'Produto excluído!')
            listar(self)
            limpar(self)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Erro', f'Erro ao excluir: {e}')