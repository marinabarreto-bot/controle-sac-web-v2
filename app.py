from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

import os
import json
import os
import json

creds_json = os.environ.get("GOOGLE_CREDENTIALS")

if not creds_json:
    print("ERRO: GOOGLE_CREDENTIALS não encontrada")
    creds_dict = None
else:
    creds_dict = json.loads(creds_json)

if creds_dict:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1lzSvtyA80WYnUy5_VEK1cu3CfuS8pioH").sheet1
else:
    sheet = None


creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)


client = gspread.authorize(creds)

sheet = client.open_by_key("1lzSvtyA80WYnUy5_VEK1cu3CfuS8pioH").sheet1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buscar", methods=["POST"])
def buscar():
    try:
        awb = request.form["awb"]

        dados = sheet.get_all_records()

        print("DADOS:", dados[:2])  # DEBUG

        for linha in dados:
            print("LINHA:", linha)  # DEBUG

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

    awb = request.form["awb"]
    comentario = request.form["comentario"]

    cell = sheet.find(awb)

    sheet.update_cell(cell.row, 14, comentario)

    return "OK"