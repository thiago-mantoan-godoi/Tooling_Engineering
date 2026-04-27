import pandas as pd
import sys
import os
from datetime import datetime
import warnings

warnings.simplefilter("ignore")

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

# Agora você pode importar normalmente
from src.function import *
from src.extrair_cuts import *


logger = LoggerTerminal(salvar_log=False, typing=True)


def renomear_arquivo(caminho_arquivo):
    if caminho_arquivo.endswith(".XLSX"):
        # Novo caminho com a extensão corrigida
        novo_caminho = caminho_arquivo[:-5] + ".xlsx"

        # Renomeia o arquivo
        os.rename(caminho_arquivo, novo_caminho)
        logger.info(f"Renomeado: {caminho_arquivo} -> {novo_caminho}")
    else:
        logger.atencao("O arquivo não tem a extensão .XLSX.")


logger = LoggerTerminal(salvar_log=False, typing=True)


def converter_cmz_sap():
    os.system("cls")

    logo("Converte Tabela CMZ SAP")

    logger.info("Entre com o caminho do arquivo")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    renomear_arquivo(caminho_base)

    caminho_base = caminho_base.replace("XLSX", "xlsx")

    with pd.ExcelFile(caminho_base) as xls:
        df_cmz = pd.read_excel(xls)

    df_cmz.drop(
        columns=[
            "Master Circuit Plant",
            "Short Description",
            "Common Circuit Plant",
            "Short Description.1",
        ],
        inplace=True,
    )

    df_cmz.rename(
        columns={
            "Plant": "WERKS",
            "Master Circuit": "CIRC_MASTER",
            "Common Circuit": "CIRC_COMUNS",
        },
        inplace=True,
    )

    data_atual = datetime.now().strftime("%d.%m.%Y")
    df_cmz.to_csv(
        f"{caminho_output}/1600.Comuniza.{data_atual}.csv", index=False, sep=";"
    )

    logger.info("Arquivo Salvo!")
