const chatLogs = document.querySelector('.chat-logs');
const widgetsContainer = document.getElementById('widgets');
const imageUploadWidget = document.getElementById('imageUploadWidget');
const pdfWidget = document.getElementById('pdfWidget');

const perguntas = [
    "Qual o seu nome?",
    "Data da Visita (DD/MM/AAAA):",
    "Nome da Propriedade:",
    "Nome do Proprietário:",
    "Objetivo da Visita:",
    "Município da Visita:",
    "Safra:",
    "Qual Cultura:"
];

const dadosVisita = {};
let perguntaAtual = 0;
let imagensInfo = [];

function criarMensagem(mensagem, tipo) {
    const chatItem = document.createElement('div');
    chatItem.classList.add('chat-item', tipo); 
    chatItem.style.opacity = 0; 

    if (tipo === 'pergunta') {
        chatItem.innerHTML = `<div class="pergunta">${mensagem}</div>`;
    } else if (tipo === 'resposta') {
        // Adicionando a imagem do consultor na resposta
        chatItem.innerHTML = `<div class="resposta"><img src="consultor.jpeg" alt="Consultor"> ${mensagem}</div>`; 
    }

    chatLogs.appendChild(chatItem);

    setTimeout(() => {
        chatItem.style.opacity = 1; 
        chatLogs.scrollTop = chatLogs.scrollHeight;
    }, 10); 
}

function criarInputResposta() {
    const inputArea = document.createElement('div');
    inputArea.classList.add('input-area');

    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = 'Digite sua resposta';
    inputArea.appendChild(input);

    const button = document.createElement('button');
    button.textContent = 'Enviar';
    button.onclick = () => {
        const resposta = input.value;
        if (resposta) {
            widgetsContainer.removeChild(inputArea);
            processarResposta(resposta);
        }
    };
    inputArea.appendChild(button);

    widgetsContainer.appendChild(inputArea);
    input.focus();
}

function fazerPergunta() {
    if (perguntaAtual < perguntas.length) {
        criarMensagem(perguntas[perguntaAtual], 'pergunta');
        criarInputResposta();
    } else {
        iniciarUploadImagens();
    }
}

function processarResposta(resposta) {
    const chave = perguntas[perguntaAtual].replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
    dadosVisita[chave] = resposta;
    criarMensagem(resposta, 'resposta');
    perguntaAtual++;
    fazerPergunta();
}

function iniciarUploadImagens() {
    chatLogs.style.display = 'none';
    imageUploadWidget.style.display = 'block';

    imageUploadWidget.innerHTML = `
        Escolha uma imagem: <input type="file" id="imagemInput" accept="image/*">
        Digite a descrição da imagem: <input type="text" id="descricaoInput" placeholder="Digite a descrição da imagem">
        <button onclick="salvarImagem()">Salvar Imagem</button>
    `;
}

function salvarImagem() {
    const fileInput = document.getElementById('imagemInput');
    const descricaoInput = document.getElementById('descricaoInput');

    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const descricao = descricaoInput.value;
            imagensInfo.push({ caminho: e.target.result, descricao: descricao });
            perguntarNovaImagem();
        };
        reader.readAsDataURL(file);
    }
}

function perguntarNovaImagem() {
    imageUploadWidget.innerHTML = 'Deseja inserir outra imagem?';

    const btnSim = document.createElement('button');
    btnSim.textContent = 'Sim';
    btnSim.onclick = iniciarUploadImagens;
    imageUploadWidget.appendChild(btnSim);

    const btnNao = document.createElement('button');
    btnNao.textContent = 'Não';
    btnNao.onclick = finalizarColetaDados;
    imageUploadWidget.appendChild(btnNao);
}

function finalizarColetaDados() {
    chatLogs.style.display = 'block'; 
    imageUploadWidget.style.display = 'none'; 
    pdfWidget.style.display = 'block'; 

    pdfWidget.innerHTML = `
        <button onclick="gerarPDF()">Gerar PDF</button>
        <button onclick="enviarEmail()">Enviar por E-mail</button>
    `;
}

function gerarPDF() {
    // Lógica para gerar PDF 
    console.log("Gerar PDF");
    console.log(dadosVisita);
    console.log(imagensInfo);
}

function enviarEmail() {
    // Lógica para enviar email
    console.log("Enviar E-mail");
    console.log(dadosVisita);
    console.log(imagensInfo);
}

fazerPergunta(); 