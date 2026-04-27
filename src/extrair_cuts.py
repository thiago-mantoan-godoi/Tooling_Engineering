import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from src.function import *
from art import *
from collections import Counter
import traceback
import warnings
import numpy as np


warnings.simplefilter("ignore")

#### FUNÇÕES
logger = LoggerTerminal(salvar_log=False, typing=True)


def format_cut(path):
    with open(path, "rb") as f:
        df = pd.read_excel(f)

    palavras = ["Wire Nb", "Mult.Wire Nb", "Splice Nb", "Sleeve Nb"]
    indices_linhas = procurar_indices_linhas(palavras, df)

    dict_df = {}

    for i in range(len(indices_linhas) - 1):
        index_1 = indices_linhas[i]
        index_2 = indices_linhas[i + 1]

        df_filtrado = df.loc[index_1 : index_2 - 1].reset_index(drop=True)

        novo_header = df_filtrado.iloc[0]
        df_novo = df_filtrado[1:].copy()
        df_novo.columns = novo_header
        df_novo.reset_index(drop=True, inplace=True)

        name = df_novo.columns[0].replace(" ", "_").replace(".", "")

        df_novo = (
            df_novo.dropna(how="all", axis=0)
            .dropna(how="all", axis=1)
            .reset_index(drop=True)
        )

        df_novo = renomear_colunas_duplicadas(df_novo)

        df_novo["Nome do arquivo"] = os.path.basename(path).replace(".xlsx", "")

        df_novo["Fase"] = os.path.basename(path).replace(".xlsx", "").split("_")[0]

        if name == "Wire_Nb":
            try:
                list_add = [
                    "Multicore",
                    "Term. 1",
                    "Term. 2",
                    "Seal 1",
                    "Seal 2",
                    "Joint 1",
                    "Joint 2",
                ]
                for l in list_add:
                    if l not in df_novo.columns:
                        df_novo[l] = None

                # Processos
                df_novo = adicionar_codigo_ucs(df_novo)
                df_novo = adicionar_processos(df_novo)
                df_novo = add_leadset_wire(df_novo)

                colunas_prioritarias = [
                    "Nome do arquivo",
                    "Fase",
                    "ProcessoA",
                    "ProcessoB",
                    "UCS",
                    "Leadset",
                ]
                df_novo = reordenar_colunas(df_novo, colunas_prioritarias)
            except Exception as err:
                logger.error(f"Erro reordenar colunas no {name}: {err}")
                traceback.print_exc()

            try:
                colunas_para_excluir = [
                    "Wire Spec",
                    "Pack",
                    "Options",
                    "Cav. 1",
                    "Cav. 2",
                    "Term.Mat 1",
                    "Term.Mat 2",
                ]
                #df_novo = excluir_colunas(df_novo, colunas_para_excluir)
            except Exception as err:
                logger.error(f"Erro excluir colunas no {name}: {err}")
                traceback.print_exc()

        if name == "MultWire_Nb":
            try:
                df_novo = adicionar_codigo_ucs(df_novo)
                colunas_prioritarias = [
                    "Nome do arquivo",
                    "Fase",
                    "UCS",
                    "Mult.Wire Nb",
                    "T",
                    "CSA",
                    "Length",
                    "Wire Spec",
                    "Pack",
                    "CutBack1",
                    "CutBack2",
                    "W1",
                    "W2",
                    "Int.PN",
                ]
                df_novo = reordenar_colunas(df_novo, colunas_prioritarias)
            except Exception as err:
                logger.error(f"Erro reordenar colunas no {name}: {err}")
                traceback.print_exc()

        if name == "Sleeve_Nb":
            try:
                df_novo = adicionar_codigo_ucs(df_novo)
                colunas_prioritarias = ["Nome do arquivo", "Fase", "UCS"]
                df_novo = reordenar_colunas(df_novo, colunas_prioritarias)
            except Exception as err:
                logger.error(f"Erro reordenar colunas no {name}: {err}")
                traceback.print_exc()

        if name == "Splice_Nb":
            try:
                df_novo = adicionar_codigo_ucs(df_novo)

                colunas = [
                    "L1",
                    "L2",
                    "L3",
                    "L4",
                    "L5",
                    "L6",
                    "L7",
                    "L8",
                    "L9",
                    "L10",
                    "R1",
                    "R2",
                    "R3",
                    "R4",
                    "R5",
                    "R6",
                    "R7",
                    "R8",
                    "R9",
                    "R10",
                ]

                for c in colunas:
                    if c not in df_novo.columns:
                        df_novo[c] = None

                colunas_prioritarias = [
                    "Nome do arquivo",
                    "Fase",
                    "UCS",
                    "Splice Nb",
                    "Int.PN",
                    "Extra Component PN",
                    "Pack",
                    "CSA Left",
                    "CSA Right",
                    "CSA Total",
                    "Node",
                    "L1",
                    "L2",
                    "L3",
                    "L4",
                    "L5",
                    "L6",
                    "L7",
                    "L8",
                    "L9",
                    "L10",
                    "R1",
                    "R2",
                    "R3",
                    "R4",
                    "R5",
                    "R6",
                    "R7",
                    "R8",
                    "R9",
                    "R10",
                ]
                df_novo = reordenar_colunas(df_novo, colunas_prioritarias)
            except Exception as err:
                logger.error(f"Erro reordenar colunas no {name}: {err}")
                traceback.print_exc()

        # if name.upper() == "MULTWIRE_NB" or ('Mult' in name and 'Wire' in name):
        #     colunas_prioritarias =['Mult.Wire Nb', 'T', 'CSA', 'Length', 'Wire Spec', 'Pack', 'CutBack1','CutBack2', 'W1', 'W2','Int.PN']
        #     df_novo = reordenar_colunas(df_novo, colunas_prioritarias)

        dict_df[name] = df_novo
    return dict_df

def format_Charted_cutsheet(path):
    nome_arquivo = os.path.basename(path).replace(".xlsx", "")

    with open(path, "rb") as f:
        df_Wire = pd.read_excel(f, sheet_name="Wire Sheet")

    with open(path, "rb") as f:
        df_Multicore = pd.read_excel(f, sheet_name="Multicore Sheet")

    with open(path, "rb") as f:
        df_Tube = pd.read_excel(f, sheet_name="Tube Sheet")

    with open(path, "rb") as f:
        df_Splice = pd.read_excel(f, sheet_name="Splice Sheet")

    with open(path, "rb") as f:
        df_Multicrimp = pd.read_excel(f, sheet_name="Multicrimp Sheet")

    if len(df_Wire) > 0:
        palavras = ["Wire Nb"]
        indices_linhas = procurar_indices_linhas(palavras, df_Wire)

        if len(indices_linhas) == 1:
            palavras = ["2D UCS"]
            indices_linhas = procurar_indices_linhas(palavras, df_Wire)

        df_Wire = df_Wire.loc[indices_linhas[0] : indices_linhas[1]].reset_index(
            drop=True
        )

        novo_header = df_Wire.iloc[0]
        df_Wire = df_Wire[1:].copy()
        df_Wire.columns = novo_header
        df_Wire.reset_index(drop=True, inplace=True)

        df_Wire["Nome do arquivo"] = nome_arquivo

        df_Wire = adicionar_codigo_ucs(df_Wire,coluna_tag='2D UCS')
        df_Wire = adicionar_processos(df_Wire)
        df_Wire = add_leadset_wire(df_Wire)

        colunas = [
            "Nome do arquivo",
            "ProcessoA",
            "ProcessoB",
            "UCS",
            "Leadset",
            "Wire Nb",
            "Multicore",
            "Sub-Assembly",
            "Wire Type",
            "Unm. Length",
            "Length Type",
            "Offset Value",
            "Total Length",
            "Color",
            "Int.PN",
            "Mat Code",
            "Wire Spec",
            "CSA",
            "Options/Modules",
            "Strip 1",
            "Term. 1",
            "Term. 1 Cust",
            "Term.Mat 1",
            "Seal 1",
            "Seal 1 Cust",
            "Node 1",
            "Joint 1",
            "Connector 1 Cust. PN",
            "Cav. 1",
            "Note 1",
            "Strip 2",
            "Term. 2",
            "Term. 2 Cust",
            "Term.Mat 2",
            "Seal 2",
            "Seal 2 Cust",
            "Node 2",
            "Joint 2",
            "Connector 2 Cust. PN",
            "Cav. 2",
            "Note 2",
            "Joint Type",
            "Wire Usage",
        ]

        df_Wire = reordenar_colunas(df_Wire, colunas)

        colunas_dell = [
            "Length Type",
            "Offset Value",
            "Total Length",
            "Mat Code",
            "Term. 1 Cust",
            "Term.Mat 1",
            "Term. 2 Cust",
            "Term.Mat 2",
            "Options/Modules",
            "Seal 1 Cust",
            "Connector 1 Cust. PN",
            "Cav. 1",
            "Seal 2 Cust",
            "Connector 2 Cust. PN",
            "Cav. 2",
            "Wire Usage",
            "Circuit Klima",
            "Term 1 Klima",
            "Seal 1 Klima",
            "Node 1 Klima",
            "Term 2 Klima",
            "Seal 2 Klima",
            "Node 2Klima",
            "2D UCS",
            "FAMILIA",
        ]

        df_Wire = df_Wire.drop(
            columns=[col for col in colunas_dell if col in df_Wire.columns]
        )

    else:
        df_Wire = pd.DataFrame()

    if len(df_Multicore) > 0:
        palavras = ["Mult.Wire Nb"]
        indices_linhas = procurar_indices_linhas(palavras, df_Multicore)
        df_Multicore = df_Multicore.loc[
            indices_linhas[0] : indices_linhas[1]
        ].reset_index(drop=True)

        novo_header = df_Multicore.iloc[0]
        df_Multicore = df_Multicore[1:].copy()
        df_Multicore.columns = novo_header
        df_Multicore.reset_index(drop=True, inplace=True)

        df_Multicore["Nome do arquivo"] = nome_arquivo

        df_Multicore = adicionar_codigo_ucs(df_Multicore)

        colunas = ["Nome do arquivo","UCS","Mult.Wire Nb","Wire Type","Length","Int.PN","Wire Spec","Inc.BOM",
                   "Inc.Chart","CutBack1","CutBack2","W1","W2","W3","W4"]

        df_Multicore = reordenar_colunas(df_Multicore, colunas)
    else:
        df_Multicore = pd.DataFrame()

    if len(df_Tube) > 0:
        palavras = ["Sleeve Nb"]
        indices_linhas = procurar_indices_linhas(palavras, df_Tube)
        df_Tube = df_Tube.loc[indices_linhas[0] : indices_linhas[1]].reset_index(
            drop=True
        )

        novo_header = df_Tube.iloc[0]
        df_Tube = df_Tube[1:].copy()
        df_Tube.columns = novo_header
        df_Tube.reset_index(drop=True, inplace=True)

        df_Tube["Nome do arquivo"] = nome_arquivo

        df_Tube = adicionar_codigo_ucs(df_Tube)

        colunas = ["Nome do arquivo", "UCS","Sleeve Nb","Int.PN","Length","Cut-back","Insulated Length","Type",
                   "Note","Description","Mater","Type","Int.Diameter","Group","Color","Slit","Conv","Wall Th.",
                   "Layer","Node 1","Node 2"]

        df_Tube = reordenar_colunas(df_Tube, colunas)


        colunas_dell = ['Klima','Type_2','Type_3']
        df_Tube = df_Tube.drop(
            columns=[col for col in colunas_dell if col in df_Tube.columns]
        )

    else:
        df_Tube = pd.DataFrame()

    if len(df_Splice) > 0:
        palavras = ["Splice Name"]
        indices_linhas = procurar_indices_linhas(palavras, df_Splice)
        df_Splice = df_Splice.loc[indices_linhas[0] : indices_linhas[1]].reset_index(
            drop=True
        )

        novo_header = df_Splice.iloc[0]
        df_Splice = df_Splice[1:].copy()
        df_Splice.columns = novo_header
        df_Splice.reset_index(drop=True, inplace=True)

        df_Splice["Nome do arquivo"] = nome_arquivo

        df_Splice = adicionar_codigo_ucs(df_Splice)

        colunas = [
            "Nome do arquivo",
            "UCS",
            "Splice Name",
            "Int.PN",
            "Extra Component PN",
            "CSA Left",
            "CSA Right",
            "CSA Total",
            "X1",
            "X2",
            "X3",
            "X4",
            "X5",
            "X6",
            "X7",
            "X8",
            "X9",
            "X10",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L7",
            "L8",
            "L9",
            "L10",
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7",
            "R8",
            "R9",
            "R10",
        ]

        df_Splice = reordenar_colunas(df_Splice, colunas)

        colunas_dell = ['Klima']
        df_Splice = df_Splice.drop(
            columns=[col for col in colunas_dell if col in df_Splice.columns]
        )

        df_Splice = df_Splice.dropna(how='all',axis=1)

    else:
        df_Splice = pd.DataFrame()

    if len(df_Multicrimp) > 0:
        palavras = ["M. Crimp Name"]
        indices_linhas = procurar_indices_linhas(palavras, df_Multicrimp)
        df_Multicrimp = df_Multicrimp.loc[
            indices_linhas[0] : indices_linhas[1]
        ].reset_index(drop=True)

        novo_header = df_Multicrimp.iloc[0]
        df_Multicrimp = df_Multicrimp[1:].copy()
        df_Multicrimp.columns = novo_header
        df_Multicrimp.reset_index(drop=True, inplace=True)

        df_Multicrimp["Nome do arquivo"] = nome_arquivo

        df_Multicrimp = adicionar_codigo_ucs(df_Multicrimp)

        colunas = [
            "Nome do arquivo",
            "UCS",
            "M. Crimp Name",
            "Extra Component PN",
            "Terminal",
            "CSA Total",
            "Node",
            "W1",
            "W2",
            "W3",
            "W4",
            "W5",
            "W6",
            "W7",
            "W8",
            "W9",
            "W10",
            "W11",
            "W12",
            "W13",
            "W14",
            "W15",
            "W16",
            "W17",
            "W18",
            "W19",
            "W20",
        ]
        df_Multicrimp = reordenar_colunas(df_Multicrimp, colunas)
        
        colunas_dell = ['Klima']
        df_Multicrimp = df_Multicrimp.drop(
            columns=[col for col in colunas_dell if col in df_Multicrimp.columns]
        )

        df_Multicrimp = df_Multicrimp.dropna(how='all',axis=1)

    else:
        df_Multicrimp = pd.DataFrame()

    dict_df = {
        "Wire_Nb": df_Wire,
        "MultWire_Nb": df_Multicore,
        "Sleeve_Nb": df_Tube,
        "Splice_Nb": df_Splice,
        "Multicrimp_Nb": df_Multicrimp,
    }

    return dict_df

def check_usar_21(df_wire):
    if "Seal 1" not in df_wire:
        df_wire["Seal 1"] = None
    if "Seal 2" not in df_wire:
        df_wire["Seal 2"] = None

    df_path_cabos = consultar_arquivos_base(id_name="Lista_de_cabos")
    with open(df_path_cabos, "rb") as f:
        df_book = pd.read_excel(f)
        
    df_path_cabos = consultar_arquivos_base(id_name="Lista_de_cabos_com_legacy")
    with open(df_path_cabos, "rb") as f:
        df_book = pd.read_excel(f,dtype=str)

    # df_spec_cabos = convert_legacy(df_book)
    # dict_tipos = {
    #     row["Part Number"]: row["Legacy"] for i, row in df_spec_cabos.iterrows()
    # }
    
    dict_tipos = {
        row["Part Number"]: row["Legacy"] for i, row in df_book.iterrows()
    }

    df_path = consultar_arquivos_base(id_name="lista_app")
    with open(df_path, "rb") as f:
        df_spec = pd.read_excel(f, sheet_name="Crimpagem Access")[
            ["CHP", "Relatório", "Terminal", "Bitola", "Isolação", "Selo"]
        ].astype(str)

    # Duplicando --------------------------------------------------------------------------------------------------------------------------
    iso = ["65766", "65860", "65927"]
    duplicated_rows = []  # Para armazenar as duplicatas

    # Loop para percorrer cada linha do DataFrame
    for i in df_spec.index:
        isolacao_value = df_spec.at[i, "Isolação"]

        # Se o valor de 'Isolação' estiver na lista 'iso'
        if isolacao_value in iso:
            # Para cada valor em 'iso', exceto o valor encontrado
            for item in iso:
                if isolacao_value != item:
                    # Faz uma cópia da linha original
                    duplicated_row = df_spec.loc[[i]].copy()
                    # Altera o valor de 'Isolação' para o valor atual da lista
                    duplicated_row["Isolação"] = item
                    # Adiciona a linha duplicada à lista
                    duplicated_rows.append(duplicated_row)

    # Agora adiciona as duplicatas ao DataFrame original
    df_spec = pd.concat([df_spec] + duplicated_rows, ignore_index=True)

    df_spec = df_spec.reset_index(drop=True)

    df_spec = df_spec.drop_duplicates(
        subset=["CHP", "Relatório", "Terminal", "Bitola", "Isolação", "Selo"]
    ).reset_index(drop=True)

    # Duplicando --------------------------------------------------------------------------------------------------------------------------

    df_spec = df_spec[
        (df_spec["Relatório"].str.contains("USCAR|BR", na=False))
        & (
            ~df_spec["Relatório"].str.contains(
                "PERM|perm|PROV|desvio|DESVIO|Desvio", na=False
            )
        )
    ].reset_index(drop=True)

    df_spec["Bitola"] = df_spec["Bitola"].replace(",", ".", regex=True)

    for (
        i,
        row,
    ) in df_spec.iterrows():  # Usando iterrows para obter as linhas e seus índices
        bitola = str(row["Bitola"])

        # Separa os valores por '+'
        valores = bitola.split("+")

        # Definindo valor1, valor2 e valor3
        valor1 = valores[0]
        valor2 = valores[1] if len(valores) > 1 else None
        valor3 = valores[2] if len(valores) > 2 else None

        # Formata valor1
        if len(valor1) < 4:
            valor1 = f"{float(valor1):.2f}"

        # Formata valor2 (se existir)
        if valor2 and len(valor2) < 4:
            valor2 = f"{float(valor2):.2f}"

        # Formata valor3 (se existir)
        if valor3 and len(valor3) < 4:
            valor3 = f"{float(valor3):.2f}"

        # Monta a nova bitola considerando os valores
        if valor3:
            df_spec.at[i, "Bitola"] = f"{valor1}+{valor2}+{valor3}"
        elif valor2:
            df_spec.at[i, "Bitola"] = f"{valor1}+{valor2}"
        else:
            df_spec.at[i, "Bitola"] = valor1

    if "Joint 1" not in df_wire.columns:
        df_wire["Joint 1"] = None
    if "Joint 2" not in df_wire.columns:
        df_wire["Joint 2"] = None

    list_de_circuitos = df_wire["Wire Nb"].unique()
    list_de_circuitos = pd.DataFrame(list_de_circuitos, columns=["Circuitos"])
    list_de_circuitos["ID"] = range(len(list_de_circuitos))
    dict_ckt = {row["Circuitos"]: row["ID"] for i, row in list_de_circuitos.iterrows()}
    dict_ckt_inv = {
        row["ID"]: row["Circuitos"] for i, row in list_de_circuitos.iterrows()
    }

    dict_wire = {row["Wire Nb"]: row["Int.PN"] for i, row in df_wire.iterrows()}
    dict_csa = {row["Wire Nb"]: row["CSA"] for i, row in df_wire.iterrows()}
    dict_term1 = {row["Wire Nb"]: row["Term. 1"] for i, row in df_wire.iterrows()}
    dict_term2 = {row["Wire Nb"]: row["Term. 2"] for i, row in df_wire.iterrows()}
    dict_selo1 = {row["Wire Nb"]: row["Seal 1"] for i, row in df_wire.iterrows()}
    dict_selo2 = {row["Wire Nb"]: row["Seal 2"] for i, row in df_wire.iterrows()}

    df_1 = df_wire[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Wire Nb",
            "CSA",
            "Joint 1",
            "Int.PN",
            "Term. 1",
            "Seal 1",
        ]
    ].rename(columns={"Joint 1": "Wire Nb_2", "Term. 1": "Term", "Seal 1": "Seal"})
    df_2 = df_wire[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Wire Nb",
            "CSA",
            "Joint 2",
            "Int.PN",
            "Term. 2",
            "Seal 2",
        ]
    ].rename(columns={"Joint 2": "Wire Nb_2", "Term. 2": "Term", "Seal 2": "Seal"})

    df_1["Int.PN_2"] = df_1["Wire Nb_2"].map(dict_wire)
    df_1["CSA_2"] = df_1["Wire Nb_2"].map(dict_csa)
    df_1["Term_2"] = df_1["Wire Nb_2"].map(dict_term1)
    df_1["Selo_2"] = df_1["Wire Nb_2"].map(dict_selo1)

    df_2["Int.PN_2"] = df_2["Wire Nb_2"].map(dict_wire)
    df_2["CSA_2"] = df_2["Wire Nb_2"].map(dict_csa)
    df_2["Term_2"] = df_2["Wire Nb_2"].map(dict_term2)
    df_2["Selo_2"] = df_2["Wire Nb_2"].map(dict_selo2)

    df_completo = pd.concat([df_1, df_2], ignore_index=False)

    df_completo = df_completo[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Wire Nb",
            "Wire Nb_2",
            "CSA",
            "CSA_2",
            "Int.PN",
            "Int.PN_2",
            "Term",
            "Term_2",
            "Seal",
            "Selo_2",
        ]
    ]

    df_completo["Wire Nb_ID"] = df_completo["Wire Nb"].map(dict_ckt)
    df_completo["Wire Nb_2_ID"] = df_completo["Wire Nb_2"].map(dict_ckt).fillna(1000)

    df_completo = df_completo.reset_index(drop=True)
    df_completo["Wire Nb_ID_Inv"] = None
    df_completo["Wire Nb_2_ID_Inv"] = None

    for i in df_completo.index:
        var1 = int(df_completo.at[i, "Wire Nb_ID"])
        var2 = int(df_completo.at[i, "Wire Nb_2_ID"])
        if var1 > var2:
            df_completo.at[i, "Wire Nb_ID_Inv"] = var2
            df_completo.at[i, "Wire Nb_2_ID_Inv"] = var1
        else:
            df_completo.at[i, "Wire Nb_ID_Inv"] = var1
            df_completo.at[i, "Wire Nb_2_ID_Inv"] = var2

    df_completo["Wire Nb_inv"] = df_completo["Wire Nb_ID_Inv"].map(dict_ckt_inv)
    df_completo["Wire Nb_2_inv"] = (
        df_completo["Wire Nb_2_ID_Inv"].map(dict_ckt_inv).fillna("")
    )
    df_completo.drop(
        columns=["Wire Nb_ID", "Wire Nb_2_ID", "Wire Nb_ID_Inv", "Wire Nb_2_ID_Inv"],
        inplace=True,
    )

    df_completo["Circuito"] = None
    df_completo["Comentários"] = None

    for i in df_completo.index:
        if pd.notna(df_completo.at[i, "Int.PN_2"]):
            df_completo.at[i, "Circuito"] = (
                str(df_completo.at[i, "Wire Nb_inv"])
                + ", "
                + str(df_completo.at[i, "Wire Nb_2_inv"])
            )
            df_completo.at[i, "Comentários"] = "Double crimp"
        elif pd.notna(df_completo.at[i, "Int.PN"]) and pd.isna(
            df_completo.at[i, "Int.PN_2"]
        ):
            df_completo.at[i, "Circuito"] = str(df_completo.at[i, "Wire Nb_inv"])
            df_completo.at[i, "Comentários"] = "Single Crimp"
        elif pd.isna(df_completo.at[i, "Int.PN_2"]):
            df_completo.at[i, "Circuito"] = None

    df_completo.drop(
        columns=["Wire Nb_inv", "Wire Nb_2_inv", "Wire Nb", "Wire Nb_2"], inplace=True
    )

    df_completo = df_completo[(~df_completo["Int.PN"].isna())].reset_index(drop=True)

    df_completo = df_completo[(~df_completo["Term"].isna())].reset_index(drop=True)

    df_completo = df_completo[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Circuito",
            "Int.PN",
            "Int.PN_2",
            "CSA",
            "CSA_2",
            "Term",
            "Term_2",
            "Seal",
            "Selo_2",
            "Comentários",
        ]
    ]

    df_completo = df_completo.reset_index(drop=True)

    df_completo["CSA_New"] = None

    for i in df_completo.index:
        csa1 = df_completo.at[i, "CSA"]
        csa2 = df_completo.at[i, "CSA_2"]

        if pd.notna(csa1) and pd.notna(csa2):
            df_completo.at[i, "CSA_New"] = f"{csa1}+{csa2}"
        elif pd.notna(csa1) and pd.isna(csa2):
            df_completo.at[i, "CSA_New"] = csa1

        if df_completo.at[i, "Term"] == df_completo.at[i, "Term_2"]:
            df_completo.at[i, "Term_2"] = None

    if df_completo["Term_2"].notna().sum() == 0:
        df_completo.drop(columns=["Term_2"], inplace=True)
    if df_completo["Selo_2"].notna().sum() == 0:
        df_completo.drop(columns=["Selo_2"], inplace=True)

    df_completo = df_completo.drop(columns=["CSA", "CSA_2"]).rename(
        columns={"CSA_New": "CSA", "Int.PN": "Tipo Cabo 1", "Int.PN_2": "Tipo Cabo 2"}
    )

    df_completo = df_completo.reset_index(drop=True)
    df_completo["Legacy 1"] = df_completo["Tipo Cabo 1"].map(dict_tipos)
    df_completo["Legacy 2"] = df_completo["Tipo Cabo 2"].map(dict_tipos)

    df_completo = df_completo[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Circuito",
            "Tipo Cabo 1",
            "Tipo Cabo 2",
            "Legacy 1",
            "Legacy 2",
            "CSA",
            "Term",
            "Seal",
            "Comentários",
        ]
    ]

    df_completo["Relatório"] = None
    df_completo["Tipo de validação"] = None

    df_completo = df_completo.reset_index(drop=True)

    for i in df_completo.index:
        term = df_completo.at[i, "Term"]
        csa = df_completo.at[i, "CSA"]

        list_csa = str(csa).split("+")

        if len(list_csa[0]) < 4:
            list_csa[0] = f"{float(list_csa[0]):.2f}"

        try:
            if len(list_csa[1]) < 4:
                list_csa[1] = f"{float(list_csa[1]):.2f}"
        except:
            pass

        Legacy = df_completo.at[i, "Legacy 1"]
        Seal = df_completo.at[i, "Seal"]

        if pd.isna(Seal):
            Seal = ""

        lista_interna = []
        lista_externa = []

        for j in df_spec.index:
            list_csa1 = str(df_spec.at[j, "Bitola"]).split("+")

            if len(list_csa1[0]) < 4:
                list_csa1[0] = f"{float(list_csa1[0]):.2f}"

            try:
                if len(list_csa1[1]) < 4:
                    list_csa1[1] = f"{float(list_csa1[1]):.2f}"
            except:
                pass

            if (
                df_spec.at[j, "Terminal"] == term
                and Counter(list_csa1) == Counter(list_csa)
                and str(df_spec.at[j, "Isolação"]) == str(Legacy)
            ):
                lista_externa.append(df_spec.at[j, "Relatório"])
            if (
                df_spec.at[j, "Terminal"] == term
                and Counter(list_csa1) == Counter(list_csa)
                and str(df_spec.at[j, "Isolação"]) == str(Legacy)
                and str(df_spec.at[j, "Selo"]) == str(Seal)
            ):
                lista_interna.append(df_spec.at[j, "Relatório"])

        df_completo.at[i, "Relatório - Interno"] = ", ".join(lista_interna)
        df_completo.at[i, "Relatório - Externo"] = ", ".join(lista_externa)

        def safe_str(value):
            if pd.isna(value) or value is None:
                return ""
            return str(value).replace(" ", "")

        interno = safe_str(df_completo.at[i, "Relatório - Interno"])
        seal = safe_str(df_completo.at[i, "Seal"])
        externo = safe_str(df_completo.at[i, "Relatório - Externo"])

        if (interno != "" and seal != "" and externo != "") or (
            interno == "" and seal == "" and externo != ""
        ):
            df_completo.at[i, "Tipo de validação"] = "Validação OK"

        elif interno == "" and seal == "" and externo == "":
            df_completo.at[i, "Tipo de validação"] = (
                "Validação Mecânica, Validação Externa (USCAR21)"
            )

        elif interno == "" and seal != "" and externo != "":
            df_completo.at[i, "Tipo de validação"] = (
                "Validação Mecânica, Validação interna (Selo)"
            )

        elif interno == "" and seal != "" and externo == "":
            df_completo.at[i, "Tipo de validação"] = (
                "Validação Mecânica, Validação interna (Selo), Validação externa (USCAR21)"
            )

    df_completo = df_completo[
        df_completo["Tipo de validação"] != "Validação OK"
    ].reset_index(drop=True)

    df_completo = df_completo.drop_duplicates().reset_index(drop=True)

    df_grouped = (
        df_completo.groupby(
            ["Tipo Cabo 1", "Tipo Cabo 2", "Term", "Seal"], dropna=False
        )
        .agg(
            {
                "Circuito": lambda x: ", ".join(
                    map(str, sorted(set(x)))
                ),  # junta os circuitos
                "Legacy 1": lambda x: ", ".join(sorted(map(str, set(x.dropna())))),
                "Legacy 2": lambda x: ", ".join(sorted(map(str, set(x.dropna())))),
                "CSA": lambda x: ", ".join(map(str, sorted(set(x.dropna())))),
                "Comentários": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Relatório": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Tipo de validação": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Relatório - Interno": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Relatório - Externo": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Nome do arquivo": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Fase": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Leadset": lambda x: ", ".join(sorted(set(x.dropna()))),
            }
        )
        .reset_index()
    )

    df_grouped = df_grouped[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Circuito",
            "Tipo Cabo 1",
            "Tipo Cabo 2",
            "Legacy 1",
            "Legacy 2",
            "CSA",
            "Term",
            "Seal",
            "Comentários",
            "Tipo de validação",
            "Relatório - Interno",
            "Relatório - Externo",
        ]
    ]

    df_grouped = df_grouped.sort_values(
        by=["Tipo Cabo 1", "Tipo Cabo 2", "Term", "Seal"]
    ).reset_index(drop=True)

    return df_grouped

def Check_splices(df_splice, df_wire):
    # ----------------------------------------------------------------------------------------------------------------------------------------

    df_path = consultar_arquivos_base(id_name="Uscar_38_45_GMW")

    with open(df_path, "rb") as f:
        df_temp = pd.read_excel(f, sheet_name="Controle", header=None)

    df_temp.columns = df_temp.iloc[1]
    df_uscar_45 = df_temp.drop([0, 1]).reset_index(drop=True)

    df_uscar_45.columns = df_uscar_45.columns.astype(str)

    df_uscar_45 = renomear_colunas(df_uscar_45)

    df_uscar_45.rename(columns={"CÓDIGO_2": "Número", "TERMO": "Termo"}, inplace=True)
    colunas_L = [
        "0.35",
        "0.5",
        "0.75",
        "1.0",
        "1.5",
        "2.0",
        "2.5",
        "3.0",
        "4.0",
        "5.0",
        "6.0",
        "8.0",
        "10.0",
        "16.0",
        "25.0",
        "30.0",
        "35.0",
    ]
    colunas_R = [
        "0.35_2",
        "0.5_2",
        "0.75_2",
        "1.0_2",
        "1.5_2",
        "2.0_2",
        "2.5_2",
        "3.0_2",
        "4.0_2",
        "5.0_2",
        "6.0_2",
        "8.0_2",
        "10.0_2",
        "16.0_2",
        "25.0_2",
        "30.0_2",
        "35.0_2",
    ]

    colunas_completares = ["Número", "Termo"]

    colunas_consolidadas = colunas_completares + colunas_L + colunas_R

    df_uscar_45 = df_uscar_45[colunas_consolidadas]

    df_uscar_45["Número"].fillna("Sem numéro de relatório", inplace=True)

    df_uscar_45[colunas_L + colunas_R] = (
        df_uscar_45[colunas_L + colunas_R].fillna(0).astype(int)
    )

    df_uscar_45 = df_uscar_45.drop_duplicates().reset_index(drop=True)
    # ----------------------------------------------------------------------------------------------------------------------------------------

    dict_wire = {str(row["Wire Nb"]): row["CSA"] for i, row in df_wire.iterrows()}

    df_splice = df_splice.dropna(how="all", axis=1).reset_index(drop=True)
    df_splice = df_splice.dropna(how="all", axis=0).reset_index(drop=True)

    colunas_add = [
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        "L10",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9",
        "R10",
    ]

    for c in colunas_add:
        if c not in df_splice.columns:
            df_splice[c] = None

    colunas = [
        "Nome do arquivo",
        "Fase",
        "UCS",
        "Splice Nb",
        "Int.PN",
        "Extra Component PN",
        "Pack",
        "CSA Left",
        "CSA Right",
        "CSA Total",
        "Node",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        "L10",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9",
        "R10",
    ]

    df_splice = reordenar_colunas(df_splice, colunas)

    def map_wire(x):
        # Se for None ou NaN
        if x is None or pd.isna(x):
            return None

        # Normaliza para string
        x_str = str(x).strip()

        # Se depois de strip ficou vazio, trata como None
        if x_str == "":
            return None

        # Verifica se está no dicionário
        if x_str in dict_wire:
            return dict_wire[x_str]

        return "Valor não mapeado"

    for c in colunas_add:
        df_splice[str(c) + "_CSA"] = df_splice[c].apply(map_wire)

    # for c in colunas_add:
    #     for i in df_splice.index:
    #         df_splice[str(c)+'_CSA'] = df_splice[c].map(dict_wire).fillna("Valor não encontrado!")

    colunas_left = [
        "L1_CSA",
        "L2_CSA",
        "L3_CSA",
        "L4_CSA",
        "L5_CSA",
        "L6_CSA",
        "L7_CSA",
        "L8_CSA",
        "L9_CSA",
        "L10_CSA",
    ]
    colunas_right = [
        "R1_CSA",
        "R2_CSA",
        "R3_CSA",
        "R4_CSA",
        "R5_CSA",
        "R6_CSA",
        "R7_CSA",
        "R8_CSA",
        "R9_CSA",
        "R10_CSA",
    ]

    colunas_check = [
        "count_left_0.35",
        "count_left_0.50",
        "count_left_0.75",
        "count_left_1.00",
        "count_left_1.50",
        "count_left_2.00",
        "count_left_2.50",
        "count_left_3.00",
        "count_left_4.00",
        "count_left_5.00",
        "count_left_6.00",
        "count_left_8.00",
        "count_left_10.00",
        "count_left_16.00",
        "count_left_25.00",
        "count_left_30.00",
        "count_left_35.00",
        "count_right_0.35",
        "count_right_0.50",
        "count_right_0.75",
        "count_right_1.00",
        "count_right_1.50",
        "count_right_2.00",
        "count_right_2.50",
        "count_right_3.00",
        "count_right_4.00",
        "count_right_5.00",
        "count_right_6.00",
        "count_right_8.00",
        "count_right_10.00",
        "count_right_16.00",
        "count_right_25.00",
        "count_right_30.00",
        "count_right_35.00",
    ]
    for col in colunas_check:
        df_splice[col] = 0

    colunas = [
        "Nome do arquivo",
        "Fase",
        "UCS",
        "Splice Nb",
        "Int.PN",
        "Extra Component PN",
        "Pack",
        "CSA Left",
        "CSA Right",
        "CSA Total",
        "Node",
        "L1",
        "L2",
        "L3",
        "L4",
        "L5",
        "L6",
        "L7",
        "L8",
        "L9",
        "L10",
        "R1",
        "R2",
        "R3",
        "R4",
        "R5",
        "R6",
        "R7",
        "R8",
        "R9",
        "R10",
        "L1_CSA",
        "L2_CSA",
        "L3_CSA",
        "L4_CSA",
        "L5_CSA",
        "L6_CSA",
        "L7_CSA",
        "L8_CSA",
        "L9_CSA",
        "L10_CSA",
        "R1_CSA",
        "R2_CSA",
        "R3_CSA",
        "R4_CSA",
        "R5_CSA",
        "R6_CSA",
        "R7_CSA",
        "R8_CSA",
        "R9_CSA",
        "R10_CSA",
    ] + colunas_check

    df_splice = reordenar_colunas(df_splice, colunas)

    for i in df_splice.index:
        # pega a linha e remove colunas vazias
        df_prov_left = df_splice.iloc[i : i + 1][colunas_left].dropna(how="all", axis=1)
        df_prov_right = df_splice.iloc[i : i + 1][colunas_right].dropna(
            how="all", axis=1
        )

        # conta ocorrências
        resultados_left = df_prov_left.apply(lambda row: row.value_counts(), axis=1)
        resultados_right = df_prov_right.apply(lambda row: row.value_counts(), axis=1)

        # renomeia colunas para indicar que são contagens
        resultados_left.columns = [f"count_left_{c}" for c in resultados_left.columns]
        resultados_right.columns = [
            f"count_right_{c}" for c in resultados_right.columns
        ]

        # Corrigindo nomes das colunas com tratamento de erro
        # resultados_left.columns = [
        #     f"count_left_{float(c):.2f}" if isinstance(c, (int, float)) or (isinstance(c, str) and c.replace('.', '', 1).isdigit())
        #     else f"count_left_{c}"
        #     for c in resultados_left.columns
        # ]

        # resultados_right.columns = [
        #     f"count_right_{float(c):.2f}" if isinstance(c, (int, float)) or (isinstance(c, str) and c.replace('.', '', 1).isdigit())
        #     else f"count_right_{c}"
        #     for c in resultados_right.columns
        # ]

        # junta no df_splice (mesma linha)
        df_splice.loc[i, resultados_left.columns] = resultados_left.iloc[0]
        df_splice.loc[i, resultados_right.columns] = resultados_right.iloc[0]

    # USCAR 45 e GMW -------------------------------------------------------------------------------------------------------------
    colunas_splice_L = [
        "count_left_0.35",
        "count_left_0.50",
        "count_left_0.75",
        "count_left_1.00",
        "count_left_1.50",
        "count_left_2.00",
        "count_left_2.50",
        "count_left_3.00",
        "count_left_4.00",
        "count_left_5.00",
        "count_left_6.00",
        "count_left_8.00",
        "count_left_10.00",
        "count_left_16.00",
        "count_left_25.00",
        "count_left_30.00",
        "count_left_35.00",
    ]
    colunas_splice_R = [
        "count_right_0.35",
        "count_right_0.50",
        "count_right_0.75",
        "count_right_1.00",
        "count_right_1.50",
        "count_right_2.00",
        "count_right_2.50",
        "count_right_3.00",
        "count_right_4.00",
        "count_right_5.00",
        "count_right_6.00",
        "count_right_8.00",
        "count_right_10.00",
        "count_right_16.00",
        "count_right_25.00",
        "count_right_30.00",
        "count_right_35.00",
    ]

    df_splice["USCAR_45"] = None
    df_splice["GMW17136"] = None

    for i in tqdm(
        df_splice.index, "[+] Adicionando USCAR 45 e GMW17136...", colour="Blue"
    ):
        valor = df_splice.at[i, "Extra Component PN"]
        termo = [v.strip() for v in str(valor).split(";")]
        string_L = ", ".join(
            map(str, df_splice.iloc[i : i + 1][colunas_splice_L].values[0].tolist())
        )
        string_R = ", ".join(
            map(str, df_splice.iloc[i : i + 1][colunas_splice_R].values[0].tolist())
        )
        string_L_check = ", ".join(
            map(str, df_splice.iloc[i : i + 1][colunas_left].values[0].tolist())
        )
        string_R_check = ", ".join(
            map(str, df_splice.iloc[i : i + 1][colunas_right].values[0].tolist())
        )

        for j in df_uscar_45.index:
            number = df_uscar_45.at[j, "Número"]
            valor_vd = df_uscar_45.at[j, "Termo"]
            termo_vd = [v.strip() for v in str(valor_vd).split(",")]
            string_L_vd = ", ".join(
                map(str, df_uscar_45.iloc[j : j + 1][colunas_L].values[0].tolist())
            )
            string_R_vd = ", ".join(
                map(str, df_uscar_45.iloc[j : j + 1][colunas_R].values[0].tolist())
            )

            if (
                "Valor não mapeado" not in string_L_check
                and "Valor não mapeado" not in string_R_check
            ):
                if (string_L == string_L_vd and string_R == string_R_vd) or (
                    string_L == string_R_vd and string_R == string_L_vd
                ):
                    # pega o valor atual da célula
                    valor_atual = df_splice.at[i, "USCAR_45"]

                    # se já existe algo, concatena com vírgula
                    if pd.notna(valor_atual) and valor_atual != "":
                        df_splice.at[i, "USCAR_45"] = f"{valor_atual}, {number}"
                    else:
                        df_splice.at[i, "USCAR_45"] = str(number)

                    for t in termo:
                        if t in termo_vd:
                            valor_termo = df_splice.at[i, "GMW17136"]

                            if pd.notna(valor_termo) and valor_termo != "":
                                df_splice.at[i, "GMW17136"] = f"{valor_termo}, {number}"
                            else:
                                df_splice.at[i, "GMW17136"] = str(number)
                            break

    df_45 = df_splice[(df_splice["USCAR_45"].isna())].reset_index(drop=True)
    df_gmw = df_splice[(df_splice["GMW17136"].isna())].reset_index(drop=True)

    df_45["USCAR_45"] = df_45["USCAR_45"].fillna("Sem validação")
    df_45["GMW17136"] = df_45["GMW17136"].fillna("Sem validação")

    df_gmw["USCAR_45"] = df_gmw["USCAR_45"].fillna("Sem validação")
    df_gmw["GMW17136"] = df_gmw["GMW17136"].fillna("Sem validação")

    return df_splice, df_45, df_gmw

def resumo_uscar21(df_wire):
    df_wire = df_wire[(df_wire["Tipo de validação"] != "Validação OK")].reset_index(
        drop=True
    )

    df_wire = df_wire[(df_wire["Tipo de validação"] != "Validação OK")].reset_index(
        drop=True
    )

    df_prov = df_wire.groupby(["Term", "CSA"], as_index=False).agg(
        {
            "Legacy 1": "first",
            "Seal": "first",
            "Circuito": lambda x: ",".join(dict.fromkeys(map(str, x))),
            "Tipo de validação": lambda x: ",".join(dict.fromkeys(map(str, x))),
        }
    )

    vm = df_prov[df_prov["Tipo de validação"].str.contains("Validação Mecânica")][
        "Tipo de validação"
    ].count()
    vs = df_prov[df_prov["Tipo de validação"].str.contains("Validação interna")][
        "Tipo de validação"
    ].count()
    vu = df_prov[df_prov["Tipo de validação"].str.contains("Validação Externa")][
        "Tipo de validação"
    ].count()

    return df_prov, vm, vs, vu

def renomear_colunas(df):
    # Criar um dicionário para contar as ocorrências dos nomes das colunas
    colunas_renomeadas = {}

    for i, col in enumerate(df.columns):
        # Verifica se o nome da coluna já apareceu antes
        if col in colunas_renomeadas:
            # Incrementa o contador de ocorrências para essa coluna
            colunas_renomeadas[col] += 1
            # Cria um novo nome para a coluna com o sufixo
            novo_nome = f"{col}_{colunas_renomeadas[col] + 1}"
            df.columns.values[i] = novo_nome  # Atualiza o nome da coluna no DataFrame
        else:
            colunas_renomeadas[col] = 0  # Inicializa o contador para o nome da coluna

    return df

def excluir_coluns_splice(df, tipo=None):
    if tipo == "UCSAR45":
        colunas_uscar_45 = [
            "Nome do arquivo",
            "Fase",
            "UCS",
            "Splice Nb",
            "Int.PN",
            "Extra Component PN",
            "Standard",
            "CSA Left",
            "CSA Right",
            "CSA Total",
            "Node",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L7",
            "L8",
            "L9",
            "L10",
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7",
            "R8",
            "R9",
            "R10",
            "L1_CSA",
            "L2_CSA",
            "L3_CSA",
            "L4_CSA",
            "L5_CSA",
            "L6_CSA",
            "L7_CSA",
            "L8_CSA",
            "L9_CSA",
            "L10_CSA",
            "R1_CSA",
            "R2_CSA",
            "R3_CSA",
            "R4_CSA",
            "R5_CSA",
            "R6_CSA",
            "R7_CSA",
            "R8_CSA",
            "R9_CSA",
            "R10_CSA",
            "USCAR_45",
        ]
        df = df[colunas_uscar_45].dropna(how="all", axis=0)
        return df
    elif tipo == "GMW":
        colunas_GMW = [
            "Nome do arquivo",
            "Fase",
            "UCS",
            "Splice Nb",
            "Int.PN",
            "Extra Component PN",
            "Standard",
            "CSA Left",
            "CSA Right",
            "CSA Total",
            "Node",
            "L1",
            "L2",
            "L3",
            "L4",
            "L5",
            "L6",
            "L7",
            "L8",
            "L9",
            "L10",
            "R1",
            "R2",
            "R3",
            "R4",
            "R5",
            "R6",
            "R7",
            "R8",
            "R9",
            "R10",
            "L1_CSA",
            "L2_CSA",
            "L3_CSA",
            "L4_CSA",
            "L5_CSA",
            "L6_CSA",
            "L7_CSA",
            "L8_CSA",
            "L9_CSA",
            "L10_CSA",
            "R1_CSA",
            "R2_CSA",
            "R3_CSA",
            "R4_CSA",
            "R5_CSA",
            "R6_CSA",
            "R7_CSA",
            "R8_CSA",
            "R9_CSA",
            "R10_CSA",
            "GMW17136",
        ]
        df = df[colunas_GMW].dropna(how="all", axis=0)
        return df
    else:
        return df.dropna(how="all", axis=0)

def extrair_uscar_38(df_mult):

    if len(df_mult) == 0 or df_mult.empty: 
        return pd.DataFrame()

    if "Note 1" not in df_mult.columns:
        df_mult["Note 1"] = None

    if 'Term. 2' not in df_mult.columns:
        df_mult['Term. 2'] = None


    if "Note 2" in df_mult.columns and df_mult["Note 2"].str.contains("MULTI|X", na=False).any():
        # df_path = consultar_arquivos_base(id_name='Uscar_38_45_GMW')

        # with open(df_path, 'rb') as f:
        #     df_uscar_45 = pd.read_excel(f,sheet_name='Solda e MC GMI')

        # df_uscar_45.columns = df_uscar_45.columns.astype(str)

        # df_uscar_45 = renomear_colunas(df_uscar_45)

        # colunas_L = ['0.35','0.5','0.75', '1','1.5', '2','2.5','3', '4', '5', '6', '8','10','16','25','30','35']
        # colunas_R = ['0.35.1','0.5.1', '0.75.1','1.1','1.5.1','2.1','2.5.1','3.1','4.1','5.1','6.1','8.1', '10.1', '16.1', '25.1', '30.1', '35.1']

        # colunas_completares = ['Número','Termo','Terminal']

        # colunas_consolidadas = colunas_completares+colunas_L+colunas_R

        # df_uscar_45 = df_uscar_45[colunas_consolidadas]

        df_path = consultar_arquivos_base(id_name="Uscar_38_45_GMW")

        with open(df_path, "rb") as f:
            df_temp = pd.read_excel(f, sheet_name="Controle", header=None)

        df_temp.columns = df_temp.iloc[1]
        df_uscar_45 = df_temp.drop([0, 1]).reset_index(drop=True)

        df_uscar_45.columns = df_uscar_45.columns.astype(str)

        df_uscar_45 = renomear_colunas(df_uscar_45)

        df_uscar_45.rename(
            columns={"CÓDIGO_2": "Número", "TERMO": "Termo", "TERMINAL": "Terminal"},
            inplace=True,
        )
        colunas_L = [
            "0.35",
            "0.5",
            "0.75",
            "1.0",
            "1.5",
            "2.0",
            "2.5",
            "3.0",
            "4.0",
            "5.0",
            "6.0",
            "8.0",
            "10.0",
            "16.0",
            "25.0",
            "30.0",
            "35.0",
        ]
        colunas_R = [
            "0.35_2",
            "0.5_2",
            "0.75_2",
            "1.0_2",
            "1.5_2",
            "2.0_2",
            "2.5_2",
            "3.0_2",
            "4.0_2",
            "5.0_2",
            "6.0_2",
            "8.0_2",
            "10.0_2",
            "16.0_2",
            "25.0_2",
            "30.0_2",
            "35.0_2",
        ]

        colunas_completares = ["Número", "Termo", "Terminal"]

        df_uscar_45["Número"].fillna("Sem numéro de relatório", inplace=True)

        colunas_consolidadas = colunas_completares + colunas_L + colunas_R

        df_uscar_45 = df_uscar_45[colunas_consolidadas]

        df_uscar_45[colunas_L + colunas_R] = (
            df_uscar_45[colunas_L + colunas_R].fillna(0).astype(int)
        )

        df_uscar_45 = df_uscar_45.drop_duplicates().reset_index(drop=True)

        number_coluna = df_mult.columns.get_loc("Note 2") + 1

        df_mult_new = pd.DataFrame()

        for c in df_mult.columns[number_coluna:]:
            df_prov = df_mult[
                (df_mult[c].notna()) & (df_mult["Note 2"].str.contains("MULTI|X"))
            ][
                [
                    "Nome do arquivo",
                    "Fase",
                    "Leadset",
                    "Wire Nb",
                    "CSA",
                    "Int.PN",
                    "Term. 1",
                    "Seal 1",
                    "Node 1",
                    "Joint 1",
                    "Note 1",
                    "Term. 2",
                    "Seal 2",
                    "Node 2",
                    "Joint 2",
                    "Note 2",
                ]
            ].reset_index(drop=True)

            mult = df_prov["Note 2"].unique().tolist()

            for m in mult:
                df_prov2 = df_prov[df_prov["Note 2"] == m].reset_index(drop=True)

                df_grouped = (
                    df_prov2.groupby(["Note 2"], dropna=False)
                    .agg(
                        {
                            "Nome do arquivo": lambda x: ", ".join(
                                sorted(set(map(str, x.dropna())))
                            ),
                            "Fase": lambda x: ", ".join(
                                sorted(set(map(str, x.dropna())))
                            ),
                            "Leadset": lambda x: ", ".join(
                                sorted(set(map(str, x.dropna())))
                            ),
                            "Wire Nb": lambda x: ", ".join(
                                sorted(set(map(str, x.dropna())))
                            ),
                            #"CSA": lambda x: "+".join(sorted(x.dropna())),
                            "CSA": lambda x: "+".join(sorted(x.dropna().astype(str))),
                            "Term. 2": lambda x: ", ".join(
                                sorted(set(map(str, x.dropna())))
                            ),
                        }
                    )
                    .reset_index()
                )
                df_mult_new = pd.concat([df_mult_new, df_grouped], ignore_index=False)


        # colunas_add = ["Term. 2", "CSA"]
        # for i in colunas_add:
        #     if i not in df_mult_new.columns:
        #         df_mult_new[i] = None


        df_grouped2 = (
            df_mult_new.groupby(["Term. 2", "CSA"], dropna=False)
            .agg(
                {
                    "Nome do arquivo": lambda x: ", ".join(
                        sorted(set(map(str, x.dropna())))
                    ),
                    "Fase": lambda x: ", ".join(sorted(set(map(str, x.dropna())))),
                    "Leadset": lambda x: ", ".join(sorted(set(map(str, x.dropna())))),
                    "Wire Nb": lambda x: ", ".join(sorted(set(map(str, x.dropna())))),
                    "Note 2": lambda x: ", ".join(sorted(x.dropna())),
                }
            )
            .reset_index()
        )

        df_grouped2 = df_grouped2[
            [
                "Nome do arquivo",
                "Fase",
                "Leadset",
                "Wire Nb",
                "Note 2",
                "Term. 2",
                "CSA",
            ]
        ].rename(columns={"Note 2": "Multicrimp", "Term. 2": "Terminal"})

        colunas_splice_L = [
            "count_left_0.35",
            "count_left_0.50",
            "count_left_0.75",
            "count_left_1.00",
            "count_left_1.50",
            "count_left_2.00",
            "count_left_2.50",
            "count_left_3.00",
            "count_left_4.00",
            "count_left_5.00",
            "count_left_6.00",
            "count_left_8.00",
            "count_left_10.00",
            "count_left_16.00",
            "count_left_25.00",
            "count_left_30.00",
            "count_left_35.00",
        ]
        colunas_splice_R = [
            "count_right_0.35",
            "count_right_0.50",
            "count_right_0.75",
            "count_right_1.00",
            "count_right_1.50",
            "count_right_2.00",
            "count_right_2.50",
            "count_right_3.00",
            "count_right_4.00",
            "count_right_5.00",
            "count_right_6.00",
            "count_right_8.00",
            "count_right_10.00",
            "count_right_16.00",
            "count_right_25.00",
            "count_right_30.00",
            "count_right_35.00",
        ]

        for i in colunas_splice_L + colunas_splice_R:
            if i not in df_grouped2.columns:
                df_grouped2[i] = 0

        for i in df_grouped2.index:
            lista_csa = df_grouped2.loc[i, "CSA"].split("+")
            contagem = Counter(lista_csa)
            for item, count in contagem.items():
                df_grouped2.at[i, "count_left_" + str(item)] = count

        df_grouped2["USCAR_38"] = None

        for i in tqdm(df_grouped2.index, "[+] Adicionando USCAR 38...", colour="Blue"):
            valor = df_grouped2.at[i, "Terminal"]
            [v.strip() for v in str(valor).split(";")]
            string_L = ", ".join(
                map(
                    str,
                    df_grouped2.iloc[i : i + 1][colunas_splice_L].values[0].tolist(),
                )
            )
            string_R = ", ".join(
                map(
                    str,
                    df_grouped2.iloc[i : i + 1][colunas_splice_R].values[0].tolist(),
                )
            )

            for j in df_uscar_45.index:
                number = df_uscar_45.at[j, "Número"]
                valor_vd = df_uscar_45.at[j, "Terminal"]
                [v.strip() for v in str(valor_vd).split(",")]
                string_L_vd = ", ".join(
                    map(str, df_uscar_45.iloc[j : j + 1][colunas_L].values[0].tolist())
                )
                string_R_vd = ", ".join(
                    map(str, df_uscar_45.iloc[j : j + 1][colunas_R].values[0].tolist())
                )

                if (string_L == string_L_vd and string_R == string_R_vd) or (
                    string_L == string_R_vd and string_R == string_L_vd
                ):
                    # pega o valor atual da célula
                    valor_atual = df_grouped2.at[i, "USCAR_38"]

                    # se já existe algo, concatena com vírgula
                    if pd.notna(valor_atual) and valor_atual != "":
                        df_grouped2.at[i, "USCAR_38"] = f"{valor_atual}, {number}"
                    else:
                        df_grouped2.at[i, "USCAR_38"] = str(number)

        dict_mult = {row["Terminal"]: "Multicrimp" for i, row in df_grouped2.iterrows()}

    else:
        df_grouped2 = pd.DataFrame()
        dict_mult = {}
    return df_grouped2, dict_mult

def resumo_uscar38(df):
    df_group = (
        df.groupby(["Terminal", "CSA"], dropna=False)
        .agg(
            {
                "Nome do arquivo": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Fase": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Leadset": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Wire Nb": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Multicrimp": lambda x: ", ".join(sorted(x.dropna())),
                "USCAR_38": lambda x: ", ".join(sorted(x.dropna())),
            }
        )
        .reset_index()
    )

    df_group = df_group[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Wire Nb",
            "Multicrimp",
            "Terminal",
            "CSA",
            "USCAR_38",
        ]
    ]

    return df_group

def resumir_uscar_21(df):
    df_group = (
        df.groupby(["Term", "CSA", "Seal", "Legacy 1", "Legacy 2"], dropna=False)
        .agg(
            {
                "Nome do arquivo": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Fase": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Leadset": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Circuito": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Comentários": lambda x: ", ".join(sorted(set(x.dropna()))),
                "Tipo de validação": lambda x: ", ".join(sorted(x.dropna())),
                "Relatório - Interno": lambda x: ", ".join(sorted(x.dropna())),
                "Relatório - Externo": lambda x: ", ".join(sorted(x.dropna())),
            }
        )
        .reset_index()
    )

    df_group = df_group[
        [
            "Nome do arquivo",
            "Fase",
            "Leadset",
            "Circuito",
            "Term",
            "CSA",
            "Seal",
            "Legacy 1",
            "Legacy 2",
            "Comentários",
            "Tipo de validação",
            "Relatório - Interno",
            "Relatório - Externo",
        ]
    ]

    return df_group

def gerar_grupos_splices(df):
    lista_strings = []
    colunas_left = [
        "L1_CSA",
        "L2_CSA",
        "L3_CSA",
        "L4_CSA",
        "L5_CSA",
        "L6_CSA",
        "L7_CSA",
        "L8_CSA",
        "L9_CSA",
        "L10_CSA",
    ]
    colunas_rigth = [
        "R1_CSA",
        "R2_CSA",
        "R3_CSA",
        "R4_CSA",
        "R5_CSA",
        "R6_CSA",
        "R7_CSA",
        "R8_CSA",
        "R9_CSA",
        "R10_CSA",
    ]

    for i in df.index:
        stringL = ", ".join(sorted(df.loc[i, colunas_left].dropna().astype(str)))
        lista_strings.append(stringL)
        stringR = ", ".join(sorted(df.loc[i, colunas_rigth].dropna().astype(str)))
        lista_strings.append(stringR)

    lista_strings = list(set(lista_strings))
    lista_strings = [v.strip() for v in lista_strings if v.strip() != ""]
    lista_strings = (
        pd.DataFrame(lista_strings, columns=["Standard"])
        .dropna()
        .reset_index(drop=True)
    )
    lista_strings["ID"] = range(len(lista_strings))
    dict_normal = {row["Standard"]: row["ID"] for i, row in lista_strings.iterrows()}
    dict_Inv = {row["ID"]: row["Standard"] for i, row in lista_strings.iterrows()}

    df["Coluna_L"] = None
    df["Coluna_R"] = None
    df["Coluna_inv_L"] = None
    df["Coluna_inv_R"] = None
    df["Standard"] = None
    for i in df.index:
        stringL = ", ".join(sorted(df.loc[i, colunas_left].dropna().astype(str)))
        stringR = ", ".join(sorted(df.loc[i, colunas_rigth].dropna().astype(str)))
        df.at[i, "Coluna_L"] = dict_normal.get(stringL, 1000)
        df.at[i, "Coluna_R"] = dict_normal.get(stringR, 1000)
        vlr1 = df.at[i, "Coluna_L"]
        vlr2 = df.at[i, "Coluna_R"]
        if vlr1 > vlr2:
            df.at[i, "Coluna_L"] = vlr2
            df.at[i, "Coluna_R"] = vlr1

        df.at[i, "Coluna_inv_L"] = dict_Inv.get(df.at[i, "Coluna_L"], "-")
        df.at[i, "Coluna_inv_R"] = dict_Inv.get(df.at[i, "Coluna_R"], "-")

    df["Standard"] = (
        df["Coluna_inv_L"].astype(str) + " | " + df["Coluna_inv_R"].astype(str)
    )

    df = df.drop(columns=["Coluna_L", "Coluna_R", "Coluna_inv_L", "Coluna_inv_R"])

    return df

def agrupar_splices(df):
    df["Status"] = df.duplicated(
        subset=["Standard", "Extra Component PN"], keep="first"
    ).map({False: "Exclusivo", True: "Duplicado"})
    return df

def excluir_duplicados(dados):
    colunas = [
        "Multicrimp",
        "Leadset",
        "Wire Nb",
        "Nome do arquivo",
        "Tipo de validação",
        "Relatório - Interno",
        "Relatório - Externo",
    ]

    for coluna in colunas:
        if coluna in dados.columns:
            dados[coluna] = dados[coluna].apply(
                lambda x: ", ".join(
                    sorted(
                        set(item.strip() for item in str(x).split(",")), reverse=True
                    )
                )
            )
    return dados

def arrumar_wire_charted_cutsheet(df_wire:pd.DataFrame=None):

    # Substituir valores vazios (None, '', ' ', np.nan) por NaN
    df_wire.replace([None, ' ', '', np.nan], np.nan, inplace=True)

    # Remover as colunas que são completamente NaN
    df_wire.dropna(how='all', axis=1, inplace=True)

    df_wire = df_wire.reset_index(drop=True)
    df_wire.rename(columns={'Unm. Length':'Length','Wire Type':'T'},inplace=True)

    colunas_add = ['Note 1','Note 2','Fase']

    for i in colunas_add:
        if i not in df_wire.columns:
            df_wire[i] = None

    try:df_wire[['T_1', 'T_2']] = df_wire['Joint Type'].str.split('/', n=1, expand=True)
    except:pass
    
    try:df_wire[['C1', 'C2']] = df_wire['Color'].str.split('/', n=1, expand=True)
    except: pass

    colunas_ord = ['Nome do arquivo','Fase', 'ProcessoA', 'ProcessoB', 'UCS', 'Leadset', 'Wire Nb', 'Multicore', 'Sub-Assembly', 'Wire Type', 'Length', 'C1','C2', 
                   'Int.PN', 'T', 'CSA', 'Strip 1', 'Term. 1', 'Seal 1', 'Node 1', 'Joint 1','T_1', 'Note 1', 'Strip 2', 'Term. 2', 'Seal 2', 'Node 2',
                    'Joint 2','T_2','Note 2']
    
    df_wire = df_wire.drop(columns=['Color','Joint Type','Wire Spec'], errors='ignore')

    df_wire = reordenar_colunas(df_wire, colunas_prioritarias=colunas_ord)

    return df_wire

def Check_splices_cutsheet(df_splice: pd.DataFrame=None, df_wire: pd.DataFrame=None):
    # Substituir valores vazios (None, '', ' ', np.nan) por NaN
    df_splice.replace([None, ' ', '', np.nan], np.nan, inplace=True)

    # Remover as colunas que são completamente NaN
    df_splice.dropna(how='all', axis=1, inplace=True)


    dict_wire = {str(row["Wire Nb"]): row["CSA"] for i, row in df_wire.iterrows()}

    colunas_add = ['X1', 'X2', 'X3', 'X4', 'X5','X6','X7','X8','X9','X10']

    for i in df_splice.columns:
        if i in colunas_add:
            new_columns = i.replace('X','L')
            df_splice.rename(columns = {i:new_columns},inplace=True)

    colunas_add = ["L1","L2","L3","L4","L5","L6","L7","L8","L9","L10",'Fase',"Pack"]

    for c in colunas_add:
        if c not in df_splice.columns:
            df_splice[c] = None

    colunas = ["Nome do arquivo","Fase","UCS","Splice Nb","Int.PN",
               "Extra Component PN","Pack","CSA Left","CSA Right","CSA Total","Node",
               "L1","L2","L3","L4","L5","L6","L7","L8","L9","L10"]

    df_splice = reordenar_colunas(df_splice, colunas_prioritarias=colunas)

    def map_wire(x):
        # Se for None ou NaN
        if x is None or pd.isna(x):
            return None

        # Normaliza para string
        x_str = str(x).strip()

        # Se depois de strip ficou vazio, trata como None
        if x_str == "":
            return None

        # Verifica se está no dicionário
        if x_str in dict_wire:
            return dict_wire[x_str]

        return "Valor não mapeado"

    for c in colunas_add:
        df_splice[str(c) + "_CSA"] = df_splice[c].apply(map_wire)


    df_splice.rename(columns={'Splice Name':"Splice Nb"},inplace=True)


    colunas = ["Nome do arquivo","Fase","UCS","Splice Nb","Int.PN","Extra Component PN","Pack","CSA Left","CSA Right","CSA Total","Node",
               "L1","L2","L3","L4","L5","L6","L7","L8","L9","L10",
               "L1_CSA","L2_CSA","L3_CSA","L4_CSA","L5_CSA","L6_CSA","L7_CSA","L8_CSA","L9_CSA","L10_CSA"]

    df_splice = reordenar_colunas(df_splice, colunas)
    
    return df_splice

def Check_multicrimp_cutsheet(df_mult: pd.DataFrame=None, df_wire: pd.DataFrame=None):

    # Substituir valores vazios (None, '', ' ', np.nan) por NaN
    df_mult.replace([None, ' ', '', np.nan], np.nan, inplace=True)

    # Remover as colunas que são completamente NaN
    df_mult.dropna(how='all', axis=1, inplace=True)


    dict_wire = {str(row["Wire Nb"]): row["CSA"] for i, row in df_wire.iterrows()}

    colunas_add = ['W1', 'W2', 'W3', 'W4', 'W5','W6','W7','W8','W9','W10']

    for i in df_mult.columns:
        if i in colunas_add:
            new_columns = i.replace('W','MC.W')
            df_mult.rename(columns = {i:new_columns},inplace=True)

    colunas_add = ['MC.W1', 'MC.W2', 'MC.W3', 'MC.W4','MC.W5', 'MC.W6','MC.W7','MC.W8','MC.W9','MC.W10']

    for c in colunas_add:
        if c not in df_mult.columns:
            df_mult[c] = None

    colunas = ["Nome do arquivo","Fase","UCS","Splice Nb","Int.PN",
               "Extra Component PN","Pack","CSA Left","CSA Right","CSA Total","Node",
               'MC.W1', 'MC.W2', 'MC.W3', 'MC.W4','MC.W5', 'MC.W6','MC.W7','MC.W8','MC.W9','MC.W10']

    df_mult = reordenar_colunas(df_mult, colunas_prioritarias=colunas)

    def map_wire(x):
        # Se for None ou NaN
        if x is None or pd.isna(x):
            return None

        # Normaliza para string
        x_str = str(x).strip()

        # Se depois de strip ficou vazio, trata como None
        if x_str == "":
            return None

        # Verifica se está no dicionário
        if x_str in dict_wire:
            return dict_wire[x_str]

        return "Valor não mapeado"

    for c in colunas_add:
        df_mult[str(c) + "_CSA"] = df_mult[c].apply(map_wire)


    df_mult.rename(columns={'Splice Name':"Splice Nb"},inplace=True)


    df_mult.rename(columns={'Terminal':'MC.Terminal',},inplace=True)


    colunas_add = ['Fase','M. Crimp Name','MC.Splice1','MC.Splice2','MC.Splice3']

    for c in colunas_add:
        if c not in df_mult.columns:
            df_mult[c] = None

    colunas = ["Nome do arquivo","Fase","UCS",'M. Crimp Name','MC.Terminal',"Extra Component PN",'Note 2','Node', 'MC.Splice1','MC.Splice2','MC.Splice3',"CSA Total",
               'MC.W1', 'MC.W2', 'MC.W3', 'MC.W4','MC.W5', 'MC.W6','MC.W7','MC.W8','MC.W9','MC.W10',
               "MC.W1_CSA","MC.W2_CSA","MC.W3_CSA","MC.W4_CSA","MC.W5_CSA","MC.W6_CSA","MC.W7_CSA","MC.W8_CSA","MC.W9_CSA","MC.W10_CSA"]

    df_mult = reordenar_colunas(df_mult, colunas)

    return df_mult

def consolidar_cuts():
    os.system("cls")

    logo("Extrair e Consolidar Cut's")

    logger.info("Entre com o caminho do diretório, onde estão os arquivos")
    caminho_base = input("[>] ")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    logger.info("""
                Escolha o tipo de formato de arquivo:
                1. CUT
                2. CHARTED-CUT
                """)

    tipo_CUT = False
    tipo_CHARTED = False

    while True:
        try:
            tipo = int(input("[>] "))
            if tipo == 1:
                tipo_CUT = True
                break
            elif tipo == 2:
                tipo_CHARTED = True
                break
            else:
                logger.atencao("Entre com os valores [1 ou 2]")
        except Exception as e:
            logger.error(f"O valor digitado {e} esta incorreto")

    lista_arquivos = encontrar_arquivos_excel(caminho_base)

    logger.info(f"Total de arquivos encontrados: {len(lista_arquivos)}")

    # Inicializa dicionários
    dict_dataframe_cut = {
        "Wire_Nb": pd.DataFrame(),
        "MultWire_Nb": pd.DataFrame(),
        "Sleeve_Nb": pd.DataFrame(),
        "Splice_Nb": pd.DataFrame(),
        "Multcrimp_Nb - Estudo": pd.DataFrame(),
        "Multcrimp_Nb": pd.DataFrame(),
        "Análise Uscar21": pd.DataFrame(),
        "Resumo Uscar21": pd.DataFrame(),
        "Resumo Uscar45 - Splice": pd.DataFrame(),
        "Resumo GMW - Splice": pd.DataFrame(),
        "Análise Uscar38": pd.DataFrame(),
        "Resumo Uscar38": pd.DataFrame(),
    }

    dict_dataframe_cutsheet = {
        "Wire_Nb": pd.DataFrame(),
        "MultWire_Nb": pd.DataFrame(),
        "Sleeve_Nb": pd.DataFrame(),
        "Splice_Nb": pd.DataFrame(),
        "Multicrimp_Nb": pd.DataFrame()
    }

    for caminho in tqdm(lista_arquivos, desc="[+] Processando Arquivos", colour="blue"):
        abas = listar_abas_excel(caminho)
        if "CUT" in str(os.path.basename(caminho).replace(".xlsx", "")).upper():
            logger.info(
                f"\n\n[>] Em análise: {os.path.basename(caminho).replace('.xlsx', '')}"
            )
        # Se tiver aba "Sheet1", processa
        if any("Sheet1" in item for item in abas) and tipo_CUT:
            # print(f'Arquivo: {caminho}')
            df_dict = format_cut(caminho)

            # Concatena os DataFrames nas respectivas chaves
            for d in df_dict.keys():
                if d in dict_dataframe_cut:
                    if d == "Wire_Nb":
                        if "Int.PN" not in df_dict[d].columns:
                            df_dict[d]["Int.PN"] = None

                        if not df_dict[d]["Int.PN"].isnull().all():
                            df_uscar21 = check_usar_21(df_dict[d])
                            try:
                                df_uscar_38, dict_mult = extrair_uscar_38(
                                    df_dict[d].reset_index(drop=True)
                                )
                            except Exception as e:
                                df_uscar_38 = pd.DataFrame()
                                dict_mult = {}
                                logger.error(f"Error Extrair Uscar 38: {e}")
                                traceback.print_exc()

                            if len(df_uscar_38) > 0:
                                dict_dataframe_cut["Análise Uscar38"] = pd.concat(
                                    [
                                        dict_dataframe_cut["Análise Uscar38"],
                                        df_uscar_38,
                                    ],
                                    ignore_index=True,
                                )

                            if not any(not value for value in dict_mult.values()):
                                df_uscar21["Comentários"] = df_uscar21.apply(
                                    lambda row: dict_mult.get(
                                        row["Term"], row["Comentários"]
                                    ),
                                    axis=1,
                                )

                            dict_dataframe_cut["Análise Uscar21"] = pd.concat(
                                [dict_dataframe_cut["Análise Uscar21"], df_uscar21],
                                ignore_index=True,
                            )
                            df_prov, vm, vs, vu = resumo_uscar21(
                                dict_dataframe_cut["Análise Uscar21"]
                            )
                            report = []
                            report.append([d, "Validação Mecânica Selo: ", vs])
                            report.append([d, "Validação Uscar 21: ", vu])
                            report.append(
                                [d, "Validação Mecânica Terminal e selo: ", vm]
                            )
                            df_prov = pd.DataFrame(
                                report, columns=["Origem", "Tipo", "Quantidade"]
                            )
                            df_prov = df_prov[df_prov["Quantidade"] > 0].reset_index(
                                drop=True
                            )
                            dict_dataframe_cut["Resumo Uscar21"] = pd.concat(
                                [dict_dataframe_cut["Resumo Uscar21"], df_prov],
                                ignore_index=True,
                            )
                        dict_dataframe_cut[d] = pd.concat(
                            [dict_dataframe_cut[d], df_dict[d]], ignore_index=True
                        )

                        df_mult_consolidado = criar_multicrimp(
                            df_dict[d].reset_index(drop=True)
                        )
                        df_mult_consolidado_estudo = adicionar_mult_estudo(
                            df_dict[d].reset_index(drop=True)
                        )
                        if len(df_mult_consolidado) > 0:
                            dict_dataframe_cut["Multcrimp_Nb"] = pd.concat(
                                [
                                    dict_dataframe_cut["Multcrimp_Nb"],
                                    df_mult_consolidado,
                                ],
                                ignore_index=True,
                            )

                        if len(df_mult_consolidado_estudo) > 0:
                            dict_dataframe_cut["Multcrimp_Nb - Estudo"] = pd.concat(
                                [
                                    dict_dataframe_cut["Multcrimp_Nb - Estudo"],
                                    df_mult_consolidado_estudo,
                                ],
                                ignore_index=True,
                            )

                    elif d == "MultWire_Nb":
                        dict_dataframe_cut[d] = pd.concat(
                            [dict_dataframe_cut[d], df_dict[d]], ignore_index=True
                        )

                    elif d == "Sleeve_Nb":
                        dict_dataframe_cut[d] = pd.concat(
                            [dict_dataframe_cut[d], df_dict[d]], ignore_index=True
                        )

                    elif d == "Splice_Nb":
                        df_splice, df_45, df_gmw = Check_splices(
                            df_dict[d].reset_index(drop=True),
                            df_dict["Wire_Nb"].reset_index(drop=True),
                        )
                        dict_dataframe_cut[d] = pd.concat(
                            [dict_dataframe_cut[d], df_splice], ignore_index=True
                        )
                        dict_dataframe_cut["Resumo Uscar45 - Splice"] = pd.concat(
                            [dict_dataframe_cut["Resumo Uscar45 - Splice"], df_45],
                            ignore_index=True,
                        )
                        dict_dataframe_cut["Resumo GMW - Splice"] = pd.concat(
                            [dict_dataframe_cut["Resumo GMW - Splice"], df_gmw],
                            ignore_index=True,
                        )

                    else:
                        dict_dataframe_cut[d] = pd.concat(
                            [dict_dataframe_cut[d], df_dict[d]], ignore_index=True
                        )
                else:
                    pass

        # Se não tiver "Sheet1", mas tiver "Summary", ignora (log opcional)
        if any("Summary" in item for item in abas) and tipo_CHARTED:
            df_dict_cutsheet = format_Charted_cutsheet(caminho)

            for d in df_dict_cutsheet.keys():
                if d in dict_dataframe_cutsheet.keys():
                    if d == "Sleeve_Nb":
                        df_dict_cutsheet[d].replace([None, ' ', '', np.nan], np.nan, inplace=True)
                        df_dict_cutsheet[d].dropna(how='all', axis=1, inplace=True)
                        df_dict_cutsheet[d] = renomear_colunas_duplicadas(df_dict_cutsheet[d])
                    if d == "Wire_Nb":
                        df_dict_cutsheet[d] = renomear_colunas_duplicadas(df_dict_cutsheet[d])
                        df_dict_cutsheet[d] = arrumar_wire_charted_cutsheet(df_dict_cutsheet[d])
                    if d == "Splice_Nb":
                        df_dict_cutsheet[d] = Check_splices_cutsheet(df_splice=df_dict_cutsheet[d],df_wire=df_dict_cutsheet["Wire_Nb"])
                    if d == "Multicrimp_Nb":
                        df_dict_cutsheet[d] = Check_multicrimp_cutsheet(df_mult=df_dict_cutsheet[d],df_wire=df_dict_cutsheet["Wire_Nb"])
                    if d == "MultWire_Nb":
                        df_dict_cutsheet[d].replace([None, ' ', '', np.nan], np.nan, inplace=True)
                        df_dict_cutsheet[d].dropna(how='all', axis=1, inplace=True)
                        df_dict_cutsheet[d] = renomear_colunas_duplicadas(df_dict_cutsheet[d])

                    dict_dataframe_cutsheet[d] = pd.concat([dict_dataframe_cutsheet[d], df_dict_cutsheet[d]],ignore_index=True)

    if len(dict_dataframe_cut["Multcrimp_Nb"]) > 0:
        dict_dataframe_cut["Multcrimp_Nb"] = (
            dict_dataframe_cut["Multcrimp_Nb"].drop_duplicates().reset_index(drop=True)
        )

    if len(dict_dataframe_cut["Análise Uscar21"]) > 0:
        dict_dataframe_cut["Resumo Uscar21"] = resumir_uscar_21(
            dict_dataframe_cut["Análise Uscar21"]
        )
        dict_dataframe_cut["Resumo Uscar21"] = excluir_duplicados(
            dict_dataframe_cut["Resumo Uscar21"]
        )

    if len(dict_dataframe_cut["Resumo Uscar45 - Splice"]) > 0:
        dict_dataframe_cut["Resumo Uscar45 - Splice"] = gerar_grupos_splices(
            dict_dataframe_cut["Resumo Uscar45 - Splice"]
        )
        dict_dataframe_cut["Resumo Uscar45 - Splice"] = excluir_coluns_splice(
            dict_dataframe_cut["Resumo Uscar45 - Splice"], tipo="UCSAR45"
        )
        dict_dataframe_cut["Resumo Uscar45 - Splice"] = agrupar_splices(
            dict_dataframe_cut["Resumo Uscar45 - Splice"]
        )
    if len(dict_dataframe_cut["Resumo GMW - Splice"]) > 0:
        dict_dataframe_cut["Resumo GMW - Splice"] = gerar_grupos_splices(
            dict_dataframe_cut["Resumo GMW - Splice"]
        )
        dict_dataframe_cut["Resumo GMW - Splice"] = excluir_coluns_splice(
            dict_dataframe_cut["Resumo GMW - Splice"], tipo="GMW"
        )
        dict_dataframe_cut["Resumo GMW - Splice"] = agrupar_splices(
            dict_dataframe_cut["Resumo GMW - Splice"]
        )

    if len(dict_dataframe_cut["Análise Uscar38"]) > 0:
        dict_dataframe_cut["Resumo Uscar38"] = resumo_uscar38(
            dict_dataframe_cut["Análise Uscar38"]
        )
        dict_dataframe_cut["Resumo Uscar38"] = excluir_duplicados(
            dict_dataframe_cut["Resumo Uscar38"]
        )
        dict_dataframe_cut["Análise Uscar38"] = excluir_duplicados(
            dict_dataframe_cut["Análise Uscar38"]
        )

    if len(dict_dataframe_cutsheet["Wire_Nb"])>0:
        colunas = ['Nome do arquivo','Fase', 'ProcessoA', 'ProcessoB', 'UCS', 'Leadset', 'Wire Nb', 'Multicore', 'Sub-Assembly', 'Wire Type', 'Length', 'C1','C2', 
                   'Int.PN', 'T', 'CSA', 'Strip 1', 'Term. 1', 'Seal 1', 'Node 1', 'Joint 1','T_1', 'Note 1', 'Strip 2', 'Term. 2', 'Seal 2', 'Node 2',
                    'Joint 2','T_2','Note 2']
        dict_dataframe_cutsheet["Wire_Nb"] = reordenar_colunas(dict_dataframe_cutsheet["Wire_Nb"], colunas)


    if len(dict_dataframe_cutsheet["Sleeve_Nb"])>0:
        colunas = ["Nome do arquivo", "UCS","Sleeve Nb","Int.PN","Length","Cut-back","Insulated Length","Type",
                   "Note","Description","Mater","Type","Int.Diameter","Group","Color","Slit","Conv","Wall Th.",
                   "Layer","Node 1","Node 2"]
        dict_dataframe_cutsheet["Sleeve_Nb"] = reordenar_colunas(dict_dataframe_cutsheet["Sleeve_Nb"], colunas)

    if len(dict_dataframe_cutsheet["MultWire_Nb"])>0:
        colunas = ["Nome do arquivo","UCS","Mult.Wire Nb","Wire Type","Length","Int.PN","Wire Spec","Inc.BOM",
                   "Inc.Chart","CutBack1","CutBack2","W1","W2","W3","W4"]
        dict_dataframe_cutsheet["MultWire_Nb"] = reordenar_colunas(dict_dataframe_cutsheet["MultWire_Nb"], colunas)

    if len(dict_dataframe_cutsheet['Splice_Nb'])>0:
        colunas = ["Nome do arquivo","Fase","UCS","Splice Nb","Int.PN","Extra Component PN","Pack","CSA Left","CSA Right","CSA Total","Node",
               "L1","L2","L3","L4","L5","L6","L7","L8","L9","L10",
               "L1_CSA","L2_CSA","L3_CSA","L4_CSA","L5_CSA","L6_CSA","L7_CSA","L8_CSA","L9_CSA","L10_CSA"]
        dict_dataframe_cutsheet['Splice_Nb'] = reordenar_colunas(dict_dataframe_cutsheet['Splice_Nb'], colunas)

    data_atual = datetime.now().strftime("%d-%m-%Y")
    if not all(df.empty for df in dict_dataframe_cut.values()):
        salvar_dict_df_em_excel(
            dict_dataframe_cut, f"{caminho_output}/Cuts_consolidadas_{data_atual}.xlsx"
        )
    if not all(df.empty for df in dict_dataframe_cutsheet.values()):
        salvar_dict_df_em_excel(
            dict_dataframe_cutsheet,
            f"{caminho_output}/Charted_cutsheet_consolidadas_{data_atual}.xlsx",
        )

    logger.info("Arquivos salvos!")
