import mysql.connector

print("TESTE DIRETO...")

conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    port=3306,
    connection_timeout=5
)

print("CONECTOU!")