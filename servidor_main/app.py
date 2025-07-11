from flask import Flask, request, send_file, jsonify
from werkzeug.utils import safe_join
from fpdf import FPDF
import io
import os
from werkzeug.utils import secure_filename
import json
import logging
from flask import render_template
import zipfile
import shutil

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DIRETORIOS_REATORES = {  ################################################################ MODIFICADO ########################################
    "reator1": "dados/reator1",
    "reator2": "dados/reator2"
} ###########################################################################################################################################

def salvar_json(diretorio, nome_arquivo, dados):
    if not nome_arquivo.endswith('.pdf'):
        nome_arquivo += '.pdf'
    nome_json = nome_arquivo.replace('.pdf', '.json')
    caminho_json = os.path.join(diretorio, nome_json)

    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)


def gerar_nome_unico(diretorio, nome_base):
    nome_base = secure_filename(nome_base.strip())
    if not nome_base.endswith('.pdf'):
        nome_base += '.pdf'

    nome, ext = os.path.splitext(nome_base)
    contador = 1
    nome_unico = nome_base

    while os.path.exists(os.path.join(diretorio, nome_unico)):
        nome_unico = f"{nome}_{contador}{ext}"
        contador += 1

    return nome_unico

@app.route('/pdf', methods=['POST'])
def gerar_pdf():
    data = request.get_json()
    texto = data.get('text', "").strip()
    reator = data['reator']
    tabelas = data.get('tabelas', {})
    nome_arquivo = data.get('nome_arquivo', 'relatorio.pdf')

    if not nome_arquivo.endswith('.pdf'):
        nome_arquivo += '.pdf'

    tabela1 = tabelas.get('tabela1', [])
    tabela2 = tabelas.get('tabela2', [])
    tabela3 = tabelas.get('tabela3', [])

    if not texto:
        return jsonify({'error': 'Texto vazio'}), 400

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    nomes_campos = [
        "Nome da amostra", "Materiais", "Temp. Inicial", "Temp. Final",
        "Fonte de energia", "Potência",
        "P.Base Inicial", "P.Base Final",
        "P.Ar Inicial", "P.Ar Final",
        "Flux.Ar Inicial", "Flux.Ar Final",
        "P.02 Inicial", "P.02 Final",
        "P.tot Inicial", "P.tot Final",
        "Tempo dep.", "Distância", "Alvo",
        "Frequência", "TP", "RSH e RLIM", "Observações"
    ]

    unidades = [
        "", "", "°C", "°C",
        "", "W",
        "Pa", "Pa",
        "Pa", "Pa",
        "sccm", "sccm",
        "Pa", "Pa",
        "Pa", "Pa",
        "min", "cm", "",
        "Hz", "", "", ""
    ]

    linhas_texto = texto.split('\n')

    # Exibir os campos em 2 colunas
    col_width = 95
    for i in range(0, min(len(nomes_campos), len(linhas_texto)), 2):
        nome1 = nomes_campos[i]
        unidade1 = unidades[i]
        valor1 = linhas_texto[i] if i < len(linhas_texto) else ''
        # Monta string: Nome: valor unidade
        linha = f"{nome1}: {valor1} {unidade1}".strip()

        if i + 1 < len(nomes_campos):
            nome2 = nomes_campos[i + 1]
            unidade2 = unidades[i + 1]
            valor2 = linhas_texto[i + 1] if i + 1 < len(linhas_texto) else ''
            linha2 = f"{nome2}: {valor2} {unidade2}".strip()
            pdf.cell(col_width, 5, linha, border=0)
            pdf.cell(col_width, 5, linha2, border=0)
        else:
            pdf.cell(0, 5, linha, border=0)
        pdf.ln()
        pdf.ln(5)

    def desenhar_tabela(tabela, titulo):
        if not tabela:
            return
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, titulo, ln=True)
        pdf.set_font("DejaVu", '', 12)

        largura_total_disponivel = 190  # área horizontal útil
        for linha in tabela:
            num_colunas = len(linha)
            largura_coluna = largura_total_disponivel / num_colunas if num_colunas > 0 else 40
            for celula in linha:
                pdf.cell(largura_coluna, 10, str(celula), border=1)
            pdf.ln()
        pdf.ln()

    desenhar_tabela(tabela1, "Dados de Perfilometria")
    desenhar_tabela(tabela2, "Tabela ")
    desenhar_tabela(tabela3, "Tabela ")

    ## Gerar nome único e salvar
    buffer = io.BytesIO()
    buffer.write(pdf.output(dest='S'))
    buffer.seek(0)

    if reator == 'reator1':
        diretorio1 = DIRETORIOS_REATORES["reator1"] #####################  MODIFICADO  ################################################
        filename = gerar_nome_unico(diretorio1, nome_arquivo)
        filepath = os.path.join(diretorio1, filename)

        dados_para_json = {
             "nome_arquivo": nome_arquivo,
             "reator": reator,
             "text": texto,
             "tabelas": tabelas
        }
        salvar_json(diretorio1, filename, dados_para_json)

    if reator == 'reator2':
        diretorio2 = DIRETORIOS_REATORES["reator2"] #####################  MODIFICADO  #################################################
        filename = gerar_nome_unico(diretorio2, nome_arquivo)
        filepath = os.path.join(diretorio2, filename)

        dados_para_json = {
             "nome_arquivo": nome_arquivo,
             "reator": reator,
             "text": texto,
             "tabelas": tabelas
        }
        salvar_json(diretorio2, filename, dados_para_json)

    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())

    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nome_arquivo
    )

@app.route('/arquivos/<reator>')
def listar_arquivos(reator):
    path = DIRETORIOS_REATORES.get(reator)
    if not path or not os.path.isdir(path):
        return jsonify([])

    arquivos = [f for f in os.listdir(path) if f.endswith('.pdf')]
    return jsonify(arquivos)

@app.route('/visualizar/<reator>/<arquivo>')
def visualizar_arquivo(reator, arquivo):
    path = DIRETORIOS_REATORES.get(reator)
    if not path:
        return "Reator nao encontrado", 404

    caminho = os.path.join(path, arquivo)
    if os.path.exists(caminho):
        return send_file(caminho)

    return "Arquivo nao encontrado", 404

@app.route('/json/<reator>/<arquivo>')
def carregar_json(reator, arquivo):
    path = DIRETORIOS_REATORES.get(reator)
    if not path:
        return "Reator nao encontrado", 404
    if not arquivo.lower().endswith('.pdf'):
        return jsonify({'erro': 'Extensao invalida'}), 400

    arquivo_new = arquivo[:-4] + '.json'
    caminho = os.path.join(path, arquivo_new)

    if not os.path.isfile(caminho):
        return jsonify({'erro': 'Arquivo JSON nao encontrado'}), 404

    try:
        with open(caminho, 'r') as f:
           dados = json.load(f)
        return jsonify(dados)
    except FileNotFoundError:
        return jsonify({'erro': 'Arquivo json nao encontrado'}), 404

@app.route('/salvar_pdf/<reator>/<nome_arquivo>', methods=['POST'])
def salvar_pdf(reator, nome_arquivo):
    data = request.get_json()
    texto = data.get('text', '').strip()
    tabelas = data.get('tabelas', {})

    if not nome_arquivo.endswith('.pdf'):
        nome_arquivo += '.pdf'

    diretorio = DIRETORIOS_REATORES.get(reator)
    if not diretorio:
        return jsonify({"erro": "Reator inválido"}), 400

    caminho_json = os.path.join(diretorio, nome_arquivo.replace('.pdf', '.json'))
    caminho_pdf = os.path.join(diretorio, nome_arquivo)

    # Salva JSON atualizado
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Gera novo PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)

    nomes_campos = [
        "Nome da amostra", "Materiais", "Temp. Inicial", "Temp. Final", "Fonte de energia",
        "Potência", "P.Base Inicial", "P.Base Final", "P.Ar Inicial", "P.Ar Final",
        "Flux.Ar Inicial", "Flux.Ar Final", "P.02 Inicial", "P.02 Final",
        "P.tot Inicial", "P.tot Final", "Tempo dep.", "Distância", "Alvo",
        "Frequência", "TP", "RSH e RLIM", "Observações"
    ]

    unidades = [
        "", "", "°C", "°C",
        "", "W",
        "Pa", "Pa",
        "Pa", "Pa",
        "sccm", "sccm",
        "Pa", "Pa",
        "Pa", "Pa",
        "min", "cm", "",
        "Hz", "", "", ""
    ]

    linhas_texto = texto.split('\n')
    col_width = 95
    for i in range(0, min(len(nomes_campos), len(linhas_texto)), 2):
        nome1 = nomes_campos[i]
        unidade1 = unidades[i]
        valor1 = linhas_texto[i] if i < len(linhas_texto) else ''
        linha = f"{nome1}: {valor1} {unidade1}".strip()

        if i + 1 < len(nomes_campos):
            nome2 = nomes_campos[i + 1]
            unidade2 = unidades[i + 1]
            valor2 = linhas_texto[i + 1] if i + 1 < len(linhas_texto) else ''
            linha2 = f"{nome2}: {valor2} {unidade2}".strip()
            pdf.cell(col_width, 5, linha, border=0)
            pdf.cell(col_width, 5, linha2, border=0)
        else:
            pdf.cell(0, 5, linha, border=0)
        pdf.ln(5)

    def desenhar_tabela(tabela, titulo):
        if not tabela:
            return
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, titulo, ln=True)
        pdf.set_font("DejaVu", '', 12)

        largura_total_disponivel = 190  # área horizontal útil
        for linha in tabela:
            num_colunas = len(linha)
            largura_coluna = largura_total_disponivel / num_colunas if num_colunas > 0 else 40
            for celula in linha:
                pdf.cell(largura_coluna, 10, str(celula), border=1)
            pdf.ln()
        pdf.ln()

    # Aplica nomes reais às tabelas
    for nome, tabela in tabelas.items():
        if nome == 'tabela1':
            titulo = "Dados de Perfilometria"
        elif nome == 'tabela2':
            titulo = "Parâmetros do FM"
        elif nome == 'tabela3':
            titulo = "Parâmetros 4 Pontas"
        else:
            titulo = nome.capitalize()
        desenhar_tabela(tabela, titulo)

    pdf.output(caminho_pdf)
    return jsonify({"status": "PDF atualizado com sucesso!"})

@app.route("/remover/<reator>/<nome_arquivo>", methods=["DELETE"])
def remover_arquivo(reator, nome_arquivo):
    diretorio = DIRETORIOS_REATORES.get(reator)
    if not diretorio:
        return jsonify({"erro": "Reator inválido"}), 400

    caminho_pdf = os.path.join(diretorio, nome_arquivo)
    caminho_json = caminho_pdf.replace('.pdf', '.json')

    try:
        if os.path.exists(caminho_pdf):
            os.remove(caminho_pdf)
        if os.path.exists(caminho_json):
            os.remove(caminho_json)
        return jsonify({"mensagem": "Removido com sucesso"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
####################################################################TESTE########################################################################
BASE_DIR = os.path.abspath("uploads")
os.makedirs(BASE_DIR, exist_ok=True)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/arquivos.html')
def arquivos():
    return render_template('arquivos.html')

@app.route('/gerador.html')
def ger():
    return render_template('gerador.html')

@app.route('/api/listar')
def listar():
    caminho = request.args.get('caminho', '').lstrip('/')
    full_path = os.path.join(BASE_DIR, caminho)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    itens = []
    for nome in os.listdir(full_path):
        tipo = 'pasta' if os.path.isdir(os.path.join(full_path, nome)) else 'arquivo'
        itens.append({'nome': nome, 'tipo': tipo})
    return jsonify(itens)

@app.route('/api/upload', methods=['POST'])
def upload():
    caminho = request.form.get('caminho', '').lstrip('/')
    full_path = os.path.join(BASE_DIR, caminho)
    os.makedirs(full_path, exist_ok=True)

    for f in request.files.getlist('arquivo'):
        nome_seguro = secure_filename(f.filename)
        caminho_arquivo = os.path.join(full_path, nome_seguro)
        f.save(caminho_arquivo)

        if nome_seguro.lower().endswith('.zip'):
            nome_pasta = nome_seguro[:-4]  # remove ".zip"
            destino_pasta = os.path.join(full_path, nome_pasta)
            os.makedirs(destino_pasta, exist_ok=True)

            with zipfile.ZipFile(caminho_arquivo, 'r') as zip_ref:
                zip_ref.extractall(destino_pasta)

            os.remove(caminho_arquivo)

    return '', 204

@app.route('/api/criar-pasta', methods=['POST'])
def criar_pasta():
    data = request.get_json()
    nome = secure_filename(data['nome'])
    caminho = data.get('caminho', '').lstrip('/')
    full_path = os.path.join(BASE_DIR, caminho, nome)
    os.makedirs(full_path, exist_ok=True)
    return '', 204

@app.route('/api/remover', methods=['POST'])
def remover():
    data = request.get_json()
    nome = data['nome']
    caminho = data.get('caminho', '').lstrip('/')
    full_path = os.path.join(BASE_DIR, caminho, nome)

    if os.path.isdir(full_path):
        shutil.rmtree(full_path)
    elif os.path.isfile(full_path):
        os.remove(full_path)
    return '', 204

@app.route('/arquivos/<path:subpath>')
def visualizar_geral(subpath):
    from urllib.parse import unquote
    from werkzeug.utils import safe_join

    decoded_path = unquote(subpath)
    try:
        full_path = os.path.abspath(safe_join(BASE_DIR, decoded_path))
    except Exception:
        return "Caminho inválido", 400

    if not full_path.startswith(BASE_DIR):
        return "Acesso negado", 403

    if not os.path.isfile(full_path):
        return f"Arquivo não encontrado: {full_path}", 404

    # Verifica a extensão
    is_pdf = full_path.lower().endswith(".pdf")

    try:
        return send_file(
            full_path,
            mimetype='application/pdf' if is_pdf else None,
            as_attachment=not is_pdf,
            download_name=os.path.basename(full_path)
        )
    except Exception as e:
        return f"Erro ao abrir o arquivo: {e}", 500


if __name__ == '__main__':
    app.run(debug=True)
