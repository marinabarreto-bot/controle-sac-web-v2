from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# =========================
# CONEXÃO COM GOOGLE SHEETS
# =========================

creds_json = os.environ.get("GOOGLE_CREDENTIALS")

if not creds_json:
    print("ERRO: GOOGLE_CREDENTIALS não encontrada")
    sheet = None
else:
    try:
        creds_dict = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key("1lzSvtyA80WYnUy5_VEK1cu3CfuS8pioH").sheet1
        print("Google Sheets conectado com sucesso")
    except Exception as e:
        print("ERRO AO CONECTAR:", str(e))
        sheet = None


# =========================
# ROTAS
# =========================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buscar", methods=["POST"])
def buscar():
    try:
        if not sheet:
            return jsonify({"erro": "Sem conexão com planilha"})

        awb = request.form["awb"]
        dados = sheet.get_all_records()

        for linha in dados:
            if str(linha.get("AWB")) == awb:
                return jsonify({
                    "pedido": linha.get("Pedido"),
                    "data_saida": linha.get("DATA_SAIDA"),
                    "destino": linha.get("DESTINATARIO"),
                    "status": linha.get("STATUS")
                })

        return jsonify({"erro": "AWB não encontrado"})

    except Exception as e:
        print("ERRO:", str(e))
        return jsonify({"erro": str(e)})


@app.route("/salvar", methods=["POST"])
def salvar():
    try:
        if not sheet:
            return "Erro: sem conexão com planilha"

        awb = request.form["awb"]
        comentario = request.form["comentario"]

        cell = sheet.find(awb)
        sheet.update_cell(cell.row, 14, comentario)

        return "OK"

    except Exception as e:
        print("ERRO SALVAR:", str(e))
        return str(e)