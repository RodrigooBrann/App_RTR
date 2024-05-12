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
from flask import Flask, request, jsonify

# ... (Código GenAI)

def gerar_pdf(nome_arquivo, data, consultor, proprietario, propriedade, municipio, safra, cultura, objetivo, imagens_info):
    doc = SimpleDocTemplate(nome_arquivo, pagesize=letter)
    styles = getSampleStyleSheet()

    # Construir conteúdo do PDF (adicionar imagens, formatação, etc.)
    # ...

    doc.build(elements)

def enviar_email(destinatario, assunto, corpo, arquivo_pdf=None):
    msg = MIMEMultipart()
    msg['From'] = 'seu_email@gmail.com'
    msg['To'] = destinatario
    msg['Subject'] = assunto
    msg.attach(MIMEText(corpo, 'plain'))

    if arquivo_pdf:
        with open(arquivo_pdf, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {arquivo_pdf}")
            msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('seu_email@gmail.com', 'sua_senha')
    text = msg.as_string()
    server.sendmail('seu_email@gmail.com', destinatario, text)
    server.quit()

app = Flask(__name__)

@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    dados = request.get_json()

    # Extrair dados do JSON
    data = dados['data']
    consultor = dados['consultor']
    proprietario = dados['proprietario']
    propriedade = dados['propriedade']
    municipio = dados['municipio']
    safra = dados['safra']
    cultura = dados['cultura']
    objetivo = dados['objetivo']
    imagens_info = dados['imagensInfo']

    now = datetime.now()
    data_hora = now.strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_visita_{data_hora}.pdf"
    gerar_pdf(nome_arquivo, data, consultor, proprietario, propriedade, municipio, safra, cultura, objetivo, imagens_info)

    return jsonify({"mensagem": f"PDF gerado: {nome_arquivo}"})

if __name__ == '__main__':
    app.run(debug=True)