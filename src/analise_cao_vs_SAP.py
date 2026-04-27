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


def analise_delta_sap_cao(path_base, path_analise, path_permit):
    with pd.ExcelFile(path_base) as xls:
        # Ler uma planilha específica
        df = pd.read_excel(xls)

    with pd.ExcelFile(path_analise) as xls:
        # Ler uma planilha específica
        df_analise = pd.read_excel(xls, sheet_name="Análise")

    with pd.ExcelFile(path_permit) as xls:
        # Ler uma planilha específica
        df_permit = pd.read_excel(xls)

    dict_permit = {
        row["Leadset"]: "Permit: " + str(row["Permit"])
        for i, row in df_permit.iterrows()
    }

    list_ordem = df["Text 15"].unique().tolist()

    lista_new = []

    for i in list_ordem:
        df_prov = df[df["Text 15"] == i].reset_index(drop=True)

        try:
            circuito = df_prov[df_prov["Text 03"] == 0]["Text 02"].values[0]
            componente = df_prov[df_prov["Unit"] == "mm"]["Text 02"].unique().tolist()

            if len(componente) == 2:
                quantidade = float(
                    df_prov[
                        (df_prov["Unit"] == "mm")
                        & (df_prov["Text 02"].astype(str) == str(componente[0]))
                    ]["Quantity"].sum()
                    / 1000
                )
                pcs = df_prov[df_prov["Text 03"] == 0]["Quantity"].values[0]
                lista_new.append([i, circuito, componente[0], quantidade, pcs])

                quantidade = float(
                    df_prov[
                        (df_prov["Unit"] == "mm")
                        & (df_prov["Text 02"].astype(str) == str(componente[1]))
                    ]["Quantity"].sum()
                    / 1000
                )
                pcs = df_prov[df_prov["Text 03"] == 0]["Quantity"].values[0]
                lista_new.append([i, circuito, componente[1], quantidade, pcs])
            else:
                quantidade = float(
                    df_prov[
                        (df_prov["Unit"] == "mm")
                        & (df_prov["Text 02"].astype(str) == str(componente[0]))
                    ]["Quantity"].sum()
                    / 1000
                )
                pcs = df_prov[df_prov["Text 03"] == 0]["Quantity"].values[0]
                lista_new.append([i, circuito, componente[0], quantidade, pcs])
        except Exception:
            # display(df_prov[df_prov['Text 03']==0])
            # print(f'Err: {e}')
            pass

    lista_new = pd.DataFrame(
        lista_new,
        columns=[
            "Order",
            "Leadset",
            "Componente",
            "Consumo [Metros]",
            "Quantide de circuitos",
        ],
    )

    df_analise = df_analise[
        [
            "Leadset Atual",
            "Length Atual",
            "Length Novo",
            "Length TW Atual",
            "Length TW Novo",
        ]
    ]

    df_analise = df_analise.dropna(
        how="all",
        subset=["Length Atual", "Length Novo", "Length TW Atual", "Length TW Novo"],
    ).reset_index(drop=True)

    for i in df_analise.index:
        if pd.isna(df_analise.loc[i, "Length Atual"]):
            df_analise.loc[i, "Length Atual"] = df_analise.loc[i, "Length TW Atual"]
        if pd.isna(df_analise.loc[i, "Length Novo"]):
            df_analise.loc[i, "Length Novo"] = df_analise.loc[i, "Length TW Novo"]

    df_analise = df_analise.drop(columns=["Length TW Atual", "Length TW Novo"]).rename(
        columns={
            "Length Atual": "Length [CAO]",
            "Length Novo": "Length [SAP]",
            "Leadset Atual": "Leadset",
        }
    )

    df_consolidado = pd.merge(lista_new, df_analise, on="Leadset", how="outer")
    df_consolidado = df_consolidado[
        (df_consolidado["Order"].notna()) & (df_consolidado["Length [CAO]"].notna())
    ].reset_index(drop=True)

    df_consolidado["Comentários"] = (
        df_consolidado["Leadset"].map(dict_permit).fillna("Sem histórico de permit")
    )

    return df_consolidado


# path_df = (
#     r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Documents\2026\mar-26\11-mar\Consulta\Resumo.xlsx"
# )

# path_analise = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Documents\2025\11.Nov\17-11-2025\Análise_CAO_Completo_2025_11_17.xlsx"

# path_permit = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Documents\Permit_CAO.xlsx"

# df = analise_delta_sap_cao(path_df, path_analise, path_permit)


def comparar_ordens():
    os.system("cls")

    logo("Comparar CAO vs SAP")

    logger.info("Entre com o caminho do arquivo de report de Ordens")
    path_df = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo Análise CAO vs SAP")
    path_analise = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo do Permit")
    path_permit = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    dict_df = {"Análise": pd.DataFrame()}

    try:
        dict_df["Análise"] = analise_delta_sap_cao(path_df, path_analise, path_permit)

        data_atual = datetime.now().strftime("%Y_%m_%d")

        salvar_dict_df_em_excel(dict_df, f"{caminho_output}/Report_{data_atual}.xlsx")

    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
