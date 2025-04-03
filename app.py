from flask import Flask, render_template, request, redirect, url_for
import json
from datetime import datetime
import calendar

app = Flask(__name__)

def carregar_tarefas():
    try:
        with open("tarefas.json", "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []


def salvar_tarefas(tarefas):
    with open("tarefas.json", "w") as arquivo:
        json.dump(tarefas, arquivo, indent=4)


def organizar_tarefas(tarefas):
    calendario = {}
    for i, tarefa in enumerate(tarefas):
        data = tarefa["data"]  # Formato: YYYY-MM-DD
        data_br = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        mes = data[:7]  # Ex.: "2025-04"
        if mes not in calendario:
            ano, mes_num = map(int, mes.split("-"))
            ultimo_dia = calendar.monthrange(ano, mes_num)[1]
            primeiro_dia_semana = calendar.monthrange(ano, mes_num)[0]
            calendario[mes] = {
                "ano": ano,
                "mes_num": mes_num,
                "dias": {
                    f"{mes}-{str(dia).zfill(2)}": [] for dia in range(1, ultimo_dia + 1)
                },
                "primeiro_dia_semana": primeiro_dia_semana,
                "ultimo_dia": ultimo_dia,
            }
        calendario[mes]["dias"][data].append(
            {
                "indice": i,
                "nome": tarefa["nome"],
                "data": data_br,
                "hora": tarefa["hora"],
                "concluida": tarefa["concluida"],
            }
        )
    return calendario

@app.route("/")
def index():
    tarefas = carregar_tarefas()
    calendario = organizar_tarefas(tarefas)
    return render_template("index.html", calendario=calendario)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        nome = request.form["nome"]
        data = request.form["data"]
        hora = request.form["hora"]
        tarefas = carregar_tarefas()
        tarefas.append({"nome": nome, "data": data, "hora": hora, "concluida": False})
        salvar_tarefas(tarefas)
        return redirect(url_for("index"))
    return render_template("adicionar.html")

@app.route("/concluir/<int:indice>")
def concluir(indice):
    tarefas = carregar_tarefas()
    if 0 <= indice < len(tarefas):
        tarefas[indice]["concluida"] = True
        salvar_tarefas(tarefas)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
