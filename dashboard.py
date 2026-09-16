import pymysql.cursors
from PyQt5 import QtWidgets, QtCore
from conexao import conectar  # Puxa a sua função padrão de conexão

def atualizar_dashboard(tela):
    """Busca os dados reais no MariaDB e preenche todos os indicadores da Home."""
    try:
        conexao = conectar()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        
        # 1. FATURAMENTO TOTAL (Soma de todos os totais da tabela pedido)
        cursor.execute("SELECT SUM(total) AS faturamento FROM pedido")
        res_fat = cursor.fetchone()
        faturamento = res_fat['faturamento'] if res_fat['faturamento'] else 0.0
        
        # Formata para Moeda Real (Ex: R$ 2.759,78)
        valor_fat_str = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tela.lblValorFat.setText(valor_fat_str)
        
        # 2. VENDAS CONCLUÍDAS (Contagem de pedidos)
        cursor.execute("SELECT COUNT(id_pedido) AS total_vendas FROM pedido")
        res_vendas = cursor.fetchone()
        total_vendas = res_vendas['total_vendas'] if res_vendas['total_vendas'] else 0
        tela.lblValorVendas.setText(str(total_vendas))
        
        # 3. TICKET MÉDIO (Faturamento dividido por total de vendas)
        ticket_medio = faturamento / total_vendas if total_vendas > 0 else 0.0
        valor_tk_str = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tela.lblValorTicket.setText(valor_tk_str)
        
        # 4. ITENS VENDIDOS (Soma de todas as quantidades na tabela item_pedido)
        cursor.execute("SELECT SUM(quantidade) AS total_itens FROM item_pedido")
        res_itens = cursor.fetchone()
        total_itens = res_itens['total_itens'] if res_itens['total_itens'] else 0
        tela.lblValorItens.setText(str(total_itens))
        
        # 5. PEDIDOS NA COZINHA (Pedidos pendentes)
        cursor.execute("SELECT COUNT(id_pedido) AS total_cozinha FROM pedido WHERE status = 'Pendente'")
        res_cozinha = cursor.fetchone()
        total_cozinha = res_cozinha['total_cozinha'] if res_cozinha['total_cozinha'] else 0
        tela.lblValorCoz.setText(f"{total_cozinha} ativos")
        
        # 6. PEDIDOS ATRASADOS (Pendente e com data de entrega menor que hoje)
        data_hoje = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        cursor.execute("SELECT COUNT(id_pedido) AS total_atrasados FROM pedido WHERE data_entrega < %s AND status = 'Pendente'", (data_hoje,))
        res_atrasados = cursor.fetchone()
        total_atrasados = res_atrasados['total_atrasados'] if res_atrasados['total_atrasados'] else 0
        tela.lblValorAtr.setText(str(total_atrasados))
        
        cursor.close()
        conexao.close()
        print("Métricas do Dashboard da confeitaria atualizadas com sucesso!")
    except Exception as e:
        print("Erro ao atualizar métricas do Dashboard:", e)
