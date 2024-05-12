import os
import io
from datetime import datetime
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ipywidgets as widgets
from IPython.display import display


## Configuração Genai
GOOGLE_API_KEY = "AIzaSyDumNZWD3njWLg32ZPxq2gBagz7w88mPxE"
genai.configure(api_key=GOOGLE_API_KEY)
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



# Função para carregar imagens
def carregar_imagens(btn):
    with output:
        uploaded_file = list(btn_upload.value.values())[0]
        if uploaded_file:
            nome_arquivo = uploaded_file['name']
            conteudo = uploaded_file['content']
            caminho_destino = os.path.join("img", nome_arquivo)
            with open(caminho_destino, 'wb') as f:
                f.write(conteudo)
            print(f"Imagem '{nome_arquivo}' copiada para a pasta 'img'.")
            descricao = input("Digite a descrição da imagem: ")
            descricao = model.generate_content(descricao)
            with open(f"img/{nome_arquivo}.txt", "w") as f:
                f.write(descricao)
            print("Descrição salva com sucesso.")


# Função para gerar o PDF
def gerar_pdf(filename, data, consultor, proprietario, propriedade, municipio, safra, cultura, objetivo, imagens_info):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Cabeçalho
    p = Paragraph(f"Data: {data}            Consultor: {consultor}", styles["Normal"])
    story.append(p)
    story.append(Spacer(1, 12))

    p = Paragraph(f"Nome: {proprietario} Município: {municipio}", styles["Normal"])
    story.append(p)
    story.append(Spacer(1, 12))

    p = Paragraph(f"Estado: MT Propriedade: {propriedade}", styles["Normal"])
    story.append(p)
    story.append(Spacer(1, 12))

    p = Paragraph(f"Safra: {safra} Cultura: {cultura}", styles["Normal"])
    story.append(p)
    story.append(Spacer(1, 12))

    # Objetivo
    p = Paragraph(f"Objetivo da Visita: {objetivo}", styles["Normal"])
    story.append(p)
    story.append(Spacer(1, 24))

    # Imagens e descrições
    for img_info in imagens_info:
        img_path = img_info["caminho"]
        img_descricao = img_info["descricao"]

        im = Image(img_path, width=300, height=200)
        story.append(im)
        story.append(Spacer(1, 12))
        p = Paragraph(f"{img_descricao}", styles["Normal"])
        story.append(p)
        story.append(Spacer(1, 24))

    doc.build(story)
    print(f"PDF '{filename}' gerado com sucesso.")

# Função para enviar email
def enviar_email(destinatario, filename):
    remetente = "seu_email@gmail.com"  # Substitua pelo seu email
    senha = "sua_senha"  # Substitua pela sua senha
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = "Relatório da Visita"

    body = "Segue anexo o relatório da visita."
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(filename, "rb")

    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remetente, senha)
    text = msg.as_string()
    server.sendmail(remetente, destinatario, text)
    server.quit()
    print(f"Email enviado com sucesso para {destinatario}.")


# Coleta de informações
print("""Coleta informações de uma visita através de perguntas ao usuário.""")
consultor = input("Nome do Consultor: ")
data = input("Data da Visita (DD/MM/AAAA): ")
propriedade = input("Nome da Propriedade: ")
proprietario = input("Nome do Proprietário: ")
objetivo = input("Objetivo da Visita: ")
municipio = input("Município da Visita: ")
safra = input("Safra: ")
cultura = input("Qual Cultura: ")

# Carregamento de imagens
if not os.path.exists("img"):
    os.makedirs("img")
btn_upload = widgets.FileUpload(accept='image/*', multiple=False)
btn_carregar = widgets.Button(description="Carregar Imagem")
output = widgets.Output()
btn_carregar.on_click(carregar_imagens)
display(btn_upload, btn_carregar, output)

# Lista para armazenar informações de imagens
imagens_info = []
for filename in os.listdir("img"):
    if filename.endswith((".jpg", ".jpeg", ".png")):
        caminho_imagem = os.path.join("img", filename)
        with open(f"img/{filename}.txt", "r") as f:
            descricao = f.read()
        imagens_info.append({"caminho": caminho_imagem, "descricao": descricao})

# Botões para gerar PDF ou enviar email
btn_gerar_pdf = widgets.Button(description="Gerar PDF")
btn_enviar_email = widgets.Button(description="Enviar por Email")
output_acoes = widgets.Output()

def on_gerar_pdf(btn):
    with output_acoes:
        now = datetime.now()
        data_hora = now.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_visita_{data_hora}.pdf"
        gerar_pdf(nome_arquivo, data, consultor, proprietario, propriedade, municipio, safra, cultura, objetivo, imagens_info)
        print(f"PDF gerado: {nome_arquivo}")

def on_enviar_email(btn):
    with output_acoes:
        destinatario = input("Digite o email do destinatário: ")
        now = datetime.now()
        data_hora = now.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"relatorio_visita_{data_hora}.pdf"
        gerar_pdf(nome_arquivo, data, consultor, proprietario, propriedade, municipio, safra, cultura, objetivo, imagens_info)
        enviar_email(destinatario, nome_arquivo)
        print(f"Email enviado para {destinatario}")

btn_gerar_pdf.on_click(on_gerar_pdf)
btn_enviar_email.on_click(on_enviar_email)
display(btn_gerar_pdf, btn_enviar_email, output_acoes)
