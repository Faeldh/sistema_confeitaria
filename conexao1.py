from conexao import conectar

try:
    conexao = conectar()
    print("Conectou com sucesso!")
    conexao.close()
except Exception as erro:
    print("Erro ao conectar:", erro)