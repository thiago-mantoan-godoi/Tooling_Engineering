import pandas as pd
import os
from src.function import *
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


def extrair_ckt_especiais():
    os.system("cls")

    logo("Extrair Circuitos Especiais")

    logger.info("Entre com o caminho do arquivo [.csv]")
    caminho_base = input("").replace('"', "")

    logger.info("Entre com o caminho onde quer salvar o arquivo")
    caminho_output = input("")

    df = pd.read_csv(caminho_base, sep=";")
    df = df.dropna(how="all", axis=1)
    df = df[df["ProdVersion"] == 0].reset_index(drop=True)
    df = df.drop(
        columns=[
            "ProdVersion",
            "Description",
            "BatchSize",
            "ProdVersion",
            "PlanTimeBatch",
            "UserWSText5",
            "CVXVisionSystemCommand",
            "UserWSText7",
            "UserWSText8",
            "StrippingLengthD1",
            "StrippingLengthD2",
            "UserWSText1",
            "UserWSText2",
            "UserWSText6",
            "UserWSText4",
            "UserWSText3",
            "StrippingLength1",
            "PartStripLength1",
            "StrippingLength2",
            "PartStripLength2",
            "StrippingLengthB2",
            "StrippingLengthC1",
            "TwistWireLength",
            "PitchLength",
            "OpenEndLength1",
            "OpenEndLength2",
            "ReducedLeadLength",
            "ReducedWire",
            "StrippingLength4",
            "PartStripLength4",
            "PartStripLength3",
            "StrippingLength3",
            "Wire1CrossSection",
            "Wire1Length",
        ]
    ).reset_index(drop=True)

    df = df[~df["Leadset"].str.startswith("A")].reset_index(drop=True)

    dict_df = {}

    df["Status"] = None
    for i in df.index:
        term1 = df.at[i, "Terminal1Key"]
        term2 = df.at[i, "Terminal2Key"]
        term3 = df.at[i, "Terminal3Key"]
        term4 = df.at[i, "Terminal4Key"]
        seal1 = df.at[i, "Seal1Key"]
        seal2 = df.at[i, "Seal2Key"]
        seal3 = df.at[i, "Seal3Key"]
        seal4 = df.at[i, "Seal4Key"]
        texto1 = df.at[i, "UserText1"]
        texto2 = df.at[i, "UserText2"]
        texto3 = df.at[i, "UserText3"]
        texto4 = df.at[i, "UserText4"]

        if pd.isna(term1):
            term1 = ""
        if pd.isna(term2):
            term2 = ""
        if pd.isna(term3):
            term3 = ""
        if pd.isna(term4):
            term4 = ""
        if pd.isna(seal1):
            seal1 = ""
        if pd.isna(seal2):
            seal2 = ""
        if pd.isna(seal3):
            seal3 = ""
        if pd.isna(seal4):
            seal4 = ""

        if pd.isna(texto1):
            texto1 = ""
        if pd.isna(texto2):
            texto2 = ""
        if pd.isna(texto3):
            texto3 = ""
        if pd.isna(texto4):
            texto4 = ""

        if term1 == texto1 and term2 == texto2 and seal1 == texto3 and seal2 == texto4:
            df.at[i, "Status"] = "normal"
        elif (
            term1 == texto2 and term2 == texto1 and seal1 == texto4 and seal2 == texto3
        ):
            df.at[i, "Status"] = "normal"
        elif (
            term2 == texto1 and term4 == texto2 and seal2 == texto3 and seal4 == texto4
        ):
            df.at[i, "Status"] = "normal"

        elif (
            term1 == texto1 and term2 == texto2 and seal1 == texto3 and seal2 == texto4
        ):
            df.at[i, "Status"] = "normal"
        else:
            df.at[i, "Status"] = "Especial"

    list_componentes = df["Terminal1Key"].dropna().unique().tolist()
    list_componentes.extend(df["Terminal2Key"].dropna().unique().tolist())
    list_componentes.extend(df["Seal1Key"].dropna().unique().tolist())
    list_componentes.extend(df["Seal2Key"].dropna().unique().tolist())

    df = df[df["Status"] == "Especial"].reset_index(drop=True)
    df = df[(df["Terminal1Key"].isna()) & (df["Terminal2Key"].isna())].reset_index(
        drop=True
    )

    dict_df["Circuitos Especiais"] = df[["Status", "Leadset"]]

    # Extrai os códigos únicos de cada coluna com suas respectivas descrições
    dados = [
        ("UserText1", "Terminal"),
        ("UserText2", "Terminal"),
        ("UserText3", "Selo"),
        ("UserText4", "Selo"),
    ]

    # Cria uma lista de DataFrames com os dados e as descrições
    dfs = [
        pd.DataFrame({"Código": df[col].unique(), "Descrição": desc})
        for col, desc in dados
    ]

    # Concatena todos os DataFrames em um único e remove duplicatas
    df_new = pd.concat(dfs, ignore_index=True).drop_duplicates().reset_index(drop=True)
    df_new = df_new[~df_new["Código"].isin(list_componentes)].reset_index(drop=True)

    df_new["Area"] = "Lead Prep"

    df_new = df_new.dropna(subset=["Código"]).reset_index(drop=True)
    dict_df["Componentes do Lead Prep"] = df_new

    salvar_dict_df_em_excel(dict_df, f"{caminho_output}/Circuitos_Especiais.xlsx")

    logger.info("Arquivo salvo!")
