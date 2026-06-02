import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

def conectar_banco():
    return sqlite3.connect('estoque.db')

def inicializar_banco():
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nome TEXT NOT NULL,
            quantidade INTEGER DEFAULT 0,
            preco REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

# Garante que o banco e a tabela existam
inicializar_banco()

def obter_dados_comuns():
    """Função auxiliar para sempre buscar a lista e o valor total atualizados"""
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Busca produtos
    cursor.execute("SELECT * FROM produtos")
    lista_produtos = cursor.fetchall()
    
    # Calcula valor total
    cursor.execute("SELECT SUM(quantidade * preco) FROM produtos")
    resultado = cursor.fetchone()[0]
    valor_total_estoque = resultado if resultado is not None else 0.0
    
    conn.close()
    return lista_produtos, valor_total_estoque

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        id_produto = request.form.get('id_produto')
        codigo = request.form.get('codigo', '').strip()
        nome = request.form.get('nome', '').strip()
        
        try:
            quantidade = int(request.form.get('quantidade', '0'))
            preco = float(request.form.get('preco', '0.0'))
        except ValueError:
            quantidade = 0
            preco = 0.0
            
        if nome and codigo:
            conn = conectar_banco()
            cursor = conn.cursor()
            if id_produto:  # Modo Editar
                cursor.execute(
                    "UPDATE produtos SET codigo=?, nome=?, quantidade=?, preco=? WHERE id=?",
                    (codigo, nome, quantidade, preco, id_produto)
                )
            else:  # Modo Cadastrar
                cursor.execute(
                    "INSERT INTO produtos (codigo, nome, quantidade, preco) VALUES (?, ?, ?, ?)",
                    (codigo, nome,quantidade, preco) # corrigido internamente para a tupla correta
                )
                # Correção rápida do nome da variável inserida por segurança:
                cursor.execute(
                    "INSERT INTO produtos (codigo, nome, quantidade, preco) VALUES (?, ?, ?, ?)",
                    (codigo, nome, quantidade, preco)
                )
            conn.commit()
            conn.close()
        return redirect(url_for('index'))

    # Carregamento normal da página (Sem estar editando nada)
    lista_produtos, valor_total_estoque = obter_dados_comuns()
    return render_template(
        'index.html', 
        produtos=lista_produtos, 
        valor_total_estoque=valor_total_estoque, 
        produto_editar=None
    )

@app.route('/editar/<int:id_produto>')
def editar(id_produto):
    # Busca o produto específico que foi clicado para editar
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id=?", (id_produto,))
    produto = cursor.fetchone()
    conn.close()
    
    # Busca os dados da tabela e o valor total
    lista_produtos, valor_total_estoque = obter_dados_comuns()
    return render_template(
        'index.html', 
        produtos=lista_produtos, 
        valor_total_estoque=valor_total_estoque, 
        produto_editar=produto
    )

@app.route('/excluir/<int:id_produto>')
def excluir(id_produto):
    conn = conectar_banco()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id=?", (id_produto,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)