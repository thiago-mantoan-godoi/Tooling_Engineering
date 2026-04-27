import pandas as pd
import os
from datetime import datetime
from src.function import *
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


# Função para renomear arquivo com extensão .XLSX para .xlsx
def renomear_arquivo(caminho_arquivo):
    if caminho_arquivo.endswith(".XLSX"):
        # Novo caminho com a extensão corrigida
        novo_caminho = caminho_arquivo[:-5] + ".xlsx"

        # Renomeia o arquivo
        os.rename(caminho_arquivo, novo_caminho)
        logger.info(f"Renomeado: {caminho_arquivo} -> {novo_caminho}")
    else:
        logger.atencao("O arquivo não tem a extensão .XLSX.")


def converter_arquivo_sap(caminho_base):
    try:
        dados = pd.read_excel(caminho_base, dtype=str)  # Ou pd.read_excel(arquivo) se for Excel
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")
        
    # try:
    #     dados = dados[dados['Familia Externa']!='5A94D85'].reset_index(drop=True)
    # except: pass

    dados["Leadset"] = dados["Internal Family"].astype(str) + dados["CIRCUIT"].astype(str)

    dict_comp_TW = {row["Leadset"]: row["LENGTH"] for i, row in dados.iterrows()}

    lista_inner = [
        "INNER_1",
        "INNER_2",
        "INNER_3",
        "INNER_4",
        "INNER_5",
        "INNER_6",
        "INNER_7",
        "INNER_8",
        "INNER_9",
    ]

    dict_leadset = {}

    for col in lista_inner:
        for j in dados.index:
            if pd.notna(dados.at[j, col]):
                leadset_pernas = str(dados.at[j, "Internal Family"]) + str(
                    dados.at[j, col]
                )
                dict_leadset[leadset_pernas] = dados.at[j, "Leadset"]
                
    dados["Leadset_2"] = dados["Leadset"].map(dict_leadset)

    contagem = dados["Leadset_2"].value_counts()
    dados["Count_Leadset_2"] = dados["Leadset_2"].map(contagem)

    dados["Leadset_new"] = None

    dados = dados.reset_index(drop=True)
    
    id = []

    dados["Comp TW"] = None

    for i in dados.index:
        if float(dados.at[i, "Count_Leadset_2"]) > 2 and "TW" not in str(
            dados.at[i, "Leadset_2"]
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]

        elif (
            float(dados.at[i, "Count_Leadset_2"]) ==2
            and str(dados.at[i, "Internal Family"])[:1] == "G"
            and float(dados.at[i, "SECTIONN"]) < 1.5
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]
            dados.at[i, "Comp TW"] = dict_comp_TW.get(dados.at[i, "Leadset_2"])
        elif (
            float(dados.at[i, "Count_Leadset_2"]) == 2
            and str(dados.at[i, "Internal Family"])[:1] == "G"
            and "MC" in str(dados.at[i, "Leadset_2"])
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]

        elif (
            float(dados.at[i, "Count_Leadset_2"]) == 2
            and str(dados.at[i, "Internal Family"])[:1] == "S"
            and float(dados.at[i, "SECTIONN"]) < 1.5
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]
            dados.at[i, "Comp TW"] = dict_comp_TW.get(dados.at[i, "Leadset_2"])

        elif (
            float(dados.at[i, "Count_Leadset_2"]) == 2
            and str(dados.at[i, "Internal Family"])[:1] == "S"
            and "MC" in str(dados.at[i, "Leadset_2"])
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]

        elif (
            float(dados.at[i, "Count_Leadset_2"]) >= 2
            and str(dados.at[i, "Internal Family"])[:1] == "X"
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset"]

        elif str(dados.at[i, "Internal Family"])[:1] == "V" and "MC" in str(
            dados.at[i, "Leadset_2"]
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]
            dados.at[i, "Comp TW"] = dict_comp_TW.get(dados.at[i, "Leadset_2"])

        elif str(dados.at[i, "Internal Family"])[:1] == "B" and "W" in str(
            dados.at[i, "Leadset_2"]
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset_2"]
            dados.at[i, "Comp TW"] = dict_comp_TW.get(dados.at[i, "Leadset_2"])

        elif (
            float(dados.at[i, "Count_Leadset_2"]) >= 2
            and str(dados.at[i, "Internal Family"])[:1] == "V"
        ):
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset"]
        else:
            dados.at[i, "Leadset_new"] = dados.at[i, "Leadset"]

        # BMW
        if (
            "W" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "B"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)
        if (
            "SHIELDED" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "X"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)

        # VS30 XDF
        if (
            "MC" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "V"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)
        if (
            "TW" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "V"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)

        if (
            "MC" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "X"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)
        if (
            "TW" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "X"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)

        # GEM SPIN
        if (
            "TW" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "S"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)
        if (
            "TW" in str(dados.at[i, "CIRCUIT"])
            and str(dados.at[i, "Internal Family"])[:1] == "G"
            and pd.isna(dados.at[i, "Leadset_2"])
        ):
            id.append(i)

    # print(dados[["Leadset_new","Leadset_2","Count_Leadset_2","Leadset"]])
    # print(id)

    
    

    
    #dados = dados.drop(dados.index[id]).reset_index(drop=True)
    try:
        mask1 = dados[dados['Leadset_new'].isin(dict_leadset.keys())].index
        dados = dados.drop(mask1).reset_index(drop=True)
    except:pass
    try:
        mask2 = dados[dados['Leadset'].isin(dict_leadset.values())].index
        dados = dados.drop(mask2).reset_index(drop=True)
        
    except:pass

    dados = dados.drop(columns=["Count_Leadset_2", "Leadset", "Leadset_2"]).rename(
        columns={"Leadset_new": "Leadset"}
    )

    colunas = ["Leadset"]

    dados = reordenar_colunas(dados, colunas_prioritarias=colunas)

    return dados


def converter():
    os.system("cls")

    logo("Converte arquivo SAP")

    logger.info("Entre com o caminho do arquivo")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    renomear_arquivo(caminho_base)

    caminho_base = caminho_base.replace("XLSX", "xlsx")

    try:
        dados = converter_arquivo_sap(caminho_base)

        data_atual = datetime.now().strftime("%Y_%m_%d")

        dados.to_excel(f"{caminho_output}\Extrato_SAP_{data_atual}.xlsx", index=False)
    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
