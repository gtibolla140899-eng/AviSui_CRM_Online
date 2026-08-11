from flask import Flask, request, redirect, render_template_string
import sqlite3
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
BANCO = Path(__file__).parent / "avisui_crm.db"

def conectar():
    conn = sqlite3.connect(BANCO)
    conn.row_factory = sqlite3.Row
    return conn

def preparar_banco():
    conn = conectar()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS combustivel (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            quilometragem REAL DEFAULT 0,
            posto TEXT,
            cidade TEXT,
            litros REAL DEFAULT 0,
            media REAL DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS alimentacao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            documento TEXT,
            razao_social TEXT,
            conta_contabil TEXT,
            valor REAL DEFAULT 0,
            valor_a_mais REAL DEFAULT 0,
            descricao TEXT
        )
    """)

    conn.commit()
    conn.close()

preparar_banco()

HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AviSui CRM</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#111;color:#fff;font-family:Arial,sans-serif}
.header{background:#1c1c1c;padding:20px;text-align:center;border-bottom:2px solid #d71920}
.logo{font-size:28px;font-weight:bold}
.subtitulo{color:#aaa;margin-top:5px}
.container{padding:18px;max-width:700px;margin:auto}
.card{background:#1c1c1c;border:1px solid #333;border-radius:14px;padding:20px;margin-bottom:18px}
.titulo{font-size:21px;font-weight:bold;margin-bottom:18px}
.menu{display:grid;gap:12px}
.menu a{display:block;text-decoration:none;background:#292929;color:#fff;padding:17px;border-radius:10px;font-weight:bold;border:1px solid #444}
.menu a:hover{background:#333}
label{display:block;color:#bbb;font-size:14px;font-weight:bold;margin-top:14px;margin-bottom:6px}
input,select,textarea{width:100%;padding:14px;border:1px solid #444;border-radius:9px;background:#292929;color:#fff;font-size:16px}
textarea{min-height:90px;resize:vertical}
button,.botao{display:block;width:100%;padding:16px;margin-top:20px;border:none;border-radius:10px;background:#d71920;color:#fff;font-size:17px;font-weight:bold;text-align:center;text-decoration:none}
.voltar{background:#444}
.sucesso{background:#174d2b;border:1px solid #287a45;padding:15px;border-radius:10px;margin-bottom:18px}
.tabela{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:10px;border-bottom:1px solid #333;text-align:left;white-space:nowrap}
th{color:#ddd}
.info{color:#bbb;font-size:14px;line-height:1.6}
.filtros{display:grid;gap:10px}
.total{font-size:18px;font-weight:bold;margin:15px 0}
</style>
</head>
<body>

<div class="header">
<div class="logo">AviSui CRM</div>
<div class="subtitulo">Equipamentos para avicultura e suinocultura</div>
</div>

<div class="container">

{% if sucesso %}
<div class="sucesso">✓ Registro salvo com sucesso!</div>
{% endif %}

<div class="card">
<div class="titulo">{{ titulo }}</div>

{% if pagina == 'inicio' %}
<div class="menu">
<a href="/visita">📝 Registrar Visita</a>
<a href="/combustivel">⛽ Combustível</a>
<a href="/alimentacao">🍽️ Alimentação</a>
<a href="/relatorio/clientes">👥 Clientes Cadastrados</a>
<a href="/relatorio/visitas">📋 Relatório Completo de Visitas</a>
<a href="/relatorio/combustivel">⛽ Relatório de Combustível</a>
<a href="/relatorio/alimentacao">🍽️ Relatório de Alimentação</a>
</div>

{% elif pagina == 'visita' %}
<form method="POST" action="/visita">
<label>Data</label>
<input type="text" name="data" value="{{ hoje }}" required>
<label>Vendedor</label>
<input type="text" name="vendedor" value="Guilherme Tibolla">
<label>Cliente</label>
<select name="cliente" required>
<option value="">Selecione o cliente</option>
{% for c in clientes %}
<option value="{{ c['nome'] }}">{{ c['nome'] }}</option>
{% endfor %}
</select>
<label>Granja</label><input name="granja">
<label>Cidade</label><input name="cidade">
<label>Hora de saída</label><input type="time" name="hora_saida">
<label>Hora de chegada</label><input type="time" name="hora_chegada">
<label>KM inicial</label><input type="number" step="0.1" name="km_inicial">
<label>KM final</label><input type="number" step="0.1" name="km_final">
<label>Atividade realizada</label><textarea name="atividade"></textarea>
<label>Observações</label><textarea name="observacoes"></textarea>
<button>SALVAR VISITA</button>
</form>

{% elif pagina == 'combustivel' %}
<form method="POST" action="/combustivel">
<label>Data</label>
<input type="text" name="data" value="{{ hoje }}" required>
<label>Quilometragem</label>
<input type="number" step="0.1" name="quilometragem" required>
<label>Nome do posto</label>
<input type="text" name="posto">
<label>Cidade</label>
<input type="text" name="cidade">
<label>Litros</label>
<input type="number" step="0.01" name="litros">
<label>Média</label>
<input type="number" step="0.01" name="media">
<button>SALVAR COMBUSTÍVEL</button>
</form>

{% elif pagina == 'alimentacao' %}
<form method="POST" action="/alimentacao">
<label>Data</label>
<input type="text" name="data" value="{{ hoje }}" required>
<label>Número do documento</label>
<input type="text" name="documento">
<label>Razão social do fornecedor</label>
<input type="text" name="razao_social">
<label>Conta contábil</label>
<input type="text" name="conta_contabil">
<label>Valor</label>
<input type="number" step="0.01" name="valor">
<label>Valor a mais</label>
<input type="number" step="0.01" name="valor_a_mais">
<label>Descrição</label>
<textarea name="descricao"></textarea>
<button>SALVAR ALIMENTAÇÃO</button>
</form>

{% elif pagina == 'clientes' %}
<div class="tabela">
<table>
<tr><th>Cliente</th></tr>
{% for c in registros %}
<tr><td>{{ c['nome'] }}</td></tr>
{% else %}
<tr><td>Nenhum cliente cadastrado.</td></tr>
{% endfor %}
</table>
</div>

{% elif pagina in ['visitas_rel','combustivel_rel','alimentacao_rel'] %}
<form method="GET" class="filtros">
<label>Data inicial</label>
<input type="text" name="inicio" value="{{ inicio }}">
<label>Data final</label>
<input type="text" name="fim" value="{{ fim }}">
<button>FILTRAR</button>
</form>

<div class="tabela">
<table>

{% if pagina == 'visitas_rel' %}
<tr><th>Data</th><th>Vendedor</th><th>Cliente</th><th>Granja</th><th>Cidade</th><th>KM inicial</th><th>KM final</th><th>Atividade</th><th>Observações</th></tr>
{% for r in registros %}
<tr>
<td>{{ r['data'] }}</td><td>{{ r['vendedor'] }}</td><td>{{ r['cliente'] }}</td>
<td>{{ r['granja'] }}</td><td>{{ r['cidade'] }}</td>
<td>{{ r['km_inicial'] }}</td><td>{{ r['km_final'] }}</td>
<td>{{ r['atividade'] }}</td><td>{{ r['observacoes'] }}</td>
</tr>
{% endfor %}

{% elif pagina == 'combustivel_rel' %}
<tr><th>Data</th><th>Quilometragem</th><th>Posto</th><th>Cidade</th><th>Litros</th><th>Média</th></tr>
{% for r in registros %}
<tr><td>{{ r['data'] }}</td><td>{{ r['quilometragem'] }}</td><td>{{ r['posto'] }}</td><td>{{ r['cidade'] }}</td><td>{{ r['litros'] }}</td><td>{{ r['media'] }}</td></tr>
{% endfor %}

{% elif pagina == 'alimentacao_rel' %}
<tr><th>Data</th><th>Documento</th><th>Razão Social</th><th>Conta</th><th>Valor</th><th>Valor a mais</th><th>Descrição</th></tr>
{% for r in registros %}
<tr><td>{{ r['data'] }}</td><td>{{ r['documento'] }}</td><td>{{ r['razao_social'] }}</td><td>{{ r['conta_contabil'] }}</td><td>{{ r['valor'] }}</td><td>{{ r['valor_a_mais'] }}</td><td>{{ r['descricao'] }}</td></tr>
{% endfor %}
{% endif %}

</table>
</div>
{% endif %}

{% if pagina != 'inicio' %}
<a class="botao voltar" href="/">← VOLTAR AO PAINEL</a>
{% endif %}

</div>
</div>
</body>
</html>
"""

def render(pagina, titulo, sucesso=False, **dados):
    return render_template_string(
        HTML,
        pagina=pagina,
        titulo=titulo,
        sucesso=sucesso,
        hoje=datetime.now().strftime("%d/%m/%Y"),
        **dados
    )

@app.route("/")
def inicio():
    return render("inicio", "Painel de Controle")

@app.route("/visita", methods=["GET","POST"])
def visita():
    conn=conectar()
    clientes=conn.execute("SELECT nome FROM clientes ORDER BY nome").fetchall()
    if request.method=="POST":
        conn.execute("""
        INSERT INTO visitas
        (data,vendedor,cliente,granja,cidade,hora_saida,hora_chegada,km_inicial,km_final,atividade,observacoes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """,(
            request.form.get("data",""),
            request.form.get("vendedor",""),
            request.form.get("cliente",""),
            request.form.get("granja",""),
            request.form.get("cidade",""),
            request.form.get("hora_saida",""),
            request.form.get("hora_chegada",""),
            request.form.get("km_inicial") or 0,
            request.form.get("km_final") or 0,
            request.form.get("atividade",""),
            request.form.get("observacoes","")
        ))
        conn.commit()
        conn.close()
        return redirect("/visita?ok=1")
    conn.close()
    return render("visita","Registrar Visita",sucesso=request.args.get("ok")=="1",clientes=clientes)

@app.route("/combustivel", methods=["GET","POST"])
def combustivel():
    if request.method=="POST":
        conn=conectar()
        conn.execute("""
        INSERT INTO combustivel
        (data,quilometragem,posto,cidade,litros,media)
        VALUES (?,?,?,?,?,?)
        """,(
            request.form.get("data",""),
            request.form.get("quilometragem") or 0,
            request.form.get("posto",""),
            request.form.get("cidade",""),
            request.form.get("litros") or 0,
            request.form.get("media") or 0
        ))
        conn.commit()
        conn.close()
        return redirect("/combustivel?ok=1")
    return render("combustivel","⛽ Registrar Combustível",sucesso=request.args.get("ok")=="1")

@app.route("/alimentacao", methods=["GET","POST"])
def alimentacao():
    if request.method=="POST":
        conn=conectar()
        conn.execute("""
        INSERT INTO alimentacao
        (data,documento,razao_social,conta_contabil,valor,valor_a_mais,descricao)
        VALUES (?,?,?,?,?,?,?)
        """,(
            request.form.get("data",""),
            request.form.get("documento",""),
            request.form.get("razao_social",""),
            request.form.get("conta_contabil",""),
            request.form.get("valor") or 0,
            request.form.get("valor_a_mais") or 0,
            request.form.get("descricao","")
        ))
        conn.commit()
        conn.close()
        return redirect("/alimentacao?ok=1")
    return render("alimentacao","🍽️ Registrar Alimentação",sucesso=request.args.get("ok")=="1")

def periodo(tabela, inicio, fim):
    conn=conectar()
    if inicio and fim:
        registros=conn.execute(
            f"SELECT * FROM {tabela} WHERE data >= ? AND data <= ? ORDER BY id DESC",
            (inicio,fim)
        ).fetchall()
    else:
        registros=conn.execute(
            f"SELECT * FROM {tabela} ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return registros

@app.route("/relatorio/clientes")
def rel_clientes():
    conn=conectar()
    registros=conn.execute("SELECT * FROM clientes ORDER BY nome").fetchall()
    conn.close()
    return render("clientes","👥 Clientes Cadastrados",registros=registros)

@app.route("/relatorio/visitas")
def rel_visitas():
    inicio=request.args.get("inicio","")
    fim=request.args.get("fim","")
    return render("visitas_rel","📋 Relatório Completo de Visitas",
                  registros=periodo("visitas",inicio,fim),inicio=inicio,fim=fim)

@app.route("/relatorio/combustivel")
def rel_combustivel():
    inicio=request.args.get("inicio","")
    fim=request.args.get("fim","")
    return render("combustivel_rel","⛽ Relatório de Combustível",
                  registros=periodo("combustivel",inicio,fim),inicio=inicio,fim=fim)

@app.route("/relatorio/alimentacao")
def rel_alimentacao():
    inicio=request.args.get("inicio","")
    fim=request.args.get("fim","")
    return render("alimentacao_rel","🍽️ Relatório de Alimentação",
                  registros=periodo("alimentacao",inicio,fim),inicio=inicio,fim=fim)

if __name__=="__main__":
    print("AviSui CRM iniciado.")
    print("Acesse no computador: http://127.0.0.1:5000")
    print("Para celular na mesma rede: http://IP-DO-COMPUTADOR:5000")
    app.run(host="0.0.0.0",port=5000,debug=False)
