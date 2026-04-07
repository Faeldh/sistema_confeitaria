import pymysql

def conectar():
    try:
        print("🔄 Conectando com PyMySQL...")

        conexao = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='db_confeitaria',
            port=3306
        )

        print("✅ Conectado com sucesso!")
        return conexao

    except Exception as erro:
        print("❌ Erro ao conectar:", erro)
        raise