from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
from datetime import datetime, timedelta
import calendar

app = Flask(__name__)


# Funções para gerenciar tarefas
def carregar_tarefas():
    try:
        with open("tarefas.json", "r") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        return []


def salvar_tarefas(tarefas):
    with open("tarefas.json", "w") as arquivo:
        json.dump(tarefas, arquivo, indent=4)


# Organizar tarefas e gerar calendário completo
def organizar_tarefas(tarefas):
    calendario = {}
    for i, tarefa in enumerate(tarefas):
        data = tarefa["data"]
        data_br = datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y")
        mes = data[:7]
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
                "prioridade": tarefa.get("prioridade", "Média"),
                "notas": tarefa.get("notas", ""),
            }
        )

    # Ordenar tarefas por horário em cada dia
    for mes in calendario:
        for dia in calendario[mes]["dias"]:
            calendario[mes]["dias"][dia].sort(key=lambda x: x["hora"])

    return calendario


# Rota principal - Lista de tarefas
@app.route("/")
def index():
    tarefas = carregar_tarefas()
    calendario = organizar_tarefas(tarefas)
    return render_template("index.html", calendario=calendario)


# Rota para adicionar tarefa
@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        nome = request.form["nome"]
        data = request.form["data"]
        hora = request.form["hora"]
        prioridade = request.form.get("prioridade", "Média")
        notas = request.form.get("notas", "")
        repetir = request.form.get("repetir", "Não")
        tarefas = carregar_tarefas()

        tarefas.append(
            {
                "nome": nome,
                "data": data,
                "hora": hora,
                "concluida": False,
                "prioridade": prioridade,
                "notas": notas,
            }
        )

        if repetir != "Não":
            data_inicial = datetime.strptime(data, "%Y-%m-%d")
            for i in range(1, 30):
                if repetir == "Diária":
                    nova_data = data_inicial + timedelta(days=i)
                elif repetir == "Semanal":
                    nova_data = data_inicial + timedelta(weeks=i)
                elif repetir == "Mensal":
                    nova_data = data_inicial + timedelta(days=i * 30)
                tarefas.append(
                    {
                        "nome": nome,
                        "data": nova_data.strftime("%Y-%m-%d"),
                        "hora": hora,
                        "concluida": False,
                        "prioridade": prioridade,
                        "notas": notas,
                    }
                )

        salvar_tarefas(tarefas)
        return redirect(url_for("index"))
    return render_template("adicionar.html")


# Rota para marcar tarefa como concluída
@app.route("/concluir/<int:indice>")
def concluir(indice):
    tarefas = carregar_tarefas()
    if 0 <= indice < len(tarefas):
        tarefas[indice]["concluida"] = True
        salvar_tarefas(tarefas)
    return redirect(url_for("index"))


# Rota para editar tarefa
@app.route("/editar/<int:indice>", methods=["POST"])
def editar(indice):
    tarefas = carregar_tarefas()
    if 0 <= indice < len(tarefas):
        tarefas[indice]["nome"] = request.form["nome"]
        tarefas[indice]["data"] = request.form["data"]
        tarefas[indice]["hora"] = request.form["hora"]
        tarefas[indice]["prioridade"] = request.form.get("prioridade", "Média")
        tarefas[indice]["notas"] = request.form.get("notas", "")
        salvar_tarefas(tarefas)
    return redirect(url_for("index"))


# Rota para excluir tarefa
@app.route("/excluir/<int:indice>", methods=["POST"])
def excluir(indice):
    tarefas = carregar_tarefas()
    if 0 <= indice < len(tarefas):
        tarefas.pop(indice)
        salvar_tarefas(tarefas)
    return redirect(url_for("index"))


# Rota para o Pomodoro
@app.route("/pomodoro")
def pomodoro():
    return render_template("pomodoro.html")


if __name__ == "__main__":
    app.run(debug=True)
