
pip install sounddevice 
pip install scipy 
pip install opencv-python
pip install -q -U google-generativeai

import os
import sounddevice as sd
from scipy.io.wavfile import write
import cv2
import google.generativeai as genai

GOOGLE_API_KEY = "AIzaSyDumNZWD3njWLg32ZPxq2gBagz7w88mPxE"
genai.configure(api_key=GOOGLE_API_KEY)


##informações do consultor
def coletar_informacoes_basicas():
  """Coleta informações básicas sobre a visita técnica."""

  data_visita = input("Data da visita (DD/MM/AAAA): ")
  nome_consultor = input("Nome do Consultor: ")
  objetivo_visita = input("Objetivo da Visita: ")

  return data_visita, nome_consultor, objetivo_visita
## informações do cliente
def coletar_informacoes_cliente():
  """Coleta informações sobre o cliente e a localização da propriedade."""

  nome_cliente = input("Nome do Cliente: ")
  nome_fazenda = input("Nome da Fazenda/Propriedade: ")
  municipio = input("Município: ")
  estado = input("Estado (Sigla): ")

  return nome_cliente, nome_fazenda, municipio, estado
## informalções da safra
def coletar_informacoes_cultura():
  """Coleta informações sobre a safra e a cultura."""

  safra = input("Safra (Ex: 23/24): ")
  cultura = input("Cultura (Ex: Soja, Milho, Algodão): ")

  return safra, cultura



##coletando dados da visita
def coletar_dados_campo():
    """Permite ao usuário escolher um método para inserir dados de campo."""

    print("Escolha uma opção para registrar suas observações:")
    print("1. Carregar uma foto")
    print("2. Gravar um áudio")
    print("3. Escrever um texto")

    escolha = input("Digite o número da sua escolha: ")

    if escolha == '1':
        carregar_foto()
    elif escolha == '2':
        gravar_audio()
    elif escolha == '3':
        escrever_texto()
    else:
        print("Escolha inválida.")

def carregar_foto():
    """Carrega uma foto usando a webcam ou selecionando um arquivo."""

    print("Escolha uma opção:")
    print("1. Tirar foto com a webcam")
    print("2. Selecionar um arquivo")

    opcao_foto = input("Digite o número da sua escolha: ")

    if opcao_foto == '1':
        camera = cv2.VideoCapture(0)
        return_value, image = camera.read()
        cv2.imwrite('foto_observacao.jpg', image)
        camera.release()
        print("Foto capturada com sucesso!")
    elif opcao_foto == '2':
        nome_arquivo = input("Digite o nome do arquivo de imagem: ")
        if os.path.exists(nome_arquivo):
            print("Foto carregada com sucesso!")
        else:
            print(f"Arquivo não encontrado: {nome_arquivo}")
    else:
        print("Opção inválida.")

def gravar_audio():
    """Grava um áudio usando o microfone."""
    fs = 44100  # Taxa de amostragem
    segundos = int(input("Quantos segundos você deseja gravar? "))
    print("Gravando...")
    audio = sd.rec(int(segundos * fs), samplerate=fs, channels=1)
    sd.wait()  # Aguarda a gravação terminar
    print("Gravação finalizada!")
    write('audio_observacao.wav', fs, audio)

def escrever_texto():
    """Permite ao usuário digitar suas observações."""
    observacoes = input("Digite suas observações: ")
    with open('texto_observacao.txt', 'w') as arquivo:
        arquivo.write(observacoes)
    print("Observações salvas com sucesso!")

coletar_dados_campo()
