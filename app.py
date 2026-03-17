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

creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)


client = gspread.authorize(creds)

sheet = client.open("tb_Fedex").sheet1


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/buscar", methods=["POST"])
def buscar():

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