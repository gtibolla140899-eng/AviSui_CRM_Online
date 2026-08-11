from pathlib import Path

arquivo = Path("app_novo.py")
texto = arquivo.read_text(encoding="utf-8")

texto = texto.replace(
    "from flask import Flask, request, redirect, render_template_string",
    "from flask import Flask, request, redirect, render_template_string, send_file"
)

texto = texto.replace(
    "from datetime import datetime",
    "from datetime import datetime\nfrom openpyxl import Workbook\nfrom io import BytesIO"
)

rotas = r'''

def buscar_excel(tabela, inicio="", fim=""):
    conn = conectar()

    if inicio and fim:
        registros = conn.execute(
            f"SELECT * FROM {tabela} WHERE data >= ? AND data <= ? ORDER BY id DESC",
            (inicio, fim)
        ).fetchall()
    else:
        registros = conn.execute(
            f"SELECT * FROM {tabela} ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return registros


def criar_excel(titulo, colunas, registros, nome):

    wb = Workbook()
    ws = wb.active
    ws.title = titulo

    ws.append(colunas)

    for r in registros:
        ws.append([r[c] for c in colunas_chaves[titulo]])

    for coluna in ws.columns:
        maior = 0
        for celula in coluna:
            if celula.value is not None:
                maior = max(maior, len(str(celula.value)))

        ws.column_dimensions[coluna[0].column_letter].width = min(maior + 2, 45)

    arquivo = BytesIO()
    wb.save(arquivo)
    arquivo.seek(0)

    return send_file(
        arquivo,
        as_attachment=True,
        download_name=nome,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


colunas_chaves = {
    "Visitas": [
        "data","vendedor","cliente","granja","cidade",
        "hora_saida","hora_chegada","km_inicial","km_final",
        "atividade","observacoes"
    ],
    "Combustível": [
        "data","quilometragem","posto","cidade","litros","media"
    ],
    "Alimentação": [
        "data","documento","razao_social","conta_contabil",
        "valor","valor_a_mais","descricao"
    ]
}


@app.route("/excel/visitas")
def excel_visitas():

    inicio = request.args.get("inicio","")
    fim = request.args.get("fim","")

    registros = buscar_excel("visitas", inicio, fim)

    return criar_excel(
        "Visitas",
        [
            "Data","Vendedor","Cliente","Granja","Cidade",
            "Hora saída","Hora chegada","KM inicial","KM final",
            "Atividade","Observações"
        ],
        registros,
        "AviSui_Relatorio_Visitas.xlsx"
    )


@app.route("/excel/combustivel")
def excel_combustivel():

    inicio = request.args.get("inicio","")
    fim = request.args.get("fim","")

    registros = buscar_excel("combustivel", inicio, fim)

    return criar_excel(
        "Combustível",
        [
            "Data","Quilometragem","Posto","Cidade",
            "Litros","Média"
        ],
        registros,
        "AviSui_Relatorio_Combustivel.xlsx"
    )


@app.route("/excel/alimentacao")
def excel_alimentacao():

    inicio = request.args.get("inicio","")
    fim = request.args.get("fim","")

    registros = buscar_excel("alimentacao", inicio, fim)

    return criar_excel(
        "Alimentação",
        [
            "Data","Documento","Razão Social","Conta Contábil",
            "Valor","Valor a mais","Descrição"
        ],
        registros,
        "AviSui_Relatorio_Alimentacao.xlsx"
    )
'''

# Coloca as novas rotas antes do bloco final do programa
texto = texto.replace(
    '\nif __name__=="__main__":',
    rotas + '\nif __name__=="__main__":'
)

# Acrescenta os botões nos relatórios
texto = texto.replace(
    '<div class="tabela">',
    '''
{% if pagina == 'visitas_rel' %}
<a class="botao" href="/excel/visitas?inicio={{ inicio }}&fim={{ fim }}" style="background:#217346">
📊 GERAR EXCEL DE VISITAS
</a>
{% endif %}

{% if pagina == 'combustivel_rel' %}
<a class="botao" href="/excel/combustivel?inicio={{ inicio }}&fim={{ fim }}" style="background:#217346">
📊 GERAR EXCEL DE COMBUSTÍVEL
</a>
{% endif %}

{% if pagina == 'alimentacao_rel' %}
<a class="botao" href="/excel/alimentacao?inicio={{ inicio }}&fim={{ fim }}" style="background:#217346">
📊 GERAR EXCEL DE ALIMENTAÇÃO
</a>
{% endif %}

<div class="tabela">''',
    1
)

arquivo.write_text(texto, encoding="utf-8")

print("ATUALIZAÇÃO DO EXCEL CONCLUÍDA.")
