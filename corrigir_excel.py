from pathlib import Path

p = Path("app_novo.py")
s = p.read_text(encoding="utf-8")

inicio = s.find("{% if pagina == 'visitas_rel' %}")
fim = s.find("{% endif %}", inicio)

if inicio != -1 and fim != -1:
    fim += len("{% endif %}")
    s = s[:inicio] + s[fim:]

marcador = '<div class="tabela">'

botoes = '''
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
'''

# Localiza especificamente a área dos relatórios
alvo = "{% elif pagina in ['visitas_rel','combustivel_rel','alimentacao_rel'] %}"

pos = s.find(alvo)

if pos == -1:
    print("ERRO: área dos relatórios não encontrada.")
else:
    pos_tabela = s.find(marcador, pos)

    if pos_tabela == -1:
        print("ERRO: tabela dos relatórios não encontrada.")
    else:
        s = s[:pos_tabela] + botoes + "\n" + s[pos_tabela:]
        p.write_text(s, encoding="utf-8")
        print("BOTÕES DO EXCEL CORRIGIDOS COM SUCESSO.")

