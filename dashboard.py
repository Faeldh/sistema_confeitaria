import pymysql.cursors
from PyQt5 import QtWidgets, QtCore, QtGui
from datetime import date
from conexao import conectar

# Configuração para integrar os gráficos do Matplotlib perfeitamente dentro do PyQt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def atualizar_dashboard(tela):
    """Busca os dados reais no MariaDB e preenche cartões e gráficos do Controle Financeiro."""
    try:
        conexao = conectar()
        cursor = conexao.cursor(pymysql.cursors.DictCursor)
        
        # ==================================================================
        # 1. CÁLCULO DOS CARDS DE VALORES (FLUXO DE CAIXA / PDV)
        # ==================================================================
        cursor.execute("SELECT SUM(total) AS faturamento FROM venda")
        res_fat = cursor.fetchone()
        faturamento = res_fat['faturamento'] if res_fat['faturamento'] else 0.0
        
        cursor.execute("SELECT COUNT(id_venda) AS total_vendas FROM venda")
        res_vendas = cursor.fetchone()
        total_vendas = res_vendas['total_vendas'] if res_vendas['total_vendas'] else 0
        
        ticket_medio = faturamento / total_vendas if total_vendas > 0 else 0.0
        
        query_itens = """
            SELECT SUM(ip.quantidade) AS total_itens 
            FROM venda v
            INNER JOIN item_pedido ip ON v.id_pedido = ip.id_pedido
        """
        cursor.execute(query_itens)
        res_itens = cursor.fetchone()
        total_itens = res_itens['total_itens'] if res_itens['total_itens'] else 0

        # Formata e preenche os cards na tela
        valor_fat_str = f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        valor_tk_str = f"R$ {ticket_medio:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        tela.lblValorFat.setText(valor_fat_str)
        tela.lblValorVendas.setText(str(total_vendas))
        tela.lblValorTicket.setText(valor_tk_str)
        tela.lblValorItens.setText(str(total_itens))
        
        # ==================================================================
        # 2. CÁLCULO DOS CARDS DE PRODUÇÃO (FLUXO DA COZINHA)
        # ==================================================================
        cursor.execute("SELECT COUNT(id_pedido) AS total_cozinha FROM pedido WHERE status = 'Pendente'")
        res_cozinha = cursor.fetchone()
        total_cozinha = res_cozinha['total_cozinha'] if res_cozinha['total_cozinha'] else 0
        tela.lblValorCoz.setText(f"{total_cozinha} ativos")
        
        data_hoje = date.today().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(id_pedido) AS total_atrasados FROM pedido WHERE data_entrega < %s AND status = 'Pendente'", (data_hoje,))
        res_atrasados = cursor.fetchone()
        total_atrasados = res_atrasados['total_atrasados'] if res_atrasados['total_atrasados'] else 0
        tela.lblValorAtr.setText(str(total_atrasados))
        
        # ==================================================================
        # 3. GERAÇÃO DOS GRÁFICOS REAIS (CAIXAS INFERIORES)
        # ==================================================================
        query_grafico_financeiro = """
            SELECT data_venda, SUM(total) AS total_dia 
            FROM venda 
            GROUP BY data_venda 
            ORDER BY data_venda ASC 
            LIMIT 7
        """
        cursor.execute(query_grafico_financeiro)
        dados_financeiros = cursor.fetchall()
        
        datas = [d['data_venda'].strftime("%d/%m") for d in dados_financeiros] if dados_financeiros else ["Sem dados"]
        valores_dias = [float(d['total_dia']) for d in dados_financeiros] if dados_financeiros else [0.0]
        
        __import__('dashboard').renderizar_grafico_barras(tela.cardLargeResumo, datas, valores_dias)

        query_mais_vendidos = """
            SELECT prod.nome AS produto, SUM(ip.quantidade) AS qtd 
            FROM venda v
            INNER JOIN item_pedido ip ON v.id_pedido = ip.id_pedido
            INNER JOIN produto prod ON ip.id_produto = prod.id_produto
            GROUP BY prod.id_produto
            ORDER BY qtd DESC
            LIMIT 5
        """
        cursor.execute(query_mais_vendidos)
        dados_produtos = cursor.fetchall()
        
        nomes_produtos = [p['produto'] for p in dados_produtos] if dados_produtos else ["Sem dados"]
        quantidades = [int(p['qtd']) for p in dados_produtos] if dados_produtos else [0]
        
        __import__('dashboard').renderizar_grafico_pizza(tela.cardLargeMaisVendidos, nomes_produtos, quantidades)

        cursor.close()
        conexao.close()
        print("Métricas e gráficos do Dashboard atualizados com sucesso!")
        
    except Exception as e:
        print("Erro ao atualizar o Dashboard:", e)

def renderizar_grafico_barras(widget_pai, labels, valores):
    """🟢 RESOLVIDO: Gera um lindo gráfico de linhas/evolução baseado no IPCA do IBGE"""
    if widget_pai.layout() is None:
        QtWidgets.QVBoxLayout(widget_pai)
    else:
        while widget_pai.layout().count():
            item = widget_pai.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    fig = Figure(figsize=(5, 3.5), dpi=100)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    
    # 🟢 NOVO DESIGN DE LINHA: Desenha a linha de evolução verde com marcadores redondos vermelhos (igual ao print!)
    ax.plot(labels, valores, color='#3F4A2F', linestyle='-', linewidth=2, marker='o', markersize=6, markerfacecolor='#991B1B', markeredgecolor='#991B1B')
    
    ax.set_title("Evolução do Faturamento por Período", fontsize=11, fontweight='bold', color='#2E3723', pad=15)
    
    # Grade de fundo cinza clara pontilhada para dar profundidade de nota fiscal
    ax.grid(axis='both', linestyle='--', alpha=0.4, color='#CBD5E1')
    ax.set_axisbelow(True) 
    
    # Limpa as bordas da caixa deixando o gráfico flutuante e chique
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#E2E8F0')
    ax.spines['bottom'].set_color('#E2E8F0')
    ax.tick_params(axis='both', colors='#475569', labelsize=9)
    
    # Adiciona os rótulos de valores flutuando acima de cada pontinho redondo da linha
    for i, txt in enumerate(valores):
        ax.annotate(f'R$ {txt:.2f}'.replace('.', ','),
                    (labels[i], valores[i]),
                    textcoords="offset points", 
                    xytext=(0, 8), 
                    ha='center', fontsize=8, color='#334155', weight='bold')

    fig.tight_layout()
    widget_pai.layout().addWidget(canvas)

def renderizar_grafico_pizza(widget_pai, labels, quantidades):
    """Gera um gráfico de rosca moderno com a porcentagem destacada e limpa no centro"""
    if widget_pai.layout() is None:
        QtWidgets.QVBoxLayout(widget_pai)
    else:
        while widget_pai.layout().count():
            item = widget_pai.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    fig = Figure(figsize=(5, 3.5), dpi=100)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    
    cores = ['#3F4A2F', '#CBB074', '#556442', '#E6D2A2', '#708259']
    
    wedges, texts = ax.pie(
        quantidades, labels=labels, startangle=90, 
        colors=cores[:len(labels)], wedgeprops=dict(width=0.35, edgecolor='w', linewidth=2.5)
    )
    
    total = sum(quantidades)
    if total > 0:
        porcentagem_principal = (quantidades[0] / total) * 100
        texto_centro = f"{porcentagem_principal:.0f}%"
    else:
        texto_centro = "0%"
        
    ax.text(0, 0, texto_centro, ha='center', va='center', fontsize=20, fontweight='bold', color='#334155')
    
    ax.set_title("Top Produtos Mais Vendidos", fontsize=11, fontweight='bold', color='#2E3723', pad=15)
    for t in texts: 
        t.set_color('#475569')
        t.set_fontsize(9)
    
    ax.axis('equal')
    fig.tight_layout()
    widget_pai.layout().addWidget(canvas)
