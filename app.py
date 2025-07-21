from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_super_secreta_123'  #Pode ser qualquer string

#Rota de login/logout
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        # Simples autenticação (pode trocar depois por banco de dados)
        if usuario == 'suporte' and senha == '1234':
            session['usuario'] = usuario
            return redirect('/')
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos')
    return render_template('login.html')

#Rota Principal
@app.route('/')
def index():
    if 'usuario' not in session:
        return redirect('/login')
    filtro = request.args.get('filtro', 'todos')
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()

    if filtro == 'abertos':
        cursor.execute("SELECT * FROM chamados WHERE status = 'Aberto'")
    elif filtro == 'resolvidos':
        cursor.execute("SELECT * FROM chamados WHERE status = 'Resolvido'")
    else:
        cursor.execute("SELECT * FROM chamados")

    chamados = cursor.fetchall()
    conn.close()
    return render_template('index.html', chamados=chamados, filtro=filtro)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

#Rota para criar chamado
@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        categoria = request.form['categoria']
        status = 'Aberto'
        conn = sqlite3.connect('chamados.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chamados (nome, descricao, categoria, status) VALUES (?, ?, ?, ?)",
                       (nome, descricao, categoria, status))
        conn.commit()
        conn.close()
        return redirect('/')
    return render_template('criar.html')

#Rota para status do chamado
@app.route('/resolver/<int:id>', methods=['POST'])
def resolver(id):
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE chamados SET status = 'Resolvido' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')


#Banco de dados
def init_db():
    conn = sqlite3.connect('chamados.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chamados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            descricao TEXT,
            categoria TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
