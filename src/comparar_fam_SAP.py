import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from src.function import *
import warnings

warnings.simplefilter("ignore")

logger = LoggerTerminal(salvar_log=False, typing=True)


def comparar_fam_sap(path, fam1=None, fam2=None):
    with open(path, "rb") as f:
        df_sap = pd.read_excel(f)

    df_fam1 = df_sap[df_sap["Internal Family"] == fam1].reset_index(drop=True)
    df_fam2 = df_sap[df_sap["Internal Family"] == fam2].reset_index(drop=True)

    df_fam1["FAM"] = fam1
    df_fam2["FAM"] = fam2

    df_fam1["Leadset_comp"] = None
    df_fam2["Leadset_comp"] = None

    for i in df_fam1.index:
        lead = df_fam1.loc[i, "Leadset"]
        df_fam1.loc[i, "Leadset_comp"] = lead

    for i in df_fam2.index:
        lead = df_fam2.loc[i, "Leadset"][:3] + df_fam2.loc[i, "Leadset"][4:]
        df_fam2.loc[i, "Leadset_comp"] = lead

    colunas_ord = ["FAM", "Leadset_comp"]
    df1 = reordenar_colunas(df_fam1, colunas_ord)
    df2 = reordenar_colunas(df_fam2, colunas_ord)

    diff_remover = df1[~df1["Leadset_comp"].isin(df2["Leadset_comp"])]

    diff_add = df2[~df2["Leadset_comp"].isin(df1["Leadset_comp"])]

    df_fam1["Comentários"] = None
    df_fam2["Comentários"] = None

    leadset = df_fam1["Leadset_comp"].unique().tolist()

    dict_consolidados = {}

    dif = pd.DataFrame()
    j = 0
    for i in tqdm(leadset, "Processando", colour="blue"):
        df_prov1 = (
            df_fam1[df_fam1["Leadset_comp"] == i]
            .sort_values(by=["WIRE_TUBE_SPLICE"])
            .reset_index(drop=True)
        )
        df_prov2 = (
            df_fam2[df_fam2["Leadset_comp"] == i]
            .sort_values(by=["WIRE_TUBE_SPLICE"])
            .reset_index(drop=True)
        )

        if len(df_prov1) == 1 and len(df_prov2) == 1:
            if str(df_prov1.loc[0, "WIRE_TUBE_SPLICE"]) != str(
                df_prov2.loc[0, "WIRE_TUBE_SPLICE"]
            ):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "WIRE_TUBE_SPLICE Atual"] = df_prov1.loc[
                    0, "WIRE_TUBE_SPLICE"
                ]
                dif.loc[j, "WIRE_TUBE_SPLICE Novo"] = df_prov2.loc[
                    0, "WIRE_TUBE_SPLICE"
                ]

            if float(df_prov1.loc[0, "LENGTH"]) != float(df_prov2.loc[0, "LENGTH"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "LENGTH Atual"] = df_prov1.loc[0, "LENGTH"]
                dif.loc[j, "LENGTH TW Atual"] = df_prov1.loc[0, "Comp TW"]
                dif.loc[j, "LENGTH Novo"] = df_prov2.loc[0, "LENGTH"]
                dif.loc[j, "LENGTH TW Novo"] = df_prov2.loc[0, "Comp TW"]

            if str(df_prov1.loc[0, "TERM_A"]) != str(df_prov2.loc[0, "TERM_A"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "TERM_A Atual"] = df_prov1.loc[0, "TERM_A"]
                dif.loc[j, "TERM_A Novo"] = df_prov2.loc[0, "TERM_A"]

            if str(df_prov1.loc[0, "SEAL_A"]) != str(df_prov2.loc[0, "SEAL_A"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "SEAL_A Atual"] = df_prov1.loc[0, "SEAL_A"]
                dif.loc[j, "SEAL_A Novo"] = df_prov2.loc[0, "SEAL_A"]

            if str(df_prov1.loc[0, "TERM_B"]) != str(df_prov2.loc[0, "TERM_B"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "TERM_B Atual"] = df_prov1.loc[0, "TERM_B"]
                dif.loc[j, "TERM_B Novo"] = df_prov2.loc[0, "TERM_B"]

            if str(df_prov1.loc[0, "SEAL_B"]) != str(df_prov2.loc[0, "SEAL_B"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "SEAL_B Atual"] = df_prov1.loc[0, "SEAL_B"]
                dif.loc[j, "SEAL_B Novo"] = df_prov2.loc[0, "SEAL_B"]

            j += 1

        if len(df_prov1) >= 2 and len(df_prov2) >= 2:
            if str(df_prov1.loc[0, "WIRE_TUBE_SPLICE"]) != str(
                df_prov2.loc[0, "WIRE_TUBE_SPLICE"]
            ) and str(df_prov1.loc[1, "WIRE_TUBE_SPLICE"]) != str(
                df_prov2.loc[1, "WIRE_TUBE_SPLICE"]
            ):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "WIRE_TUBE_SPLICE TW Atual 1"] = df_prov1.loc[
                    0, "WIRE_TUBE_SPLICE"
                ]
                dif.loc[j, "WIRE_TUBE_SPLICE TW Atual 2"] = df_prov1.loc[
                    0, "WIRE_TUBE_SPLICE"
                ]
                dif.loc[j, "WIRE_TUBE_SPLICE TW Novo 1"] = df_prov2.loc[
                    1, "WIRE_TUBE_SPLICE"
                ]
                dif.loc[j, "WIRE_TUBE_SPLICE TW Novo 2"] = df_prov2.loc[
                    1, "WIRE_TUBE_SPLICE"
                ]

            if float(df_prov1.loc[0, "Comp TW"]) != float(df_prov2.loc[0, "Comp TW"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "LENGTH TW Atual"] = df_prov1.loc[0, "Comp TW"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "LENGTH TW Novo"] = df_prov2.loc[0, "Comp TW"]

            if float(df_prov1.loc[0, "LENGTH"]) != float(df_prov2.loc[0, "LENGTH"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "LENGTH Atual"] = df_prov1.loc[0, "LENGTH"]
                dif.loc[j, "LENGTH Novo"] = df_prov2.loc[0, "LENGTH"]

            if str(df_prov1.loc[0, "TERM_A"]) != str(df_prov2.loc[0, "TERM_A"]) and str(
                df_prov1.loc[1, "TERM_A"]
            ) != str(df_prov2.loc[1, "TERM_A"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "TERM_A Atual 1"] = df_prov1.loc[0, "TERM_A"]
                dif.loc[j, "TERM_A Novo 1"] = df_prov2.loc[0, "TERM_A"]
                dif.loc[j, "TERM_A Atual 2"] = df_prov1.loc[1, "TERM_A"]
                dif.loc[j, "TERM_A Novo 2"] = df_prov2.loc[1, "TERM_A"]

            if str(df_prov1.loc[0, "SEAL_A"]) != str(df_prov2.loc[0, "SEAL_A"]) and str(
                df_prov1.loc[1, "SEAL_A"]
            ) != str(df_prov2.loc[1, "SEAL_A"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "SEAL_A Atual 1"] = df_prov1.loc[0, "SEAL_A"]
                dif.loc[j, "SEAL_A Novo 1"] = df_prov2.loc[0, "SEAL_A"]
                dif.loc[j, "SEAL_A Atual 2"] = df_prov1.loc[1, "SEAL_A"]
                dif.loc[j, "SEAL_A Novo 2"] = df_prov2.loc[1, "SEAL_A"]

            if str(df_prov1.loc[0, "TERM_B"]) != str(df_prov2.loc[0, "TERM_B"]) and str(
                df_prov1.loc[1, "TERM_B"]
            ) != str(df_prov2.loc[1, "TERM_B"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "TERM_B Atual 1"] = df_prov1.loc[0, "TERM_B"]
                dif.loc[j, "TERM_B Novo 1"] = df_prov2.loc[0, "TERM_B"]
                dif.loc[j, "TERM_B Atual 2"] = df_prov1.loc[1, "TERM_B"]
                dif.loc[j, "TERM_B Novo 2"] = df_prov2.loc[1, "TERM_B"]

            if str(df_prov1.loc[0, "SEAL_B"]) != str(df_prov2.loc[0, "SEAL_B"]) and str(
                df_prov1.loc[1, "SEAL_B"]
            ) != str(df_prov2.loc[1, "SEAL_B"]):
                dif.loc[j, "Leadset Atual"] = df_prov1.loc[0, "Leadset"]
                dif.loc[j, "Leadset Novo"] = df_prov2.loc[0, "Leadset"]
                dif.loc[j, "SEAL_B Atual 1"] = df_prov1.loc[0, "SEAL_B"]
                dif.loc[j, "SEAL_B Novo 1"] = df_prov2.loc[0, "SEAL_B"]
                dif.loc[j, "SEAL_B Atual 2"] = df_prov1.loc[1, "SEAL_B"]
                dif.loc[j, "SEAL_B Novo 2"] = df_prov2.loc[1, "SEAL_B"]

            j += 1

    dif = dif.reset_index(drop=True)

    dif.fillna("-", inplace=True)

    dict_consolidados["Remover"] = diff_remover
    dict_consolidados["Adicionar"] = diff_add
    dict_consolidados["Alteração"] = dif

    return dict_consolidados


def comparar_fam():
    os.system("cls")

    logo("Comparar FAM SAP")

    logger.info("Entre com o caminho do arquivo")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com a FAM sem o UNDERLINE")
    fam1_vlr = input("[>] ").upper()

    logger.info("Entre com a FAM com o UNDERLINE")
    fam2_vlr = input("[>] ").upper()

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    try:
        dados = comparar_fam_sap(caminho_base, fam1=fam1_vlr, fam2=fam2_vlr)

        data_atual = datetime.now().strftime("%Y_%m_%d")

        salvar_dict_df_em_excel(
            dados,
            f"{caminho_output}\Análise_comparar_fam_SAP_{fam1_vlr}_{data_atual}.xlsx",
        )
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
