from flask import Flask, render_template, request, jsonify
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__)

# Escopos corretos
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =========================
# CONEXÃO COM GOOGLE SHEETS
# =========================

sheet = None

creds_json = os.environ.get("GOOGLE_CREDENTIALS")

if not creds_json:
    print("ERRO: GOOGLE_CREDENTIALS não encontrada")
else:
    try:
        creds_dict = json.loads(creds_json)

        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        client = gspread.authorize(creds)

        planilha = client.open_by_key("1KBhkkY2Ma2WJ4_dSmIzE8tvClmBQMwuMkD-P0oXaKVE")
        sheet = planilha.get_worksheet(0)

        print("✅ Google Sheets conectado com sucesso")

    except Exception as e:
        import traceback
        print("❌ ERRO AO CONECTAR:")
        traceback.print_exc()
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

        awb = request.form.get("awb")

        dados = sheet.get_all_records()

        for linha in dados:
            if str(linha.get("AWB")) == str(awb):
                return jsonify({
                    "pedido": linha.get("Pedido"),
                    "data_saida": linha.get("DATA_SAIDA"),
                    "destino": linha.get("DESTINATARIO"),
                    "status": linha.get("STATUS")
                })

        return jsonify({"erro": "AWB não encontrado"})

    except Exception as e:
        import traceback
        traceback.print_exc()
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