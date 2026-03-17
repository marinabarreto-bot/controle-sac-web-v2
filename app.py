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

    print(linha)
    awb = request.form["awb"]

    dados = sheet.get_all_records()

    for i, linha in enumerate(dados):

        if str(linha["AWB"]) == awb:

            return jsonify({
                "pedido": linha["Pedido"],
                "data_saida": linha["DATA_SAIDA"],
                "destino": linha["DESTINATARIO"],
                "status": linha["STATUS"]
            })

    return jsonify({"erro": "AWB não encontrado"})


@app.route("/salvar", methods=["POST"])
def salvar():

    awb = request.form["awb"]
    comentario = request.form["comentario"]

    cell = sheet.find(awb)

    sheet.update_cell(cell.row, 14, comentario)

    return "OK"