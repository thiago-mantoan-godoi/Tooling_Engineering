import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from src.function import *
from art import *
from collections import Counter
import traceback
import warnings

warnings.simplefilter("ignore")

#### FUNÇÕES



logger = LoggerTerminal(salvar_log=False, typing=True)


def extrair_pn():
    os.system("cls")

    logo("Extrair derivativos do arquivo SAP")

    logger.info("Entre com o caminho do arquivo [EXPORT SAP]")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    with open(caminho_base, 'rb') as f:
        df = pd.read_excel(f)

    number = df.columns.get_loc('PN_DERIVATIVO_1')
    colunas_tag = df.columns[number:]


    lista_pn = []
    for i in colunas_tag:
        lista_pn = list(set(lista_pn+df[i].dropna().unique().tolist()))


    lista_pn = pd.DataFrame(lista_pn,columns=['Part Number'])

    data_atual = datetime.now().strftime("%d-%m-%Y")

    salvar_arquivo(lista_pn,caminho_output,f"Derivativos atuais_{data_atual}",formato='excel')


    