from flask import Flask, request, redirect, render_template_string, send_file
import sqlite3
from pathlib import Path
from datetime import datetime
from openpyxl import Workbook
from io import BytesIO

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
<button type="button"
id="avisui-voz-btn"
onclick="avisuiComandoVoz()"
style="width:100%;margin:12px 0;padding:15px;background:#c9151d;color:white;border:0;border-radius:10px;font-size:17px;font-weight:bold;cursor:pointer;">
COMANDO DE VOZ
</button>

<label>Data</label>
<input type="text" name="data" value="{{ hoje }}" required>
<label>Vendedor</label>
<input type="text" name="vendedor" value="Guilherme Tibolla">
<label>Cliente</label>
<input type="text" name="cliente" placeholder="Digite o nome do cliente" required>
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
<a class="botao" href="/cadastrar-cliente">➕ CADASTRAR CLIENTE</a>

<div class="formulario">
<form method="POST" action="/cadastrar-cliente">

<label>Nome do cliente / produtor</label>
<input type="text" name="nome" required>

<label>Nome da granja / propriedade</label>
<input type="text" name="granja">

<label>CPF / CNPJ</label>
<input type="text" name="cpf_cnpj">

<label>Inscrição Estadual</label>
<input type="text" name="inscricao_estadual">

<label>Cidade</label>
<input type="text" name="cidade">

<label>Telefone / WhatsApp</label>
<input type="text" name="telefone">

<label>Endereço</label>
<input type="text" name="endereco">

<label>Tipo</label>
<select name="tipo">
<option value="Avicultura">Avicultura</option>
<option value="Suinocultura">Suinocultura</option>
<option value="Ambos">Ambos</option>
</select>

<label>Observações</label>
<textarea name="observacoes"></textarea>

<button>SALVAR CLIENTE</button>

</form>
</div>



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

<script>
(function(){

function preencher(campo, valor){
    var el = document.querySelector('[name="' + campo + '"]');
    if(el && valor){
        el.value = valor.trim();
        el.dispatchEvent(new Event("input",{bubbles:true}));
        el.dispatchEvent(new Event("change",{bubbles:true}));
    }
}

function normalizar(t){
    return t.toLowerCase()
    .replace(/[?????]/g,"a")
    .replace(/[????]/g,"e")
    .replace(/[????]/g,"i")
    .replace(/[?????]/g,"o")
    .replace(/[????]/g,"u")
    .replace(/?/g,"c");
}

function hora(v){
    var s=normalizar(v);
    var m=s.match(/(\d{1,2})\s*(?:e|:)\s*(\d{1,2})?/);

    if(!m) return v.trim();

    var h=parseInt(m[1]);
    var min=m[2] ? parseInt(m[2]) : 0;

    if(h>23 || min>59) return v.trim();

    return String(h).padStart(2,"0")+":"+
           String(min).padStart(2,"0");
}

function numero(v){
    var s=normalizar(v);

    var mapa={
        "zero":"0","um":"1","uma":"1",
        "dois":"2","duas":"2","tres":"3",
        "quatro":"4","cinco":"5","seis":"6",
        "sete":"7","oito":"8","nove":"9",
        "dez":"10"
    };

    Object.keys(mapa).forEach(function(k){
        s=s.replace(new RegExp("\\b"+k+"\\b","g"),mapa[k]);
    });

    var m=s.match(/[0-9]+(?:[.,][0-9]+)?/);

    return m ? m[0].replace(",",".") : v.trim();
}

function ouvir(){

    var SR=window.SpeechRecognition ||
           window.webkitSpeechRecognition;

    if(!SR){
        alert("Abra o AviSui pelo Google Chrome e permita o microfone.");
        return;
    }

    var bot=document.getElementById("avisui-voz-btn");

    var r=new SR();

    r.lang="pt-BR";
    r.continuous=false;
    r.interimResults=false;

    r.onstart=function(){
        bot.innerText="OUVINDO...";
    };

    r.onerror=function(){
        bot.innerText="COMANDO DE VOZ";
        alert("Nao consegui entender. Tente novamente.");
    };

    r.onend=function(){
        bot.innerText="COMANDO DE VOZ";
    };

    r.onresult=function(e){

        var original=e.results[0][0].transcript.trim();
        var texto=normalizar(original);

        var campos=[
            ["hora de saida","hora_saida"],
            ["hora de chegada","hora_chegada"],
            ["km inicial","km_inicial"],
            ["km final","km_final"],
            ["atividade realizada","atividade"],
            ["observacoes","observacoes"],
            ["observacao","observacoes"],
            ["cliente","cliente"],
            ["granja","granja"],
            ["cidade","cidade"]
        ];

        var encontrados=[];

        campos.forEach(function(c){

            var pos=texto.indexOf(c[0]);

            if(pos>=0){
                encontrados.push({
                    pos:pos,
                    fim:pos+c[0].length,
                    campo:c[1]
                });
            }

        });

        encontrados.sort(function(a,b){
            return a.pos-b.pos;
        });

        if(encontrados.length===0){
            preencher("cliente",original);
            return;
        }

        encontrados.forEach(function(item,i){

            var fim=i+1<encontrados.length
                ? encontrados[i+1].pos
                : original.length;

            var valor=original
                .substring(item.fim,fim)
                .replace(/^[\s,:;-]+/,"")
                .replace(/[\s,:;-]+$/,"")
                .trim();

            if(!valor) return;

            if(item.campo==="hora_saida" ||
               item.campo==="hora_chegada"){
                valor=hora(valor);
            }

            if(item.campo==="km_inicial" ||
               item.campo==="km_final"){
                valor=numero(valor);
            }

            preencher(item.campo,valor);
        });
    };

    r.start();
}

function instalar(){

    var form=document.querySelector('form[action="/visita"]');

    if(!form) return;

    if(document.getElementById("avisui-voz-btn")) return;

    var bot=document.createElement("button");

    bot.type="button";
    bot.id="avisui-voz-btn";
    bot.innerText="COMANDO DE VOZ";

    bot.style.cssText=
        "display:block;width:100%;margin:12px 0;" +
        "padding:14px;background:#b00000;color:white;" +
        "border:0;border-radius:8px;" +
        "font-size:16px;font-weight:bold;";

    bot.onclick=ouvir;

    form.insertBefore(bot,form.firstChild);
}

if(document.readyState==="loading"){
    document.addEventListener("DOMContentLoaded",instalar);
}else{
    instalar();
}

})();
</script>

<!-- AVISUI VOZ FINAL -->
<script>
(function(){

function avisuiPreencher(campo,valor){
    var el=document.querySelector('[name="'+campo+'"]');
    if(el && valor && valor.trim()){
        el.value=valor.trim();
        el.dispatchEvent(new Event("input",{bubbles:true}));
        el.dispatchEvent(new Event("change",{bubbles:true}));
    }
}

function avisuiNormalizar(t){
    return String(t).toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")
    .replace(/?/g,"c");
}

function avisuiHora(v){
    var s=avisuiNormalizar(v).trim();
    var m=s.match(/(\d{1,2})\s*(?:e|:)?\s*(\d{1,2})?/);

    if(!m) return v.trim();

    var h=parseInt(m[1],10);
    var min=m[2] ? parseInt(m[2],10) : 0;

    if(h>23 || min>59) return v.trim();

    return String(h).padStart(2,"0")+":"+String(min).padStart(2,"0");
}

function avisuiNumero(v){
    var s=avisuiNormalizar(v);

    var mapa={
        "zero":"0",
        "um":"1",
        "uma":"1",
        "dois":"2",
        "duas":"2",
        "tres":"3",
        "quatro":"4",
        "cinco":"5",
        "seis":"6",
        "sete":"7",
        "oito":"8",
        "nove":"9",
        "dez":"10"
    };

    Object.keys(mapa).forEach(function(k){
        s=s.replace(new RegExp("\\b"+k+"\\b","g"),mapa[k]);
    });

    var m=s.match(/[0-9]+(?:[.,][0-9]+)?/);

    return m ? m[0].replace(",",".") : v.trim();
}

function iniciarVoz(){

    var SR=window.SpeechRecognition ||
           window.webkitSpeechRecognition;

    if(!SR){
        alert("Abra o AviSui no Google Chrome e permita o microfone.");
        return;
    }

    var bot=document.getElementById("avisui-voz-btn");

    var r=new SR();

    r.lang="pt-BR";
    r.continuous=false;
    r.interimResults=false;
    r.maxAlternatives=1;

    r.onstart=function(){
        bot.innerText="OUVINDO...";
    };

    r.onend=function(){
        bot.innerText="COMANDO DE VOZ";
    };

    r.onerror=function(){
        bot.innerText="COMANDO DE VOZ";
        alert("Nao consegui entender. Tente novamente.");
    };

    r.onresult=function(event){

        var original=event.results[0][0].transcript.trim();
        var texto=avisuiNormalizar(original);

        var campos=[
            ["hora de saida","hora_saida"],
            ["hora de chegada","hora_chegada"],
            ["km inicial","km_inicial"],
            ["km final","km_final"],
            ["atividade realizada","atividade"],
            ["observacoes","observacoes"],
            ["observacao","observacoes"],
            ["cliente","cliente"],
            ["granja","granja"],
            ["cidade","cidade"]
        ];

        var encontrados=[];

        campos.forEach(function(item){

            var pos=texto.indexOf(item[0]);

            if(pos>=0){
                encontrados.push({
                    pos:pos,
                    fim:pos+item[0].length,
                    campo:item[1]
                });
            }

        });

        encontrados.sort(function(a,b){
            return a.pos-b.pos;
        });

        if(encontrados.length===0){
            avisuiPreencher("cliente",original);
            return;
        }

        encontrados.forEach(function(item,index){

            var fim=index+1<encontrados.length
                ? encontrados[index+1].pos
                : original.length;

            var valor=original.substring(item.fim,fim)
                .replace(/^[\s,:;-]+/,"")
                .replace(/[\s,:;-]+$/,"")
                .trim();

            if(!valor) return;

            if(item.campo==="hora_saida" ||
               item.campo==="hora_chegada"){
                valor=avisuiHora(valor);
            }

            if(item.campo==="km_inicial" ||
               item.campo==="km_final"){
                valor=avisuiNumero(valor);
            }

            avisuiPreencher(item.campo,valor);
        });
    };

    r.start();
}

function instalarVoz(){

    var formulario=document.querySelector('form[action="/visita"]');

    if(!formulario) return;

    if(document.getElementById("avisui-voz-btn")) return;

    var bot=document.createElement("button");

    bot.type="button";
    bot.id="avisui-voz-btn";
    bot.innerText="COMANDO DE VOZ";

    bot.style.cssText=
        "display:block;width:100%;margin:15px 0;padding:15px;" +
        "background:#b00000;color:white;border:none;border-radius:8px;" +
        "font-size:17px;font-weight:bold;cursor:pointer;";

    bot.onclick=iniciarVoz;

    formulario.insertBefore(bot,formulario.firstChild);
}

if(document.readyState==="loading"){
    document.addEventListener("DOMContentLoaded",instalarVoz);
}else{
    instalarVoz();
}

})();
</script>
<!-- FIM AVISUI VOZ FINAL -->


<!-- AVISUI VOZ DEFINITIVO -->
<script>
function avisuiNormalizar(t){
    return String(t).toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")
    .replace(/?/g,"c");
}

function avisuiCampo(nome,valor){
    var campo=document.querySelector('[name="'+nome+'"]');

    if(!campo) return;

    valor=String(valor).trim();

    if(!valor) return;

    campo.value=valor;

    campo.dispatchEvent(
        new Event("input",{bubbles:true})
    );

    campo.dispatchEvent(
        new Event("change",{bubbles:true})
    );
}

function avisuiHora(v){

    var s=avisuiNormalizar(v);

    var numeros=s.match(/\d+/g);

    if(!numeros) return v;

    var h=parseInt(numeros[0]);

    var m=numeros.length>1
        ?parseInt(numeros[1])
        :0;

    if(h>23) return v;

    if(m>59) m=0;

    return String(h).padStart(2,"0")+":"+String(m).padStart(2,"0");
}

function avisuiNumero(v){

    var s=avisuiNormalizar(v);

    var mapa={
        "zero":"0",
        "um":"1",
        "uma":"1",
        "dois":"2",
        "duas":"2",
        "tres":"3",
        "quatro":"4",
        "cinco":"5",
        "seis":"6",
        "sete":"7",
        "oito":"8",
        "nove":"9",
        "dez":"10"
    };

    Object.keys(mapa).forEach(function(k){

        s=s.replace(
            new RegExp("\\b"+k+"\\b","g"),
            mapa[k]
        );

    });

    var n=s.match(/\d+(?:[.,]\d+)?/);

    return n
        ?n[0].replace(",",".")
        :v;
}

function avisuiIniciarVoz(){

    var Speech=
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if(!Speech){

        alert(
            "O comando de voz precisa ser usado no Google Chrome."
        );

        return;
    }

    var botao=
        document.getElementById("avisui-voz-btn");

    var reconhecimento=
        new Speech();

    reconhecimento.lang="pt-BR";
    reconhecimento.continuous=false;
    reconhecimento.interimResults=false;
    reconhecimento.maxAlternatives=1;

    reconhecimento.onstart=function(){

        if(botao){

            botao.innerText="OUVINDO...";

            botao.style.background="#555";

        }
    };

    reconhecimento.onend=function(){

        if(botao){

            botao.innerText="COMANDO DE VOZ";

            botao.style.background="#b00000";

        }
    };

    reconhecimento.onerror=function(){

        if(botao){

            botao.innerText="COMANDO DE VOZ";

            botao.style.background="#b00000";

        }

        alert(
            "Nao consegui entender. Toque novamente e fale as informacoes."
        );
    };

    reconhecimento.onresult=function(event){

        var frase=
            event.results[0][0].transcript.trim();

        var normalizada=
            avisuiNormalizar(frase);

        var campos=[

            ["hora de saida","hora_saida"],

            ["hora saida","hora_saida"],

            ["saida","hora_saida"],

            ["hora de chegada","hora_chegada"],

            ["hora chegada","hora_chegada"],

            ["chegada","hora_chegada"],

            ["km inicial","km_inicial"],

            ["quilometragem inicial","km_inicial"],

            ["quilometro inicial","km_inicial"],

            ["km final","km_final"],

            ["quilometragem final","km_final"],

            ["quilometro final","km_final"],

            ["atividade realizada","atividade"],

            ["atividade","atividade"],

            ["observacoes","observacoes"],

            ["observacao","observacoes"],

            ["cliente","cliente"],

            ["granja","granja"],

            ["cidade","cidade"]

        ];

        var encontrados=[];

        campos.forEach(function(item){

            var pos=
                normalizada.indexOf(item[0]);

            if(pos>=0){

                encontrados.push({

                    pos:pos,

                    fim:
                        pos+item[0].length,

                    campo:item[1]

                });

            }

        });

        encontrados.sort(function(a,b){

            return a.pos-b.pos;

        });

        if(encontrados.length===0){

            alert(
                "Fale usando os nomes dos campos. Exemplo: cliente, granja, cidade, hora de saida..."
            );

            return;
        }

        encontrados.forEach(function(item,index){

            var finalTexto=
                index+1<encontrados.length
                ?encontrados[index+1].pos
                :frase.length;

            var valor=
                frase
                .substring(item.fim,finalTexto)
                .replace(/^[\s,:;-]+/,"")
                .replace(/[\s,:;-]+$/,"")
                .trim();

            if(!valor) return;

            if(
                item.campo==="hora_saida" ||
                item.campo==="hora_chegada"
            ){

                valor=avisuiHora(valor);

            }

            if(
                item.campo==="km_inicial" ||
                item.campo==="km_final"
            ){

                valor=avisuiNumero(valor);

            }

            avisuiCampo(
                item.campo,
                valor
            );

        });

    };

    reconhecimento.start();
}
</script>
<!-- FIM AVISUI VOZ DEFINITIVO -->

<!-- AVI SUI VOZ -->
<script>

function avisuiNormalizar(t){
    return String(t)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")
    .replace(/?/g,"c");
}

function avisuiPreencher(nome,valor){

    var campo=document.querySelector('[name="'+nome+'"]');

    if(!campo) return;

    valor=String(valor).trim();

    if(valor==="") return;

    campo.value=valor;

    campo.dispatchEvent(
        new Event("input",{bubbles:true})
    );

    campo.dispatchEvent(
        new Event("change",{bubbles:true})
    );
}

function avisuiNumero(v){

    var s=avisuiNormalizar(v);

    var mapa={
        "zero":"0",
        "um":"1",
        "uma":"1",
        "dois":"2",
        "duas":"2",
        "tres":"3",
        "quatro":"4",
        "cinco":"5",
        "seis":"6",
        "sete":"7",
        "oito":"8",
        "nove":"9",
        "dez":"10",
        "onze":"11",
        "doze":"12",
        "treze":"13",
        "quatorze":"14",
        "quinze":"15",
        "dezesseis":"16",
        "dezessete":"17",
        "dezoito":"18",
        "dezenove":"19",
        "vinte":"20"
    };

    Object.keys(mapa).forEach(function(k){
        s=s.replace(
            new RegExp("\\b"+k+"\\b","g"),
            mapa[k]
        );
    });

    var n=s.match(/[0-9]+(?:[.,][0-9]+)?/);

    if(!n) return v.trim();

    return n[0].replace(",",".");
}

function avisuiHora(v){

    var s=avisuiNormalizar(v);

    var n=s.match(/\d+/g);

    if(!n) return v.trim();

    var h=parseInt(n[0],10);
    var m=n.length>1 ? parseInt(n[1],10) : 0;

    if(h>23) return v.trim();

    if(m>59) m=0;

    return String(h).padStart(2,"0")+":"+String(m).padStart(2,"0");
}

function avisuiComandoVoz(){

    var Reconhecimento=
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if(!Reconhecimento){

        alert(
            "O comando de voz precisa ser usado no Google Chrome."
        );

        return;
    }

    var botao=
        document.getElementById("avisui-voz-btn");

    var r=new Reconhecimento();

    r.lang="pt-BR";
    r.continuous=false;
    r.interimResults=false;
    r.maxAlternatives=1;

    r.onstart=function(){

        botao.innerText="OUVINDO...";
        botao.style.background="#555";
    };

    r.onend=function(){

        botao.innerText="COMANDO DE VOZ";
        botao.style.background="#c9151d";
    };

    r.onerror=function(){

        botao.innerText="COMANDO DE VOZ";
        botao.style.background="#c9151d";

        alert(
            "Nao consegui entender. Toque novamente e fale as informacoes."
        );
    };

    r.onresult=function(event){

        var frase=
            event.results[0][0].transcript.trim();

        var texto=
            avisuiNormalizar(frase);

        var campos=[

            ["vendedor","vendedor"],

            ["cliente","cliente"],

            ["granja","granja"],

            ["cidade","cidade"],

            ["hora de saida","hora_saida"],

            ["hora saida","hora_saida"],

            ["saida","hora_saida"],

            ["hora de chegada","hora_chegada"],

            ["hora chegada","hora_chegada"],

            ["chegada","hora_chegada"],

            ["km inicial","km_inicial"],

            ["quilometragem inicial","km_inicial"],

            ["km final","km_final"],

            ["quilometragem final","km_final"],

            ["atividade realizada","atividade"],

            ["atividade","atividade"],

            ["observacoes","observacoes"],

            ["observacao","observacoes"]

        ];

        var encontrados=[];

        campos.forEach(function(item){

            var pos=texto.indexOf(item[0]);

            if(pos>=0){

                encontrados.push({
                    pos:pos,
                    fim:pos+item[0].length,
                    campo:item[1]
                });

            }

        });

        encontrados.sort(function(a,b){
            return a.pos-b.pos;
        });

        if(encontrados.length===0){

            alert(
                "Fale os campos usando: cliente, granja, cidade, hora de saida, hora de chegada, km inicial, km final, atividade e observacoes."
            );

            return;
        }

        encontrados.forEach(function(item,index){

            var fim=

                index+1<encontrados.length
                ?encontrados[index+1].pos
                :frase.length;

            var valor=

                frase
                .substring(item.fim,fim)
                .replace(/^[\s,:;-]+/,"")
                .replace(/[\s,:;-]+$/,"")
                .trim();

            if(!valor) return;

            if(
                item.campo==="hora_saida" ||
                item.campo==="hora_chegada"
            ){

                valor=avisuiHora(valor);

            }

            if(
                item.campo==="km_inicial" ||
                item.campo==="km_final"
            ){

                valor=avisuiNumero(valor);

            }

            avisuiPreencher(
                item.campo,
                valor
            );

        });

    };

    r.start();
}

</script>
<!-- FIM AVI SUI VOZ -->
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

@app.route("/cadastrar-cliente", methods=["GET","POST"])
def cadastrar_cliente():
    if request.method == "POST":
        conn = conectar()
        conn.execute("""
            INSERT INTO clientes
            (nome, granja, cidade, telefone, observacoes, data_cadastro,
             cpf_cnpj, inscricao_estadual, endereco)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.form.get("nome", ""),
            request.form.get("granja", ""),
            request.form.get("cidade", ""),
            request.form.get("telefone", ""),
            request.form.get("observacoes", ""),
            datetime.now().strftime("%d/%m/%Y"),
            request.form.get("cpf_cnpj", ""),
            request.form.get("inscricao_estadual", ""),
            request.form.get("endereco", "")
        ))
        conn.commit()
        conn.close()
        return redirect("/relatorio/clientes")

    return render("clientes", "Cadastrar Cliente")

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

if __name__=="__main__":
    print("AviSui CRM iniciado.")
    print("Acesse no computador: http://127.0.0.1:5000")
    print("Para celular na mesma rede: http://IP-DO-COMPUTADOR:5000")
    app.run(host="0.0.0.0",port=5000,debug=False)
