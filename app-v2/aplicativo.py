import tkinter as tk
import mysql.connector
from reportlab.pdfgen import canvas
from tkinter import filedialog
import os
import speech_recognition as sr
from google.api_core.client_options import ClientOptions
from google.cloud import aiplatform_v1beta1 as aiplatform
import google.generativeai as genai
import config # Importe o arquivo de configurações

# Carregar as configurações do arquivo config.py
mysql_config = {
    'host': config.MYSQL_HOST,
    'database': config.MYSQL_DATABASE,
    'user': config.MYSQL_USER,
    'password': config.MYSQL_PASSWORD
}

## Configuração Genai
genai.configure(api_key=config.GOOGLE_API_KEY)
generation_config = {
    "candidate_count": 1,
    "temperature": 0.5,
}

safety_settings = {
    "HARASSMENT": "BLOCK_NONE",
    "HATE": "BLOCK_NONE",
    "SEXUAL": "BLOCK_NONE",
    "DANGEROUS": "BLOCK_NONE",
}
model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                              generation_config = generation_config,
                              safety_settings = safety_settings)


# *** Funções para Transcrição e Regeneração ***
arquivos = []

def transcrever_audio(audio_file):
    """Transcreve um arquivo de áudio para texto usando a API do Google Speech Recognition."""
    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        texto = r.recognize_google(audio, language='pt-BR')
        texto = model.generate_content(texto)
        print("Transcrição do áudio: " + texto)
        return texto
    except sr.UnknownValueError:
        print("Não foi possível entender o áudio")
        return ""
    except sr.RequestError as e:
        print(f"Erro ao solicitar resultados do serviço de reconhecimento de fala do Google: {e}")
        return ""

def regenerar_texto(texto):
    """Regenera o texto usando o modelo PaLM 2 (Gemini)."""
    # Definir as variáveis de ambiente para autenticação com o Google Cloud
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.CREDENTIAL_PATH
    project_id = config.PROJECT_ID
    endpoint_name = config.ENDPOINT_NAME

    # Cria o cliente do Vertex AI
    client_options = ClientOptions(api_endpoint=f"{project_id}-aiplatform.googleapis.com")
    client = aiplatform.PredictionServiceClient(client_options=client_options)

    # Define o nome do endpoint
    endpoint = f"projects/{project_id}/locations/us-central1/endpoints/{endpoint_name}"

    # Cria a instância da predição
    instance = {"content": texto}
    parameters = {}
    endpoint = client.get_endpoint(name=endpoint)

    # Faz a chamada para o modelo
    response = client.predict(endpoint=endpoint.name, instances=[instance], parameters=parameters)

    # Retorna o texto regenerado
    return response.predictions[0]["content"]

# *** Função para Salvar Dados ***
def salvar_dados():
    global conn, cursor
    
    # Obter dados dos campos de entrada
    nome_consultor = entry_nome_consultor.get()
    data_visita = entry_data_visita.get()
    objetivo_visita = entry_objetivo_visita.get()
    nome_cliente = entry_nome_cliente.get()
    propriedade = entry_propriedade.get()
    municipio = entry_municipio.get()
    safra = entry_safra.get()
    cultura = entry_cultura.get()

    try:
        # Iterar sobre os arquivos adicionados
        for tipo, dado in arquivos:
            arquivo = None
            descricao = None
            if tipo == 'texto':
                descricao = regenerar_texto(dado)
            elif tipo == 'audio':
                descricao = transcrever_audio(dado)
                descricao = regenerar_texto(descricao)
                with open(dado, 'rb') as f:
                    arquivo = f.read()

            # Inserir os dados no MySQL
            sql = '''
                INSERT INTO dados_relatorio (
                    nome_consultor, data_visita, objetivo_visita, nome_cliente, 
                    propriedade, municipio, safra, cultura, descricao_arquivo, arquivo
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql, (
                nome_consultor, data_visita, objetivo_visita, nome_cliente,
                propriedade, municipio, safra, cultura, descricao, arquivo
            ))
        conn.commit()
        print("Dados salvos com sucesso no MySQL!")
        tk.messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")

    except mysql.connector.Error as err:
        print(f"Erro ao salvar dados no MySQL: {err}")
        tk.messagebox.showerror("Erro", f"Erro ao salvar dados no MySQL: {err}")

    finally:
        # Limpar os campos de entrada
        entry_nome_consultor.delete(0, tk.END)
        entry_data_visita.delete(0, tk.END)
        entry_objetivo_visita.delete(0, tk.END)
        entry_nome_cliente.delete(0, tk.END)
        entry_propriedade.delete(0, tk.END)
        entry_municipio.delete(0, tk.END)
        entry_safra.delete(0, tk.END)
        entry_cultura.delete(0, tk.END)

        # Limpar a lista de arquivos
        arquivos.clear()

        # Limpar os widgets de arquivo da interface
        for widget in frame_arquivos.winfo_children():
            widget.destroy()

def gerar_relatorio():
    try:
        # Buscar dados do MySQL
        cursor.execute("SELECT * FROM dados_relatorio")
        resultados = cursor.fetchall()

        # Gerar PDF usando reportlab
        c = canvas.Canvas("relatorio.pdf")
        c.drawString(100, 750, "Relatório de Visitas")
        y = 700
        for row in resultados:
            c.drawString(100, y, f"Consultor: {row[1]}")
            c.drawString(100, y - 20, f"Data da Visita: {row[2]}")
            c.drawString(100, y - 40, f"Objetivo: {row[3]}")
            c.drawString(100, y - 60, f"Cliente: {row[4]}")
            c.drawString(100, y - 80, f"Propriedade: {row[5]}")
            c.drawString(100, y - 100, f"Município: {row[6]}")
            c.drawString(100, y - 120, f"Safra: {row[7]}")
            c.drawString(100, y - 140, f"Cultura: {row[8]}")
            c.drawString(100, y - 160, f"Descrição: {row[9]}")
            y -= 180 # Ajuste o espaçamento entre os registros conforme necessário
        c.save()
        print("Relatório gerado com sucesso!")
        tk.messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")

    except mysql.connector.Error as err:
        print(f"Erro ao gerar relatório: {err}")
        tk.messagebox.showerror("Erro", f"Erro ao gerar relatório: {err}")

def adicionar_arquivo():
    # Criar um novo frame para o arquivo
    file_frame = tk.Frame(frame_arquivos)
    file_frame.pack(fill=tk.X, pady=5)

    # Opções para texto ou áudio
    tipo_arquivo = tk.StringVar(value='texto')
    radio_texto = tk.Radiobutton(file_frame, text="Texto", variable=tipo_arquivo, value='texto')
    radio_texto.pack(side=tk.LEFT)
    radio_audio = tk.Radiobutton(file_frame, text="Áudio", variable=tipo_arquivo, value='audio')
    radio_audio.pack(side=tk.LEFT)

    # Campo de entrada para descrição do arquivo (texto) ou caminho do arquivo (audio)
    entry_descricao = tk.Entry(file_frame)
    entry_descricao.pack(side=tk.LEFT, padx=5)

    # Botão para selecionar arquivo ou inserir descrição
    def selecionar_arquivo():
        if tipo_arquivo.get() == 'texto':
            arquivos.append(('texto', entry_descricao.get()))
            print("Descrição em texto adicionada:", entry_descricao.get())
        elif tipo_arquivo.get() == 'audio':
            file_path = filedialog.askopenfilename(filetypes=[("Arquivos de áudio", "*.wav *.mp3 *.flac")])
            if file_path:
                arquivos.append(('audio', file_path))
                print("Arquivo de áudio selecionado:", file_path)
        else:
            print("Tipo de arquivo inválido.")

    botao_selecionar_arquivo = tk.Button(file_frame, text="Selecionar Arquivo/Inserir Descrição", command=selecionar_arquivo)
    botao_selecionar_arquivo.pack(side=tk.LEFT)

# Interface gráfica
root = tk.Tk()
root.title("Coleta de Dados para Relatório")
perguntas = [
    "Nome Consultor:",
    "Data da visita:",
    "Objetivo da Visita:",
    "Nome do Cliente:",
    "Propriedade:",
    "Município:",
    "Safra:",
    "Cultura:"
]
entries = []

# Lista para armazenar as entradas
# Criar campos de entrada para cada pergunta
for i, pergunta in enumerate(perguntas):
    label = tk.Label(root, text=pergunta)
    label.grid(row=i, column=0, padx=5, pady=5)
    entry = tk.Entry(root)
    entry.grid(row=i, column=1, padx=5, pady=5)
    entries.append(entry)

# Armazenar as entradas em variáveis separadas
entry_nome_consultor = entries[0]
entry_data_visita = entries[1]
entry_objetivo_visita = entries[2]
entry_nome_cliente = entries[3]
entry_propriedade = entries[4]
entry_municipio = entries[5]
entry_safra = entries[6]
entry_cultura = entries[7]

# Frame para os arquivos
frame_arquivos = tk.Frame(root)
frame_arquivos.grid(row=len(perguntas), column=0, columnspan=2, pady=10)

# Botão para adicionar arquivo
botao_adicionar_arquivo = tk.Button(root, text="Adicionar Arquivo", command=adicionar_arquivo)
botao_adicionar_arquivo.grid(row=len(perguntas) + 1, column=0, columnspan=2, pady=10)

# Botões para Salvar Dados e Gerar Relatório
botao_salvar = tk.Button(root, text="Salvar Dados", command=salvar_dados)
botao_salvar.grid(row=len(perguntas) + 2, column=0, columnspan=2, pady=10)
botao_relatorio = tk.Button(root, text="Gerar Relatório", command=gerar_relatorio)
botao_relatorio.grid(row=len(perguntas) + 3, column=0, columnspan=2, pady=10)

# Conectar ao MySQL
conn = None
cursor = None 
try:
    conn = mysql.connector.connect(**mysql_config)
    print("Conectado ao MySQL com sucesso!")
    cursor = conn.cursor() 

    # Criar tabela se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dados_relatorio (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome_consultor VARCHAR(255),
            data_visita DATE,
            objetivo_visita TEXT,
            nome_cliente VARCHAR(255),
            propriedade VARCHAR(255),
            municipio VARCHAR(255),
            safra VARCHAR(255),
            cultura VARCHAR(255),
            descricao_arquivo TEXT,
            arquivo LONGBLOB
        )
    ''')
except mysql.connector.Error as err:
    print(f"Erro ao conectar ao MySQL: {err}")
    tk.messagebox.showerror("Erro", f"Erro ao conectar ao MySQL: {err}")
    exit() 

root.mainloop()

# Fechar a conexão com o MySQL ao finalizar
if conn:
    conn.close()
