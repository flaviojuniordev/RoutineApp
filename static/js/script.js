document.addEventListener("DOMContentLoaded", () => {
    // Modal do Calendário
    document.querySelectorAll(".dia").forEach(dia => {
        dia.addEventListener("click", () => {
            const diaStr = dia.getAttribute("data-dia");
            const tarefas = JSON.parse(dia.getAttribute("data-tarefas"));
            abrirModal(diaStr, tarefas);
        });
    });

    // Pomodoro
    const timerElement = document.getElementById("timer");
    const btnIniciar = document.getElementById("btn-iniciar");
    const btnPausar = document.getElementById("btn-pausar");
    const btnReiniciar = document.getElementById("btn-reiniciar");
    const cicloElement = document.getElementById("ciclo");
    const statusElement = document.querySelector(".pomodoro-status");

    if (timerElement) {
        let tempoRestante = 25 * 60; // 25 minutos em segundos
        let intervalo = null;
        let ciclo = 1;
        let pausado = false;
        let ehTrabalho = true;

        function atualizarTimer() {
            const minutos = Math.floor(tempoRestante / 60);
            const segundos = tempoRestante % 60;
            timerElement.textContent = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
        }

        function iniciarTimer() {
            if (!intervalo) {
                intervalo = setInterval(() => {
                    if (tempoRestante > 0) {
                        tempoRestante--;
                        atualizarTimer();
                    } else {
                        clearInterval(intervalo);
                        intervalo = null;
                        if (ehTrabalho) {
                            if (ciclo < 4) {
                                tempoRestante = 5 * 60; // Pausa curta
                                statusElement.textContent = "Pausa Curta";
                            } else {
                                tempoRestante = 15 * 60; // Pausa longa
                                statusElement.textContent = "Pausa Longa";
                                ciclo = 0;
                            }
                            ciclo++;
                            cicloElement.textContent = ciclo;
                        } else {
                            tempoRestante = 25 * 60; // Trabalho
                            statusElement.textContent = "Trabalho";
                        }
                        ehTrabalho = !ehTrabalho;
                        iniciarTimer();
                    }
                }, 1000);
                btnIniciar.disabled = true;
                btnPausar.disabled = false;
            }
        }

        function pausarTimer() {
            if (intervalo) {
                clearInterval(intervalo);
                intervalo = null;
                btnIniciar.disabled = false;
                btnPausar.disabled = true;
            }
        }

        function reiniciarTimer() {
            clearInterval(intervalo);
            intervalo = null;
            tempoRestante = 25 * 60;
            ciclo = 1;
            ehTrabalho = true;
            statusElement.textContent = "Trabalho";
            cicloElement.textContent = ciclo;
            atualizarTimer();
            btnIniciar.disabled = false;
            btnPausar.disabled = true;
        }

        btnIniciar.addEventListener("click", iniciarTimer);
        btnPausar.addEventListener("click", pausarTimer);
        btnReiniciar.addEventListener("click", reiniciarTimer);

        atualizarTimer();
    }
});

// Funções do Modal
function abrirModal(dia, tarefas) {
    const modal = document.getElementById("modal");
    const titulo = document.getElementById("modal-titulo");
    const conteudo = document.getElementById("modal-tarefas");

    const dataBr = dia.split('-').reverse().join('/');
    titulo.innerText = `Tarefas de ${dataBr}`;
    conteudo.innerHTML = '';

    if (!tarefas || tarefas.length === 0) {
        conteudo.innerHTML = '<p>Sem tarefas para este dia.</p>';
    } else {
        tarefas.forEach(tarefa => {
            const card = document.createElement('div');
            card.className = `card ${tarefa.concluida ? 'concluida' : ''} prioridade-${tarefa.prioridade.toLowerCase()}`;
            card.innerHTML = `
                <h4>${tarefa.nome}</h4>
                <p>${tarefa.hora} | Prioridade: ${tarefa.prioridade}</p>
                ${tarefa.notas ? `<p class="notas">${tarefa.notas}</p>` : ''}
                <div class="acoes">
                    ${!tarefa.concluida ? `<button onclick="concluirTarefa(${tarefa.indice})" class="btn-concluir">Concluir</button>` : ''}
                    <button onclick="editarTarefa(${tarefa.indice}, '${tarefa.nome}', '${tarefa.data}', '${tarefa.hora}', '${tarefa.prioridade}', '${tarefa.notas}')" class="btn-editar">Editar</button>
                    <button onclick="excluirTarefa(${tarefa.indice})" class="btn-excluir">Excluir</button>
                </div>
            `;
            conteudo.appendChild(card);
        });
    }

    modal.style.display = "block";
}

function fecharModal() {
    document.getElementById("modal").style.display = "none";
}

function concluirTarefa(indice) {
    window.location.href = `/concluir/${indice}`;
}

function editarTarefa(indice, nome, data, hora, prioridade, notas) {
    const conteudo = document.getElementById("modal-tarefas");
    conteudo.innerHTML = `
        <form method="POST" action="/editar/${indice}" class="form-editar">
            <div class="form-grupo">
                <label for="nome">Nome:</label>
                <input type="text" name="nome" value="${nome}" required>
            </div>
            <div class="form-grupo form-row">
                <div>
                    <label for="data">Data:</label>
                    <input type="date" name="data" value="${data.split('/').reverse().join('-')}" required>
                </div>
                <div>
                    <label for="hora">Horário:</label>
                    <input type="time" name="hora" value="${hora}" required>
                </div>
            </div>
            <div class="form-grupo">
                <label for="prioridade">Prioridade:</label>
                <select name="prioridade">
                    <option value="Alta" ${prioridade === 'Alta' ? 'selected' : ''}>Alta</option>
                    <option value="Média" ${prioridade === 'Média' ? 'selected' : ''}>Média</option>
                    <option value="Baixa" ${prioridade === 'Baixa' ? 'selected' : ''}>Baixa</option>
                </select>
            </div>
            <div class="form-grupo">
                <label for="notas">Notas:</label>
                <textarea name="notas">${notas}</textarea>
            </div>
            <button type="submit" class="btn">Salvar</button>
            <button type="button" onclick="fecharModal()" class="btn-cancelar">Cancelar</button>
        </form>
    `;
}

function excluirTarefa(indice) {
    if (confirm("Tem certeza que deseja excluir esta tarefa?")) {
        fetch(`/excluir/${indice}`, { method: "POST" })
            .then(() => window.location.reload());
    }
}

window.onclick = function (event) {
    const modal = document.getElementById("modal");
    if (event.target == modal) {
        modal.style.display = "none";
    }
};