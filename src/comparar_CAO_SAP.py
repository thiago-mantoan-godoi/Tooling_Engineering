import pandas as pd
import os
from datetime import datetime
from src.function import *
from src.extrair_cuts import *
import warnings

warnings.simplefilter("ignore")


def comparar_cao_vs_SAP(path_report, path_cao, path_sap, path_permit):
    dict_consolidado = {}

    df_report = pd.read_excel(path_report)
    df_CAO = pd.read_csv(path_cao, sep=";")
    df_SAP = pd.read_excel(path_sap)
    df_permit = pd.read_excel(path_permit)

    # Report CAO
    df_report = df_report[df_report["Type"] == "Order Feedback"][
        ["Text 02", "Text 15", "Quantity", "Transmission Time"]
    ].reset_index(drop=True)
    df_report.rename(
        columns={
            "Text 02": "Circuito",
            "Quantity": "Quantidade em Peças",
            "Text 15": "CAO Number",
        },
        inplace=True,
    )
    df_report = df_report[
        ["Circuito", "Quantidade em Peças", "CAO Number", "Transmission Time"]
    ]

    # Master data CAO
    df_CAO = df_CAO[df_CAO["ProdVersion"] == 0][
        ["Leadset", "Wire1Key", "Wire2Key", "Wire2Length", "Wire1Length"]
    ].reset_index(drop=True)

    dict_Length_cao = {
        row["Leadset"]: row["Wire1Length"] for i, row in df_CAO.iterrows()
    }
    dict_cabos_cao = {
        row["Leadset"]: ", ".join(
            [
                str(row["Wire1Key"]) if pd.notna(row["Wire1Key"]) else "",
                str(row["Wire2Key"]) if pd.notna(row["Wire2Key"]) else "",
            ]
        ).strip(", ")
        for _, row in df_CAO.iterrows()
    }

    # ZMM385
    leadset = df_SAP["Leadset"].unique().tolist()

    dict_cabos_sap = {}
    for i in leadset:
        df_prov = df_SAP[df_SAP["Leadset"] == i].reset_index(drop=True)
        try:
            dict_cabos_sap[df_prov.loc[0, "Leadset"]] = ", ".join(
                df_prov["WIRE_TUBE_SPLICE"].dropna().unique().tolist()
            )
        except:
            print(df_prov)

    df_tw = df_SAP[df_SAP["Comp TW"].notna()]
    df_diretos = df_SAP[df_SAP["Comp TW"].isna()]

    dict_Length_sap = {row["Leadset"]: row["Comp TW"] for i, row in df_tw.iterrows()}
    dict_Length_sap1 = {
        row["Leadset"]: row["LENGTH"] for i, row in df_diretos.iterrows()
    }

    dict_Length_sap.update(dict_Length_sap1)

    df_report["Part Number do Cabo [CAO]"] = df_report["Circuito"].map(dict_cabos_cao)
    df_report["Length [CAO]"] = df_report["Circuito"].map(dict_Length_cao)

    df_report["Part Number do Cabo [SAP]"] = df_report["Circuito"].map(dict_cabos_sap)
    df_report["Length [SAP]"] = df_report["Circuito"].map(dict_Length_sap)

    df_report["Delta"] = df_report["Length [CAO]"] - df_report["Length [SAP]"]

    df_report = df_report[df_report["Delta"] != 0].reset_index(drop=True)

    dict_permit = {
        row["Circuito"]: row["Permit Number"] for i, row in df_permit.iterrows()
    }
    dict_obs = {row["Circuito"]: row["Observações"] for i, row in df_permit.iterrows()}

    df_report["Permit Number"] = df_report["Circuito"].map(dict_permit)
    df_report["Observações"] = df_report["Circuito"].map(dict_obs)

    df_report = df_report[
        [
            "Transmission Time",
            "CAO Number",
            "Circuito",
            "Quantidade em Peças",
            "Part Number do Cabo [CAO]",
            "Length [CAO]",
            "Part Number do Cabo [SAP]",
            "Length [SAP]",
            "Delta",
            "Permit Number",
            "Observações",
        ]
    ]

    df_group = (
        df_report.groupby(["Circuito"], dropna=False)
        .agg(
            {
                "CAO Number": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),  # Converte para string
                "Quantidade em Peças": "sum",
                "Part Number do Cabo [CAO]": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),
                "Length [CAO]": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),
                "Part Number do Cabo [SAP]": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),
                "Length [SAP]": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),
                "Permit Number": lambda x: ", ".join(
                    sorted(set(x.dropna().astype(str)))
                ),
                "Observações": lambda x: ", ".join(sorted(set(x.dropna().astype(str)))),
            }
        )
        .reset_index()
    )
    df_group["Length [CAO]"] = pd.to_numeric(df_group["Length [CAO]"], errors="coerce")
    df_group["Length [SAP]"] = pd.to_numeric(df_group["Length [SAP]"], errors="coerce")
    df_group["Delta"] = df_group["Length [CAO]"] - df_group["Length [SAP]"]

    df_group = df_group[
        [
            "CAO Number",
            "Circuito",
            "Quantidade em Peças",
            "Part Number do Cabo [CAO]",
            "Length [CAO]",
            "Part Number do Cabo [SAP]",
            "Length [SAP]",
            "Delta",
            "Permit Number",
            "Observações",
        ]
    ]

    df_group = df_group[~df_group["Circuito"].str.startswith(("A", "X"))].reset_index(
        drop=True
    )

    lista_ckt = ["G28", "G33", "G34", "G35"]

    # Verifica se 'Circuito' contém qualquer valor de lista_ckt
    df_group = df_group[
        ~df_group["Circuito"].str.contains("|".join(lista_ckt), na=False)
    ].reset_index(drop=True)

    df_group = df_group[df_group["Length [CAO]"] > 1].reset_index(drop=True)

    dict_consolidado["Base de dados"] = df_report
    dict_consolidado["Report"] = df_group

    return dict_consolidado


def comparar():
    os.system("cls")

    logo("Comparar CAO vs SAP")

    logger.info("Entre com o caminho do arquivo de report de Ordens")
    path_report = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo Master Data CAO")
    path_cao = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo ZMM385")
    path_sap = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo Permit")
    path_permit = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    try:
        dict_df = comparar_cao_vs_SAP(path_report, path_cao, path_sap, path_permit)

        data_atual = datetime.now().strftime("%d_%m_%Y")

        salvar_dict_df_em_excel(dict_df, f"{caminho_output}/Report_{data_atual}.xlsx")

    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
