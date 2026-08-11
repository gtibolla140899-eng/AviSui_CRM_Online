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


HTML = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>AviSui CRM</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #111111;
    color: #ffffff;
    font-family: Arial, sans-serif;
}

.header {
    background: #1c1c1c;
    padding: 20px;
    text-align: center;
    border-bottom: 2px solid #d71920;
}

.logo {
    font-size: 28px;
    font-weight: bold;
}

.subtitulo {
    color: #aaaaaa;
    margin-top: 5px;
}

.container {
    padding: 18px;
    max-width: 600px;
    margin: auto;
}

.card {
    background: #1c1c1c;
    border: 1px solid #333333;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
}

.titulo {
    font-size: 21px;
    font-weight: bold;
    margin-bottom: 18px;
}

label {
    display: block;
    color: #bbbbbb;
    font-size: 14px;
    font-weight: bold;
    margin-top: 14px;
    margin-bottom: 6px;
}

input,
select,
textarea {
    width: 100%;
    padding: 14px;
    border: 1px solid #444444;
    border-radius: 9px;
    background: #292929;
    color: white;
    font-size: 16px;
}

textarea {
    min-height: 90px;
    resize: vertical;
}

button {
    width: 100%;
    padding: 16px;
    margin-top: 20px;
    border: none;
    border-radius: 10px;
    background: #d71920;
    color: white;
    font-size: 17px;
    font-weight: bold;
}

.visita {
    border-top: 1px solid #333333;
    padding: 14px 0;
}

.info {
    color: #bbbbbb;
    font-size: 14px;
    line-height: 1.6;
}

.sucesso {
    background: #174d2b;
    border: 1px solid #287a45;
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 18px;
}

</style>
</head>

<body>

<div class="header">

    <div class="logo">AviSui CRM</div>

    <div class="subtitulo">
        Equipamentos para avicultura e suinocultura
    </div>

</div>

<div class="container">

{% if sucesso %}

<div class="sucesso">
    ✓ Visita registrada com sucesso!
</div>

{% endif %}

<div class="card">

<div class="titulo">
    📝 Registrar Visita
</div>

<form method="POST" action="/visita">

<label>Data</label>
<input
    type="text"
    name="data"
    value="{{ hoje }}"
    required
>

<label>Vendedor</label>
<input
    type="text"
    name="vendedor"
    value="Guilherme Tibolla"
>

<label>Cliente</label>

<select name="cliente" required>

<option value="">
Selecione o cliente
</option>

{% for cliente in clientes %}

<option value="{{ cliente['nome'] }}">
{{ cliente['nome'] }}
</option>

{% endfor %}

</select>

<label>Granja</label>
<input type="text" name="granja">

<label>Cidade</label>
<input type="text" name="cidade">

<label>Hora de saída</label>
<input type="time" name="hora_saida">

<label>Hora de chegada</label>
<input type="time" name="hora_chegada">

<label>KM inicial</label>
<input
    type="number"
    step="0.1"
    name="km_inicial"
>

<label>KM final</label>
<input
    type="number"
    step="0.1"
    name="km_final"
>

<label>Atividade realizada</label>
<textarea name="atividade"></textarea>

<label>Observações</label>
<textarea name="observacoes"></textarea>

<button type="submit">
    SALVAR VISITA
</button>

</form>

</div>


<div class="card">

<div class="titulo">
    📋 Últimas visitas
</div>

{% for visita in visitas %}

<div class="visita">

<strong>
{{ visita['cliente'] }}
</strong>

<div class="info">

{{ visita['data'] }}<br>

{{ visita['cidade'] }}

{% if visita['granja'] %}
<br>{{ visita['granja'] }}
{% endif %}

{% if visita['atividade'] %}
<br>{{ visita['atividade'] }}
{% endif %}

</div>

</div>

{% else %}

<div class="info">
Nenhuma visita registrada.
</div>

{% endfor %}

</div>

</div>

</body>
</html>
"""


@app.route("/")
def inicio():

    conn = conectar()

    clientes = conn.execute("""
        SELECT nome
        FROM clientes
        ORDER BY nome
    """).fetchall()

    visitas = conn.execute("""
        SELECT *
        FROM visitas
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template_string(
        HTML,
        clientes=clientes,
        visitas=visitas,
        hoje=datetime.now().strftime("%d/%m/%Y"),
        sucesso=False
    )


@app.route("/visita", methods=["POST"])
def salvar_visita():

    dados = (
        request.form.get("data", ""),
        request.form.get("vendedor", ""),
        request.form.get("cliente", ""),
        request.form.get("granja", ""),
        request.form.get("cidade", ""),
        request.form.get("hora_saida", ""),
        request.form.get("hora_chegada", ""),
        request.form.get("km_inicial") or 0,
        request.form.get("km_final") or 0,
        request.form.get("atividade", ""),
        request.form.get("observacoes", "")
    )

    conn = conectar()

    conn.execute("""
        INSERT INTO visitas
        (
            data,
            vendedor,
            cliente,
            granja,
            cidade,
            hora_saida,
            hora_chegada,
            km_inicial,
            km_final,
            atividade,
            observacoes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, dados)

    conn.commit()
    conn.close()

    conn = conectar()

    clientes = conn.execute("""
        SELECT nome
        FROM clientes
        ORDER BY nome
    """).fetchall()

    visitas = conn.execute("""
        SELECT *
        FROM visitas
        ORDER BY id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template_string(
        HTML,
        clientes=clientes,
        visitas=visitas,
        hoje=datetime.now().strftime("%d/%m/%Y"),
        sucesso=True
    )


if __name__ == "__main__":

    print("")
    print("==============================================")
    print(" AVI SUI CRM - ACESSO PELO CELULAR")
    print("==============================================")
    print("")
    print("Mantenha esta janela aberta.")
    print("O celular deverá estar na mesma rede Wi-Fi.")
    print("")
    
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
