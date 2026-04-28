# # BIBLIOTECAS


import pandas as pd
import sys
import os
from tqdm import tqdm
from collections import Counter
import math
import zipfile
root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)
from src.function import *
from rapidfuzz import fuzz
import math
import warnings
warnings.simplefilter("ignore")

logger = LoggerTerminal(salvar_log=False, typing=True)

# # FUNCTION


def extrair_wire_charted_cut(path):
    with open(path[0], "rb") as f:
        df = pd.read_excel(f, sheet_name="Wire Sheet")

    lista = ["Wire Nb"]

    indices = encontrar_indices_palavras(df, lista)

    df_wire = df.loc[indices[0] : indices[1]].dropna(how="all").reset_index(drop=True)
    df_wire.columns = df_wire.iloc[
        0
    ]  # Define a primeira linha como os nomes das colunas
    df_wire = df_wire.drop(0).reset_index(
        drop=True
    )  # Remove a linha 0 e redefine o índice

    dict_csa = {row["Wire Nb"]: row["CSA"] for i, row in df_wire.iterrows()}

    return dict_csa


def check_arquivo_charted(caminho_arquivo):
    try:
        with open(caminho_arquivo, "rb") as f:
            xls = pd.ExcelFile(f)
            return "Wire Sheet" in xls.sheet_names
    except Exception as e:
        logger.error(f"Erro ao abrir o arquivo: {e}")
        return False


def encontrar_arquivos_excel_charted(diretorio):
    arquivos_excel = []

    # Percorrer todas as pastas e subpastas
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            # Verificar se a extensão é .xls ou .xlsx
            if arquivo.endswith((".xls", ".xlsx")):
                if check_arquivo_charted(os.path.join(raiz, arquivo)):
                    arquivos_excel.append(os.path.join(raiz, arquivo))

    return arquivos_excel


def check_arquivo_delta(caminho_arquivo):
    try:
        with open(caminho_arquivo, "rb") as f:
            xls = pd.ExcelFile(f)
            return "Composite" in xls.sheet_names
    except Exception as e:
        logger.error(f"Erro ao abrir o arquivo: {e}")
        return False


def encontrar_arquivos_excel(diretorio):
    arquivos_excel = []

    # Percorrer todas as pastas e subpastas
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            # Verificar se a extensão é .xls ou .xlsx
            if arquivo.endswith((".xls", ".xlsx")):
                if check_arquivo_delta(os.path.join(raiz, arquivo)):
                    arquivos_excel.append(os.path.join(raiz, arquivo))

    return arquivos_excel


def encontrar_indices_palavras(df, lista_palavras):
    indices_palavras = []

    # Percorre cada palavra na lista
    for palavra in lista_palavras:
        # Verifica se a palavra está contida na primeira coluna
        indices_palavras += df[
            df.iloc[:, 0].str.contains(palavra, case=False, na=False)
        ].index.tolist()

    indices_palavras.append(df.shape[0])
    return indices_palavras


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


def verificar_EVO(dados):
    circuitos = dados["Wire Nb"].unique()
    lista_de_circuitos = []
    for ckt in circuitos:
        df_prov = (
            dados[dados["Wire Nb"] == ckt]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )

        try:
            if df_prov["Unm.Length"].iloc[0] != df_prov["Unm.Length"].iloc[1]:
                if (
                    df_prov[df_prov["Tab"] == "To"]["Unm.Length"]
                    .astype(float)
                    .values[0]
                    <= 200
                ):
                    if "SP" in str(
                        df_prov[df_prov["Tab"] == "To"]["Node 1"]
                    ) or "SP" in str(df_prov[df_prov["Tab"] == "To"]["Node 2"]):
                        lista_de_circuitos.append(ckt)
        except:
            pass

    df_problemas = dados[dados["Wire Nb"].isin(lista_de_circuitos)].reset_index(
        drop=True
    )

    return df_problemas


def verificar_twister_bitola(dados):
    circuitos_tw = dados[
        (dados["Multicore"].notna()) & (dados["Multicore"].str.contains("TW", na=False))
    ]
    lista_de_circuitos = circuitos_tw["Wire Nb"].unique().tolist()

    lista_ckt_com_problemas = []

    for ckt in lista_de_circuitos:
        df_prov = (
            dados[dados["Wire Nb"] == ckt]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )

        if float(df_prov[df_prov["Tab"] == "To"]["CSA"].values[0]) >= 1.5:
            lista_ckt_com_problemas.append(ckt)

    dados = (
        dados[dados["Wire Nb"].isin(lista_ckt_com_problemas)]
        .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
        .reset_index(drop=True)
    )

    return dados


def verificar_twister_comp(dados):
    circuitos_tw = dados[
        (dados["Multicore"].notna()) & (dados["Multicore"].str.contains("TW", na=False))
    ]
    lista_de_circuitos = circuitos_tw["Wire Nb"].unique().tolist()

    lista_ckt_com_problemas = []

    for ckt in lista_de_circuitos:
        df_prov = (
            dados[dados["Wire Nb"] == ckt]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )

        if float(df_prov[df_prov["Tab"] == "To"]["Unm.Length"].values[0]) <= 460:
            lista_ckt_com_problemas.append(ckt)

    dados = (
        dados[dados["Wire Nb"].isin(lista_ckt_com_problemas)]
        .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
        .reset_index(drop=True)
    )

    return dados


def verificar_lgk_cc(dados):

    colunas_add = ["Note 1", "Note 2"]

    for col in colunas_add:
        if col not in dados.columns:
            dados[col] = None


    circuitos_lgk_cc = dados[
        (dados["Note 1"].str.contains("LGK", na=False))
        | (dados["Note 2"].str.contains("LGK", na=False))
    ]

    lista_de_circuitos = circuitos_lgk_cc["Wire Nb"].unique().tolist()

    lista_ckt_com_problemas_add = []
    lista_ckt_com_problemas_remove = []

    for ckt in lista_de_circuitos:
        df_prov = (
            dados[dados["Wire Nb"] == ckt]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )
        try:
            if (
                pd.isna(df_prov[df_prov["Tab"] == "From"]["Note 1"].values)
                and pd.notna(df_prov[df_prov["Tab"] == "To"]["Note 1"].values)
            ) or (
                pd.isna(df_prov[df_prov["Tab"] == "From"]["Note 2"].values)
                and pd.notna(df_prov[df_prov["Tab"] == "To"]["Note 2"].values)
            ):
                lista_ckt_com_problemas_add.append(ckt)
        except:
            pass

        try:
            if (
                pd.notna(df_prov[df_prov["Tab"] == "From"]["Note 1"].values)
                and pd.isna(df_prov[df_prov["Tab"] == "To"]["Note 1"].values)
            ) or (
                pd.notna(df_prov[df_prov["Tab"] == "From"]["Note 2"].values)
                and pd.isna(df_prov[df_prov["Tab"] == "To"]["Note 2"].values)
            ):
                lista_ckt_com_problemas_remove.append(ckt)
        except:
            pass

    try:
        df_add = (
            dados[dados["Wire Nb"].isin(lista_ckt_com_problemas_add)]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )
    except:
        df_add = pd.DataFrame()

    try:
        df_remove = (
            dados[dados["Wire Nb"].isin(lista_ckt_com_problemas_remove)]
            .drop_duplicates(subset=["Tab", "Change", "Wire Nb"])
            .reset_index(drop=True)
        )
    except:
        df_remove = pd.DataFrame()

    return df_add, df_remove


def verificar_term_abastecimento(dados):
    df_path = consultar_arquivos_base(id_name="terminais_sem")
    with open(df_path, "rb") as f:
        df_term = pd.read_excel(f)

    dict_term = {
        row["Part Number"]: row["Feed Type/Delivery Form"]
        for i, row in df_term.iterrows()
    }

    dict_tipo = {
        row["Part Number"]: row["Connection Technology"]
        for i, row in df_term.iterrows()
    }

    lista_terminais_wire = []
    lista_terminais_mult = []
    lista_completa = pd.DataFrame()
    lista_completa_filtrada = pd.DataFrame()

    df_wire = dados["WIRE"]
    df_MULTICRIMP = dados["MULTICRIMP"]

    try:
        lista_terminais_mult = (
            df_MULTICRIMP[df_MULTICRIMP["Tab"] == "To"]["Terminal"]
            .dropna()
            .unique()
            .tolist()
        )
    except:
        pass

    try:
        lista_terminais_wire = (
            df_wire[df_wire["Tab"] == "To"]["Term.1"].dropna().unique().tolist()
            + df_wire[df_wire["Tab"] == "To"]["Term.2"].dropna().unique().tolist()
        )
    except:
        pass

    lista_terminais_mult = pd.DataFrame(lista_terminais_mult, columns=["Terminais"])
    lista_terminais_mult["Origem"] = "MULTICRIMP"

    lista_terminais_wire = pd.DataFrame(lista_terminais_wire, columns=["Terminais"])
    lista_terminais_wire["Origem"] = "WIRE"

    if len(lista_terminais_mult) > 0 and len(lista_terminais_wire):
        lista_completa = pd.concat(
            [lista_terminais_wire, lista_terminais_mult], ignore_index=False
        )

    elif len(lista_terminais_mult) > 0:
        lista_completa = lista_terminais_mult.copy()

    elif len(lista_terminais_wire):
        lista_completa = lista_terminais_wire.copy()

    if len(lista_completa) > 0:
        lista_completa = lista_completa.drop_duplicates().reset_index(drop=True)

        lista_de_retricoes = ["Right", "Verificar", "Information not available"]
        lista_completa["Feed Type/Delivery Form"] = (
            lista_completa["Terminais"].map(dict_term).fillna("Verificar")
        )
        lista_completa["Connection Technology"] = (
            lista_completa["Terminais"].map(dict_tipo).fillna("Verificar")
        )

        # Filtrando as linhas que contêm qualquer uma das palavras da lista_de_retricoes
        lista_completa_filtrada = lista_completa[
            lista_completa["Feed Type/Delivery Form"].str.contains(
                "|".join(lista_de_retricoes), case=False, na=False
            )
        ].reset_index(drop=True)

        lista_completa_filtrada = lista_completa_filtrada[
            ~(
                (lista_completa_filtrada["Origem"] == "WIRE")
                & (lista_completa_filtrada["Connection Technology"] == "Weld")
            )
        ].reset_index(drop=True)

    return lista_completa_filtrada


def verificar_path_arquivos(path_base, lista_de_path):
    arq_path = []
    nome_cut = os.path.basename(path_base).replace(".xlsx", "")
    for path2 in lista_de_path:
        nome_charted = os.path.basename(path2).replace(".xlsx", "")
        score = fuzz.ratio(nome_cut, nome_charted)
        if score > 80:
            arq_path.append(path2)
            nome_arquivo = os.path.basename(path2).replace(".xlsx", "")
            print('\n')
            logger.sucesso(f"Arquivo encontrado: {nome_arquivo}")
            return arq_path


def check_usar_21(df_wire):

    lista_de_cabos = consultar_arquivos_base(id_name="Lista_de_cabos_com_legacy")
    with open(lista_de_cabos, "rb") as f:
        df_legacy = pd.read_excel(f,sheet_name="rev.1")

    dict_legacy = {
        str(row["Part Number"]): str(row["Legacy"]) for i, row in df_legacy.iterrows()
    }

    df_path_cabos = consultar_arquivos_base(id_name="Lista_de_cabos")
    with open(df_path_cabos, "rb") as f:
        df_book = pd.read_excel(f)

    df_spec_cabos = convert_legacy(df_book)
    dict_tipos = {
        str(row["Part Number"]): str(row["Legacy"]) for i, row in df_spec_cabos.iterrows()
    }

    dict_tipos = {k: v for k, v in dict_tipos.items() if v is not None}


    for chave, valor in dict_legacy.items():
        chave_limpa = chave.strip()  # remove espaços

        # Se a chave não existe, adiciona
        if chave_limpa not in dict_tipos:
            dict_tipos[chave_limpa] = valor
        else:
            # Atualiza somente se o valor atual estiver "vazio"
            if dict_tipos[chave_limpa] is None or dict_tipos[chave_limpa] == 'None' or dict_tipos[chave_limpa] == '':
                dict_tipos[chave_limpa] = valor

    df_path = consultar_arquivos_base(id_name="lista_app")
    with open(df_path, "rb") as f:
        df_spec = pd.read_excel(f, sheet_name="Crimpagem Access")[
            ["CHP", "Relatório", "Terminal", "Bitola", "Isolação", "Selo"]
        ].astype(str)

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

    colunas_faul = ['Int.PN','CSA']
    for i in colunas_faul:
        if i not in df_wire.columns:
            df_wire[i] = None

    dict_wire = {row["Wire Nb"]: row["Int.PN"] for i, row in df_wire.iterrows()}
    dict_csa = {row["Wire Nb"]: row["CSA"] for i, row in df_wire.iterrows()}
    dict_term1 = {row["Wire Nb"]: row["Term.1"] for i, row in df_wire.iterrows()}
    dict_term2 = {row["Wire Nb"]: row["Term.2"] for i, row in df_wire.iterrows()}
    dict_selo1 = {row["Wire Nb"]: row["Seal 1"] for i, row in df_wire.iterrows()}
    dict_selo2 = {row["Wire Nb"]: row["Seal 2"] for i, row in df_wire.iterrows()}

    df_1 = df_wire[
        ["Tab", "Wire Nb", "CSA", "Joint 1", "Int.PN", "Term.1", "Seal 1"]
    ].rename(columns={"Joint 1": "Wire Nb_2", "Term.1": "Term", "Seal 1": "Seal"})
    df_2 = df_wire[
        ["Tab", "Wire Nb", "CSA", "Joint 2", "Int.PN", "Term.2", "Seal 2"]
    ].rename(columns={"Joint 2": "Wire Nb_2", "Term.2": "Term", "Seal 2": "Seal"})

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
            "Tab",
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
            "Tab",
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
    df_completo["Legacy 1"] = df_completo["Tipo Cabo 1"].astype(str).map(dict_tipos)
    df_completo["Legacy 2"] = df_completo["Tipo Cabo 2"].astype(str).map(dict_tipos)

    df_completo = df_completo[
        [
            "Tab",
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

    return df_completo


def Check_splices(df_splice, df_wire, lista_de_arquivos):
    # ----------------------------------------------------------------------------------------------------------------------------------------

    # df_path = consultar_arquivos_base(id_name='Uscar_38_45_GMW')

    # with open(df_path, 'rb') as f:
    #     df_uscar_45 = pd.read_excel(f,sheet_name='Solda e MC GMI')

    # df_uscar_45.columns = df_uscar_45.columns.astype(str)

    # df_uscar_45 = renomear_colunas(df_uscar_45)

    # colunas_L = ['0.35','0.5','0.75', '1','1.5', '2','2.5','3', '4', '5', '6', '8','10','16','25','30','35']
    # colunas_R = ['0.35.1','0.5.1', '0.75.1','1.1','1.5.1','2.1','2.5.1','3.1','4.1','5.1','6.1','8.1', '10.1', '16.1', '25.1', '30.1', '35.1']

    # colunas_completares = ['Número','Termo']

    # colunas_consolidadas = colunas_completares+colunas_L+colunas_R

    # df_uscar_45 = df_uscar_45[colunas_consolidadas]

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

    try:
        dict_wire_inteiro = extrair_wire_charted_cut(lista_de_arquivos)
    except:
        dict_wire_inteiro = {}

    if len(dict_wire_inteiro) == 0:
        print('\n')
        logger.error("Arquivo CHARTED CUT não foi encontrado. Verifique!")

    dict_wire = {str(row["Wire Nb"]): row["CSA"] for i, row in df_wire.iterrows()}

    dict_wire.update(dict_wire_inteiro)

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
        "Tab",
        "Change",
        "Splice Name",
        "Int.PN",
        "Extra Component PN",
        "CSA Left",
        "CSA Right",
        "CSA Total",
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
        "count_left_0.5",
        "count_left_0.75",
        "count_left_1.0",
        "count_left_1.5",
        "count_left_2.0",
        "count_left_2.5",
        "count_left_3.0",
        "count_left_4.0",
        "count_left_5.0",
        "count_left_6.0",
        "count_left_8.0",
        "count_left_10.0",
        "count_left_16.0",
        "count_left_25.0",
        "count_left_30.0",
        "count_left_35.0",
        "count_right_0.35",
        "count_right_0.5",
        "count_right_0.75",
        "count_right_1.0",
        "count_right_1.5",
        "count_right_2.0",
        "count_right_2.5",
        "count_right_3.0",
        "count_right_4.0",
        "count_right_5.0",
        "count_right_6.0",
        "count_right_8.0",
        "count_right_10.0",
        "count_right_16.0",
        "count_right_25.0",
        "count_right_30.0",
        "count_right_35.0",
    ]
    for col in colunas_check:
        df_splice[col] = 0

    colunas = [
        "Tab",
        "Change",
        "Splice Name",
        "Int.PN",
        "Extra Component PN",
        "CSA Left",
        "CSA Right",
        "CSA Total",
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

    for i in tqdm(df_splice.index, "[+] Processando...", colour="Blue"):
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

        # junta no df_splice (mesma linha)
        df_splice.loc[i, resultados_left.columns] = resultados_left.iloc[0]
        df_splice.loc[i, resultados_right.columns] = resultados_right.iloc[0]

    # USCAR 45 e GMW -------------------------------------------------------------------------------------------------------------
    colunas_splice_L = [
        "count_left_0.35",
        "count_left_0.5",
        "count_left_0.75",
        "count_left_1.0",
        "count_left_1.5",
        "count_left_2.0",
        "count_left_2.5",
        "count_left_3.0",
        "count_left_4.0",
        "count_left_5.0",
        "count_left_6.0",
        "count_left_8.0",
        "count_left_10.0",
        "count_left_16.0",
        "count_left_25.0",
        "count_left_30.0",
        "count_left_35.0",
    ]
    colunas_splice_R = [
        "count_right_0.35",
        "count_right_0.5",
        "count_right_0.75",
        "count_right_1.0",
        "count_right_1.5",
        "count_right_2.0",
        "count_right_2.5",
        "count_right_3.0",
        "count_right_4.0",
        "count_right_5.0",
        "count_right_6.0",
        "count_right_8.0",
        "count_right_10.0",
        "count_right_16.0",
        "count_right_25.0",
        "count_right_30.0",
        "count_right_35.0",
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

    df_45 = df_splice[
        (df_splice["USCAR_45"].isna()) & (df_splice["Tab"] == "To")
    ].reset_index(drop=True)
    df_gmw = df_splice[
        (df_splice["GMW17136"].isna()) & (df_splice["Tab"] == "To")
    ].reset_index(drop=True).drop(columns=['USCAR_45'])

    return df_splice, df_45, df_gmw


def check_multicrimp(df_mult, df_wire, lista_de_arquivos):
    # ----------------------------------------------------------------------------------------------------------------------------------------
    # df_path = consultar_arquivos_base(id_name='Uscar_38_45_GMW')

    # with open(df_path, 'rb') as f:
    #     df_uscar_38 = pd.read_excel(f,sheet_name='Solda e MC GMI')

    # df_uscar_38.columns = df_uscar_38.columns.astype(str)

    # df_uscar_38 = renomear_colunas(df_uscar_38)

    # colunas_L = ['0.35','0.5','0.75', '1','1.5', '2','2.5','3', '4', '5', '6', '8','10','16','25','30','35']
    # colunas_R = ['0.35.1','0.5.1', '0.75.1','1.1','1.5.1','2.1','2.5.1','3.1','4.1','5.1','6.1','8.1', '10.1', '16.1', '25.1', '30.1', '35.1']

    # colunas_completares = ['Número','Termo','Terminal']

    # colunas_consolidadas = colunas_completares+colunas_L+colunas_R

    # df_uscar_38 = df_uscar_38[colunas_consolidadas]

    # ----------------------------------------------------------------------------------------------------------------------------------------

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

    df_uscar_38 = df_uscar_45.drop_duplicates().reset_index(drop=True)

    # ----------------------------------------------------------------------------------------------------------------------------------------

    try:
        dict_wire_inteiro = extrair_wire_charted_cut(lista_de_arquivos)
    except:
        dict_wire_inteiro = {}

    if len(dict_wire_inteiro) == 0:
        print('\n')
        logger.error("Arquivo CHARTED CUT não foi encontrado. Verifique!")

    dict_wire = {str(row["Wire Nb"]): row["CSA"] for i, row in df_wire.iterrows()}

    dict_wire.update(dict_wire_inteiro)

    df_mult = df_mult.dropna(how="all", axis=1).reset_index(drop=True)
    df_mult = df_mult.dropna(how="all", axis=0).reset_index(drop=True)

    colunas_add = ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"]

    for c in colunas_add:
        if c not in df_mult.columns:
            df_mult[c] = None

    colunas = [
        "Tab",
        "Change",
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
    ]

    df_mult = reordenar_colunas(df_mult, colunas)

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

    colunas_w = [
        "W1_CSA",
        "W2_CSA",
        "W3_CSA",
        "W4_CSA",
        "W5_CSA",
        "W6_CSA",
        "W7_CSA",
        "W8_CSA",
        "W9_CSA",
        "W10_CSA",
    ]

    colunas_check_w = [
        "count_w_0.35",
        "count_w_0.5",
        "count_w_0.75",
        "count_w_1.0",
        "count_w_1.5",
        "count_w_2.0",
        "count_w_2.5",
        "count_w_3.0",
        "count_w_4.0",
        "count_w_5.0",
        "count_w_6.0",
        "count_w_8.0",
        "count_w_10.0",
        "count_w_16.0",
        "count_w_25.0",
        "count_w_30.0",
        "count_w_35.0",
    ]
    for col in colunas_check_w:
        df_mult[col] = 0

    for i in tqdm(df_mult.index, "[+] Processando...", colour="Blue"):
        # pega a linha e remove colunas vazias
        df_prov_w = df_mult.iloc[i : i + 1][colunas_w].dropna(how="all", axis=1)

        # conta ocorrências
        resultados_w = df_prov_w.apply(lambda row: row.value_counts(), axis=1)

        # renomeia colunas para indicar que são contagens
        resultados_w.columns = [f"count_w_{c}" for c in resultados_w.columns]

        # junta no df_mult (mesma linha)
        df_mult.loc[i, resultados_w.columns] = resultados_w.iloc[0]

    # USCAR 38 e GMW -------------------------------------------------------------------------------------------------------------
    colunas_mut_w = [
        "count_w_0.35",
        "count_w_0.5",
        "count_w_0.75",
        "count_w_1.0",
        "count_w_1.5",
        "count_w_2.0",
        "count_w_2.5",
        "count_w_3.0",
        "count_w_4.0",
        "count_w_5.0",
        "count_w_6.0",
        "count_w_8.0",
        "count_w_10.0",
        "count_w_16.0",
        "count_w_25.0",
        "count_w_30.0",
        "count_w_35.0",
    ]

    df_mult["USCAR_38"] = None
    df_mult["GMW17136"] = None

    coluna_dummy = ", ".join(
        map(str, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    )

    if (
        "Extra Component PN" not in df_mult.columns
        or "Extra Component" not in df_mult.columns
    ):
        df_mult["Extra Component PN"] = None
        colunas = [
            "Tab",
            "Change",
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
        ]

        df_mult = reordenar_colunas(df_mult, colunas)

    for i in tqdm(
        df_mult.index, "[+] Adicionando USCAR 38 e GMW17136...", colour="Blue"
    ):
        # try:
        #     valor = df_mult.at[i,'Extra Component PN']
        # except:
        #     valor = df_mult.at[i,'Extra Component']

        valor = df_mult.get("Extra Component PN", df_mult.get("Extra Component", None))
        if valor is not None:
            valor = valor.at[i]

        if ";" in str(valor):
            termo = [v.strip() for v in str(valor).split(";")]
        else:
            termo = [v.strip() for v in str(valor).split(",")]

        valor2 = df_mult.at[i, "Terminal"]
        if ";" in str(valor2):
            terminal = [v.strip() for v in str(valor2).split(";")]
        else:
            terminal = [v.strip() for v in str(valor2).split(",")]

        string_w = ", ".join(
            map(str, df_mult.iloc[i : i + 1][colunas_mut_w].values[0].tolist())
        )
        string_W_check = ", ".join(
            map(str, df_mult.iloc[i : i + 1][colunas_w].values[0].tolist())
        )

        for j in df_uscar_38.index:
            number = df_uscar_38.at[j, "Número"]
            valor_vd = df_uscar_38.at[j, "Termo"]
            if ";" in str(valor_vd):
                termo_vd = [v.strip() for v in str(valor_vd).split(";")]
            else:
                termo_vd = [v.strip() for v in str(valor_vd).split(",")]

            valor_vd_term = df_uscar_38.at[j, "Terminal"]
            if ";" in str(valor_vd_term):
                termo_vd_term = [v.strip() for v in str(valor_vd_term).split(";")]
            else:
                termo_vd_term = [v.strip() for v in str(valor_vd_term).split(",")]

            string_L_vd = ", ".join(
                map(str, df_uscar_38.iloc[j : j + 1][colunas_L].values[0].tolist())
            )
            string_R_vd = ", ".join(
                map(str, df_uscar_38.iloc[j : j + 1][colunas_R].values[0].tolist())
            )

            if "Valor não mapeado" not in string_W_check:
                if (string_w == string_L_vd and coluna_dummy == string_R_vd) or (
                    string_w == string_R_vd and coluna_dummy == string_L_vd
                ):
                    for t in terminal:
                        if t in termo_vd_term:
                            # pega o valor atual da célula
                            valor_atual = df_mult.at[i, "USCAR_38"]

                            # se já existe algo, concatena com vírgula
                            if pd.notna(valor_atual) and valor_atual != "":
                                df_mult.at[i, "USCAR_38"] = f"{valor_atual}, {number}"
                            else:
                                df_mult.at[i, "USCAR_38"] = str(number)

                    for t in termo:
                        if t in termo_vd:
                            valor_termo = df_mult.at[i, "GMW17136"]

                            if pd.notna(valor_termo) and valor_termo != "":
                                df_mult.at[i, "GMW17136"] = f"{valor_termo}, {number}"
                            else:
                                df_mult.at[i, "GMW17136"] = str(number)
                            break
    #df_us_38 = df_mult[(df_mult["USCAR_38"].isna()) & (df_mult["Tab"] == "To")].reset_index(drop=True)
    #df_gmw_38 = df_mult[(df_mult["GMW17136"].isna()) & (df_mult["Tab"] == "To")].reset_index(drop=True)
    df_us_38 = df_mult[(df_mult["Tab"] == "To")].reset_index(drop=True)
    df_gmw_38 = df_mult[(df_mult["Tab"] == "To")].reset_index(drop=True)

    return df_mult, df_us_38, df_gmw_38


def check_tubo(df_tubo):
    df_prov = df_tubo[df_tubo["Slit"] == "true"].reset_index(drop=True)

    return df_prov


def resumo_uscar21(df_wire):
    df_wire = df_wire[
        (df_wire["Tipo de validação"] != "Validação OK") & (df_wire["Tab"] == "To")
    ].reset_index(drop=True)

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


def report_resumo(df_dict):
    report = []

    for k in df_dict.keys():
        if "Análise WIRE Uscar21" == k:
            df_prov, vm, vs, vu = resumo_uscar21(df_dict[k])
            report.append([k, "Validação Mecânica Selo: ", vs])
            report.append([k, "Validação Uscar 21: ", vu])
            report.append([k, "Validação Mecânica Terminal e selo: ", vm])
        if "Problemas com bobina de term." == k:
            report.append([k, "Abastecimento de Terminais", df_dict[k].shape[0]])

        if "Problemas com EVO" == k:
            df_prov = df_dict[k][df_dict[k]["Tab"] == "To"].reset_index(drop=True)
            report.append(
                [k, "Circuitos de splices menores que 120mm", df_prov.shape[0]]
            )

        if "Análise TUBOS" == k:
            report.append([k, "Tubos Slit", df_dict[k].shape[0]])

        if "Análise MULT GMW" == k:
            report.append([k, "Validação GMW da Multicrimp", df_dict[k].shape[0]])

        if "Análise MULT Uscar 38" == k:
            report.append([k, "Validação Uscar 38 da Multicrimp", df_dict[k].shape[0]])

        if "Análise SPLICE GMW" == k:
            report.append([k, "Validação GMW da Splice", df_dict[k].shape[0]])

        if "Análise SPLICE Uscar 45" == k:
            report.append([k, "Validação Uscar 45 da Splice", df_dict[k].shape[0]])

        # ---
        if "Problemas com TW 1.5" == k:
            df_prov = df_dict[k][df_dict[k]["Tab"] == "To"].reset_index(drop=True)
            report.append([k, "Twister com bitolas acima de 1.5", df_prov.shape[0]])

        if "Problemas com TW Comp" == k:
            df_prov = df_dict[k][df_dict[k]["Tab"] == "To"].reset_index(drop=True)
            report.append(
                [k, "Twister com comprimento menor que 460mm", df_prov.shape[0]]
            )

        if "Problemas LGK-CC Adicionar" == k:
            df_prov = df_dict[k][df_dict[k]["Tab"] == "To"].reset_index(drop=True)
            report.append([k, "Circuitos LGK-CC incluídos", df_prov.shape[0]])

        if "Problemas LGK-CC Remover" == k:
            df_prov = df_dict[k][df_dict[k]["Tab"] == "To"].reset_index(drop=True)
            report.append([k, "Circuitos LGK-CC removidos", df_prov.shape[0]])

    df_dict = pd.DataFrame(report, columns=["Origem", "Tipo", "Quantidade"])

    df_dict = df_dict[df_dict["Quantidade"] > 0].reset_index(drop=True)

    return df_dict


def check_rack(df_wire, df_splice, df_mult):
    Circuit_Out_corte = 0
    Circuit_In_corte = 0

    Circuit_Out_sp = 0
    Circuit_In_sp = 0

    Circuit_Out_mult = 0
    Circuit_In_mult = 0

    total_corte = 0
    total_splice = 0
    total_mult = 0

    if len(df_wire) > 0:
        lista_ckt = df_wire["Wire Nb"].dropna().unique()
    if len(df_splice) > 0:
        lista_sp = df_splice["Splice Name"].dropna().unique()
    if len(df_mult) > 0:
        lista_mult = df_mult["M.Crimp Name"].dropna().unique()

    # CORTE
    if len(df_wire) > 0:
        for i in lista_ckt:
            df_prov = df_wire[df_wire["Wire Nb"] == i].reset_index(drop=True)

            # CORTE
            if len(df_prov) == 1 and "To" in df_prov["Tab"].loc[0]:
                Circuit_In_corte += 1
            if len(df_prov) == 1 and "From" in df_prov["Tab"].loc[0]:
                Circuit_Out_corte += 1

        total_corte = Circuit_In_corte - Circuit_Out_corte
        if total_corte > 0:
            total_corte = f"Necs: {round((Circuit_In_corte - Circuit_Out_corte) / 15, 2)} | {math.ceil((Circuit_In_corte - Circuit_Out_corte) / 15)} | 15 posições"

    # SPLICE
    if len(df_splice) > 0:
        for sp in lista_sp:
            df_prov_sp = df_splice[df_splice["Splice Name"] == sp].reset_index(
                drop=True
            )

            if len(df_prov_sp) == 1 and "To" in df_prov_sp["Tab"].loc[0]:
                linha = df_prov_sp.loc[
                    0,
                    [
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
                    ],
                ]
                Circuit_In_sp += int(
                    linha.replace("", pd.NA).replace(" ", pd.NA).notna().sum()
                )

            if len(df_prov_sp) == 1 and "From" in df_prov_sp["Tab"].loc[0]:
                linha = df_prov_sp.loc[
                    0,
                    [
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
                    ],
                ]
                Circuit_Out_sp += int(
                    linha.replace("", pd.NA).replace(" ", pd.NA).notna().sum()
                )

        total_splice = Circuit_In_sp - Circuit_Out_sp
        if total_splice > 0:
            total_splice = f"Necs: {round((Circuit_In_sp - Circuit_Out_sp) / 15, 2)} | {math.ceil((Circuit_In_sp - Circuit_Out_sp) / 15)} | 15 posições"

    # MULTICRIMP
    if len(df_mult) > 0:
        for m in lista_mult:
            df_prov_mult = df_mult[df_mult["M.Crimp Name"] == m].reset_index(drop=True)

            if len(df_prov_mult) == 1 and "To" in df_prov_mult["Tab"].loc[0]:
                linha = df_prov_mult.loc[
                    0, ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"]
                ]
                Circuit_In_mult += int(
                    linha.replace("", pd.NA).replace(" ", pd.NA).notna().sum()
                )

            if len(df_prov_mult) == 1 and "From" in df_prov_mult["Tab"].loc[0]:
                linha = df_prov_mult.loc[
                    0, ["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8", "W9", "W10"]
                ]
                Circuit_Out_mult += int(
                    linha.replace("", pd.NA).replace(" ", pd.NA).notna().sum()
                )

        total_mult = Circuit_In_mult - Circuit_Out_mult
        if total_mult > 0:
            total_mult = f"Necs: {round((Circuit_In_mult - Circuit_Out_mult) / 15, 2)} | {math.ceil((Circuit_In_mult - Circuit_Out_mult) / 15)} | 15 posições"

    if total_corte == 0 and total_splice == 0 and total_mult == 0:
        df_total = pd.DataFrame()
    else:
        df_total = pd.DataFrame(
            [[total_corte, total_splice, total_mult]],
            columns=[
                "Necessidade de Racks Corte",
                "Necessidade de Racks Splice",
                "Necessidade de Racks Mult",
            ],
        )

    if len(df_wire) > 0:
        df_total["Add Circuitos Wire"] = (
            f"{round(Circuit_In_corte - Circuit_Out_corte, 2)}"
        )
    if len(df_splice) > 0:
        df_total["Add Circuitos Splices"] = (
            f"{round(Circuit_In_sp - Circuit_Out_sp, 2)}"
        )
    if len(df_mult) > 0:
        df_total["Add Circuitos Multicrimp"] = (
            f"{round(Circuit_In_mult - Circuit_Out_mult, 2)}"
        )

    colunas_ord = [
        "Add Circuitos Wire",
        "Necessidade de Racks Corte",
        "Add Circuitos Splices",
        "Necessidade de Racks Splice",
        "Add Circuitos Multicrimp",
        "Necessidade de Racks Mult",
    ]

    df_total = reordenar_colunas(df_total, colunas_ord)

    return df_total


def Check_quantidade_app(df_wire):
    lista_ckt = df_wire["Wire Nb"].dropna().unique()

    list_term = []
    list_selo = []

    for ckt in lista_ckt:
        df_prov = df_wire[df_wire["Wire Nb"] == ckt].reset_index(drop=True)

        if len(df_prov) == 2:
            try:
                term1_from = str(df_prov[df_prov["Tab"] == "From"]["Term.1"].values[0]).strip()
            except:
                term1_from = 0
            try:
                term2_from = str(df_prov[df_prov["Tab"] == "From"]["Term.2"].values[0]).strip()
            except:
                term2_from = 0

            try:
                selo1_from = str(df_prov[df_prov["Tab"] == "From"]["Seal 1"].values[0]).strip()
            except:
                selo1_from  = 0
            try:
                selo2_from = str(df_prov[df_prov["Tab"] == "From"]["Seal 2"].values[0]).strip()
            except:
                selo2_from =  0
            try:
                term1_to = str(df_prov[df_prov["Tab"] == "To"]["Term.1"].values[0]).strip()
            except: 
                term1_to = 0
            try:
                term2_to = str(df_prov[df_prov["Tab"] == "To"]["Term.2"].values[0]).strip()
            except: 
                term2_to = 0
            try:
                selo1_to = str(df_prov[df_prov["Tab"] == "To"]["Seal 1"].values[0]).strip()
            except:
                selo1_to = 0
            try:   
                selo2_to = str(df_prov[df_prov["Tab"] == "To"]["Seal 2"].values[0]).strip()
            except:
                selo2_to = 0

            if (term1_from != term1_to and term2_from != term2_to) and (
                term1_from != term2_to and term2_from != term1_to
            ):
                if term1_from == term1_to and term2_from != term2_to:
                    if term1_to == term2_to:
                        list_term.append(["Aplicador", term1_to, 2])
                    else:
                        list_term.append(["Aplicador", term1_to, 1])
                elif term1_from != term1_to and term2_from == term2_to:
                    if term1_to == term2_to:
                        list_term.append(["Aplicador", term2_to, 2])
                    else:
                        list_term.append(["Aplicador", term2_to, 1])

                elif term1_from != term1_to and term2_from != term2_to:
                    if term1_to == term2_to:
                        list_term.append(["Aplicador", term1_to, 2])
                    else:
                        list_term.append(["Aplicador", term1_to, 1])
                        list_term.append(["Aplicador", term2_to, 1])

            if (selo1_from != selo1_to and selo2_from != selo2_to) and (
                selo1_from != selo2_to and selo2_from != selo1_to
            ):
                if selo1_from == selo1_to and selo2_from != selo2_to:
                    if selo1_to == selo2_to:
                        list_selo.append(["Calha de selo", selo1_to, 2])
                    else:
                        list_selo.append(["Calha de selo", selo1_to, 1])
                elif selo1_from != selo1_to and selo2_from == selo2_to:
                    if selo1_to == selo2_to:
                        list_selo.append(["Calha de selo", selo2_to, 2])
                    else:
                        list_selo.append(["Calha de selo", selo2_to, 1])

                elif selo1_from != selo1_to and selo2_from != selo2_to:
                    if selo1_to == selo2_to:
                        list_selo.append(["Calha de selo", selo1_to, 2])
                    else:
                        list_selo.append(["Calha de selo", selo1_to, 1])
                        list_selo.append(["Calha de selo", selo2_to, 1])

    df_term = pd.DataFrame(list_term, columns=["Item", "Código", "Quantidade"])

    df_selo = pd.DataFrame(list_selo, columns=["Item", "Código", "Quantidade"])

    df_consl = (
        pd.concat([df_term, df_selo], ignore_index=False)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return df_consl


def melhorar_saida(df_d):
    for k in df_d:
        df = df_d[k]

        if k == "Quantidade Tooling":
            df_d[k] = df[
                df["Código"].notna()
                & ~df["Código"].astype(str).str.lower().isin(["nan", "none", ""])
            ].reset_index(drop=True)

        if k == "Problemas com bobina de term.":
            df_d[k] = df[
                df["Terminais"].astype(str).str.upper() != "TERMINAL"
            ].reset_index(drop=True)

    return df_d


def adicionar_volumes(df_dict, mcr=1000):
    df_path = consultar_arquivos_base(id_name="Take_Rates")

    with open(df_path, "rb") as f:
        df_temp = pd.read_excel(f)

    dict_temp = {
        row["Derivativos"]: row["Take Rates (%)"] for i, row in df_temp.iterrows()
    }

    lista_cr = ["WIRE", "MULTICORE", "TUBE", "SPLICE", "MULTICRIMP"]

    for k in df_dict.keys():
        if k in lista_cr:
            df_temp1 = df_dict[k].reset_index(drop=True)
            colunas_alvo = df_temp1.columns

            coluna_ponto = []
            for k2 in dict_temp.keys():
                for c in colunas_alvo:
                    if str(k2) in str(c):
                        coluna_ponto.append(c)
                        novo_valor = dict_temp[k2]
                        for i in df_temp1.index:
                            valor_atual = df_temp1.loc[i, c]
                            if pd.notna(valor_atual) and str(
                                valor_atual
                            ).strip() not in ["-", "", "nan"]:
                                df_temp1.loc[i, c] = (
                                    novo_valor  # <- aplica o valor do dicionário
                                )

            coluna_ponto = list(set(coluna_ponto))
            if coluna_ponto:
                df_temp1[coluna_ponto] = df_temp1[coluna_ponto].apply(
                    pd.to_numeric, errors="coerce"
                )
                take_rates_raw = df_temp1[coluna_ponto].sum(axis=1)
                df_temp1["Volume"] = (take_rates_raw * mcr) / 100
                df_temp1["Take Rates (%)"] = take_rates_raw.apply(
                    lambda x: f"{x / 100:.2%}"
                )

            df_dict[k] = df_temp1

        if "WIRE" == k:
            colunas_ord = [
                "Nome do arquivo",
                "CR",
                "Take Rates (%)",
                "Volume",
                "Tab",
                "Change",
                "Wire Nb",
                "Multicore",
                "Sub-Assembly",
                "Wire Type",
                "Unm.Length",
                "Length Type",
                "Offset Value",
                "Modified Length",
                "Modified Length_2",
                "Unmodified Length",
                "Unmodified Length_2",
                "Delta",
                "M",
                "Ft",
                "Color",
                "Int.PN",
                "Mat Code",
                "Wire Spec",
                "CSA",
                "Options/Modules",
                "Inc.BOM",
                "Inc.Chart",
                "Strip 1",
                "Term.1",
                "Term.1 Cust",
                "Term.Mat 1 ",
                "Seal 1",
                "Seal 1 Cust",
                "Node 1",
                "Connector 1 Cust.PN",
                "Cav.1",
                "Note 1",
                "Strip 2",
                "Term.2",
                "Term.2 Cust",
                "Term.Mat 2 ",
                "Seal 2",
                "Seal 2 Cust",
                "Node 2",
                "Connector 2 Cust.PN",
                "Cav.2",
                "Note 2",
                "Joint Type",
                "Joint 1",
                "Joint 2",
            ]
            df_dict[k] = reordenar_colunas(df_dict[k], colunas_ord)

        if "MULTICORE" == k:
            colunas_ord = [
                "Nome do arquivo",
                "CR",
                "Take Rates (%)",
                "Volume",
                "Tab",
                "Change",
                "Mult.Wire Nb",
                "Wire Type",
                "Length",
                "Length_2",
                "Delta",
                "M",
                "Ft",
                "Int.PN",
                "Wire Spec",
                "Inc.BOM",
                "Inc.Chart",
                "CutBack1",
                "CutBack2",
                "W1",
                "W2",
                "W3",
            ]
            df_dict[k] = reordenar_colunas(df_dict[k], colunas_ord)

        if "TUBE" == k:
            colunas_ord = [
                "Nome do arquivo",
                "CR",
                "Take Rates (%)",
                "Volume",
                "Tab",
                "Change",
                "tube Nb",
                "Int.PN",
                "Length",
                "Length_2",
                "Delta",
                "M",
                "Ft",
                "Cut-back",
                "Insulated Length",
                "Ins.Type",
                "Note",
                "Description",
                "Mater",
                "Type",
                "Int.Diameter",
                "Group",
                "Color",
                "Slit",
                "Conv",
                "Wall Th.",
                "Layer",
                "Node 1",
                "Node 2",
            ]
            df_dict[k] = reordenar_colunas(df_dict[k], colunas_ord)

        if "SPLICE" == k:
            colunas_ord = ["Nome do arquivo", "CR", "Take Rates (%)", "Volume"]
            df_dict[k] = reordenar_colunas(df_dict[k], colunas_ord)

        if "MULTICRIMP" == k:
            colunas_ord = ["Nome do arquivo", "CR", "Take Rates (%)", "Volume"]
            df_dict[k] = reordenar_colunas(df_dict[k], colunas_ord)

        df_dict[k] = df_dict[k].dropna(how="all", axis=1)

    return df_dict


def verificar_impedancia(df_mult):
    # Separar os dados por aba/tab
    df_from = df_mult[df_mult["Tab"] == "From"].reset_index(drop=True)
    df_to = df_mult[df_mult["Tab"] == "To"].reset_index(drop=True)

    # Encontrar os índices onde há "TW" na coluna 'Mult.Wire Nb'
    index_from = df_from[df_from["Mult.Wire Nb"].str.contains("TW", na=False)].index
    index_to = df_to[df_to["Mult.Wire Nb"].str.contains("TW", na=False)].index

    # Verificar quais índices existem em 'to' mas não em 'from'
    index_only_in_to = index_to.difference(index_from)

    # Criar coluna vazia se ainda não existir
    if "Teste Impedância" not in df_to.columns:
        df_to["Análise"] = ""

    # Marcar os que precisam de teste de impedância
    df_to.loc[index_only_in_to, "Análise"] = (
        "Teste Impedância, verificar necessidade de máquina"
    )

    df_to.dropna(how="all", axis=1, inplace=True)

    # Lista de valores a remover (colunas que só contêm UM desses valores)
    valores_a_remover = ["-", "0", "0.0", 0, "X", "false", "true", " "]

    for valor in valores_a_remover:
        df_to = df_to.loc[:, ~(df_to.eq(valor).all())]

    # Remover colunas com apenas None ou NaN
    df_to = df_to.loc[:, ~df_to.isna().all()]

    colunas_ord = ["Análise"]

    df_to = reordenar_colunas(df_to, colunas_ord)

    return df_to


def calcular_folhas_necessarias(
    qtd_itens, identificacoes_por_item=3, identificacoes_por_folha=6
):
    total_identificacoes = qtd_itens * identificacoes_por_item
    return math.ceil(total_identificacoes / identificacoes_por_folha)


def add_papelaria(df):
    df_new = pd.DataFrame()
    linha_control = 0

    tipos = ["Add Circuitos Wire", "Add Circuitos Splices", "Add Circuitos Multicrimp"]

    for c in df.columns:
        for tipo in tipos:
            if tipo in c:
                try:
                    itens = int(df.loc[0, c])
                except ValueError:
                    itens = 0
                etiquetas_kanbam = calcular_folhas_necessarias(
                    itens, identificacoes_por_item=3, identificacoes_por_folha=6
                )
                papel_polaseal = calcular_folhas_necessarias(
                    itens, identificacoes_por_item=3, identificacoes_por_folha=6
                )
                identificacoes_rack = calcular_folhas_necessarias(
                    itens, identificacoes_por_item=2, identificacoes_por_folha=30
                )

                df_new.loc[linha_control, "Item"] = c
                df_new.loc[
                    linha_control, "Necessidade de folhas A4 para Etiquetas Kanbam"
                ] = etiquetas_kanbam
                df_new.loc[
                    linha_control,
                    "Necessidade de folhas A4 para identificações de Rack",
                ] = identificacoes_rack
                df_new.loc[
                    linha_control, "Necessidade de Polaseal A4 para Etiquetas Kanbam"
                ] = papel_polaseal
                linha_control += 1

    # Adiciona linha de total ao final
    total_row = {
        "Item": "TOTAL",
        "Necessidade de folhas A4 para Etiquetas Kanbam": df_new[
            "Necessidade de folhas A4 para Etiquetas Kanbam"
        ].sum(),
        "Necessidade de folhas A4 para identificações de Rack": df_new[
            "Necessidade de folhas A4 para identificações de Rack"
        ].sum(),
        "Necessidade de Polaseal A4 para Etiquetas Kanbam": df_new[
            "Necessidade de Polaseal A4 para Etiquetas Kanbam"
        ].sum(),
    }

    df_new = pd.concat([df_new, pd.DataFrame([total_row])], ignore_index=True)

    return df_new


def relatorio_check_uscar_21(df:pd.DataFrame=None,uscar21_df:pd.DataFrame=None) -> None:
    colunas_add = ["Term.1", "Term.2","Seal 1","Seal 2"]    

    for col in colunas_add:
        if col not in df.columns:
            df[col] = None

    lista_terminais = []

    lista_de_circuitos = df["Wire Nb"].dropna().unique().tolist() 
    for ckt in lista_de_circuitos:
        df_ckt = df[df["Wire Nb"] == ckt].reset_index(drop=True)
        if len(df_ckt) == 2:

            termA_0 = df_ckt.loc[0, 'Term.1'] if pd.notna(df_ckt.loc[0, 'Term.1']) else 0
            termA_1 = df_ckt.loc[1, 'Term.1'] if pd.notna(df_ckt.loc[1, 'Term.1']) else 0

            termB_0 = df_ckt.loc[0, 'Term.2'] if pd.notna(df_ckt.loc[0, 'Term.2']) else 0
            termB_1 = df_ckt.loc[1, 'Term.2'] if pd.notna(df_ckt.loc[1, 'Term.2']) else 0


            if (termA_0 == termA_1 and termB_0 == termB_1) or (termA_0 == termB_1 and termB_0 == termA_1):
                pass
            elif (termA_0 != termA_1 and termB_0 != termB_1) or (termA_0 != termB_1 and termB_0 != termA_1):
                if pd.notna(df_ckt.loc[1, 'Term.1']):
                    lista_terminais.append(df_ckt.loc[1, 'Term.1'])
                if pd.notna(df_ckt.loc[1, 'Term.2']):
                    lista_terminais.append(df_ckt.loc[1, 'Term.2'])

            elif (termA_0 != termA_1 and termB_0 == termB_1):
                lista_de_circuitos.append(df_ckt.loc[1, 'Term.1'])
            elif (termA_0 == termA_1 and termB_0 != termB_1):
                lista_de_circuitos.append(df_ckt.loc[1, 'Term.2'])

    lista_terminais = list(set(lista_terminais))
    df_check = uscar21_df[(uscar21_df['Term'].isin(lista_terminais) & (uscar21_df['Tab']=='To'))].reset_index(drop=True)


    if 'Seal' not in df_check.columns:
        df_check['Seal'] = None

    df_prov = df_check.groupby(["Term", "CSA"], as_index=False).agg(
        {   "Legacy 1": "first",
            "Seal": "first",
            "Circuito": lambda x: ",".join(dict.fromkeys(map(str, x))),
            "Tipo de validação": lambda x: ",".join(dict.fromkeys(map(str, x))),
            "Relatório - Externo": lambda x: ",".join(dict.fromkeys(map(str, x))),
            "Comentários": lambda x: ",".join(dict.fromkeys(map(str, x))),
            'Tipo Cabo 1': lambda x: ",".join(dict.fromkeys(map(str, x))),
        }
    )
    df_prov[['Circuito', 'Legacy 1', 'CSA', 'Term','Seal','Comentários', 'Tipo de validação', 'Relatório - Externo']]

    return df_prov


def verificar_ranger_de_app(df_wire: pd.DataFrame = None):
    # Supondo que 'consultar_arquivos_base' retorna o caminho do arquivo
    lista_de_term = consultar_arquivos_base(id_name="terminais_sem")
    
    # Abrindo o arquivo com a lista de terminais
    with open(lista_de_term, "rb") as f:
        df_term = pd.read_excel(f)

    # Criando dicionários para min e max range
    min_range = limpar_dict({row['Part Number']: float(row['Min Wire Size (mm^2)']) for i, row in df_term.iterrows()})
    max_range = limpar_dict({row['Part Number']: float(row['Max Wire Size (mm^2)']) for i, row in df_term.iterrows()})
    Technology = limpar_dict({row['Part Number']: row['Connection Technology'] for i, row in df_term.iterrows()})


    # Adicionando a coluna de "Ranger de Aplicação" ao df_wire
    df_wire['Ranger de Aplicação'] = None
    df_wire['Connection Technology'] = None

    # Loop para verificar o ranger de aplicação
    for i in df_wire.index:
        part_number = df_wire.loc[i, 'Term']
        csa = float(df_wire.loc[i, 'CSA'])

        df_wire.loc[i,'Connection Technology'] = Technology.get(df_wire.loc[i, 'Term'])

        # Verificando se o 'Part Number' existe nos dicionários min_range e max_range
        if part_number in min_range and part_number in max_range:
            min_value = min_range[part_number]
            max_value = max_range[part_number]
            
            # Verificando se o CSA está dentro do intervalo válido
            if min_value <= csa <= max_value:
                df_wire.loc[i, 'Ranger de Aplicação'] = 'Aplicação correta'
            else:
                df_wire.loc[i, 'Ranger de Aplicação'] = 'Aplicação incorreta ou Cravação dupla ou Multicrimp'
        else:
            df_wire.loc[i, 'Ranger de Aplicação'] = 'Part Number não encontrado'


    df_wire = df_wire[df_wire['Ranger de Aplicação'].str.contains('Aplicação incorreta')].reset_index(drop=True).drop(columns=['Tipo de validação'])

    return df_wire



def relatorio_consolidado(uscar21_df:pd.DataFrame=None, splice_df:pd.DataFrame=None, mult_df:pd.DataFrame=None) -> None:

    # Informações de Uscar21 -----------------------------------------------------------------------------------------------------------------
    if uscar21_df is not None:
        uscar21_df = uscar21_df.reset_index(drop=True)


        if 'Seal' not in uscar21_df.columns:
            uscar21_df['Seal'] = None

        uscar21_df['CHP'] = None

        

        for i in uscar21_df.index:
            term = uscar21_df.loc[i, 'Term']
            seal = uscar21_df.loc[i, 'Seal'] if pd.notna(uscar21_df.loc[i, 'Seal']) else ''
            csa = uscar21_df.loc[i, 'CSA']
            legacy = uscar21_df.loc[i, 'Legacy 1']

            uscar21_df.loc[i,'CHP'] = f'{term}-{legacy}-{csa}-{seal}-USCAR21'


        if 'Relatório - Externo' not in uscar21_df.columns:
            uscar21_df['Relatório - Externo'] = None

        uscar21_df = uscar21_df[['CR', 'CHP', 'Circuito','Relatório - Externo']].rename(columns={'Relatório - Externo':'Uscar21'})
        uscar21_df['Tipo de validação'] = 'USCAR21'

        uscar21_df.rename(columns={'Uscar21':'Relatório', 'Circuito':'Circuitos'}, inplace=True)
    else:
        uscar21_df = pd.DataFrame(columns=['CR', 'CHP', 'Circuitos','Relatório','Tipo de validação'])  # Inicialização vazia

    # Informações de Splices -----------------------------------------------------------------------------------------------------------------
    if splice_df is not None:

        splice_df = splice_df.reset_index(drop=True)

        df_prov_sp = splice_df[splice_df['Tab']=='To'].reset_index(drop=True)

        df_prov_sp['Circuitos'] = None
        df_prov_sp['CHP'] = None

        for i in df_prov_sp.index:
            splice_name = df_prov_sp.loc[i, 'Splice Name']
            extra_comp = df_prov_sp.loc[i, 'Extra Component PN']

            sp_left  = ['L1','L2','L3','L4','L5','L6','L7','L8','L9','L10']
            sp_right = ['R1','R2','R3','R4','R5','R6','R7','R8','R9','R10']
            csa_left  = ['L1_CSA','L2_CSA','L3_CSA','L4_CSA','L5_CSA','L6_CSA','L7_CSA','L8_CSA','L9_CSA','L10_CSA']
            csa_right = ['R1_CSA','R2_CSA','R3_CSA','R4_CSA','R5_CSA','R6_CSA','R7_CSA','R8_CSA','R9_CSA','R10_CSA']

            # sp_left
            cols_exist = [c for c in sp_left if c in df_prov_sp.columns]
            vals = df_prov_sp.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            left_id = '+'.join(vals)

            # sp_right
            cols_exist = [c for c in sp_right if c in df_prov_sp.columns]
            vals = df_prov_sp.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            right_id = '+'.join(vals)

            if left_id and right_id:
                sp = f"{left_id} | {right_id}"
            elif left_id:
                sp = left_id
            elif right_id:
                sp = right_id
            else:
                sp = ""


            # csa_sp_left
            cols_exist = [c for c in csa_left  if c in df_prov_sp.columns]
            vals = df_prov_sp.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            csa_left_id = '+'.join(vals)

            # csa_sp_right
            cols_exist = [c for c in csa_right if c in df_prov_sp.columns]
            vals = df_prov_sp.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            csa_right_id = '+'.join(vals)


            if csa_left_id and csa_right_id:
                csa_sp = f"{csa_left_id} | {csa_right_id}"
            elif csa_left_id:
                csa_sp = csa_left_id
            elif csa_right_id:
                csa_sp = csa_right_id
            else:
                csa_sp = ""

            df_prov_sp.loc[i,'Circuitos'] = sp
            df_prov_sp.loc[i, 'CHP'] = csa_sp


        if 'USCAR_45' not in df_prov_sp.columns:
            df_prov_sp['USCAR_45'] = None  # Ou algum valor padrão

        if 'GMW17136' not in df_prov_sp.columns:
            df_prov_sp['GMW17136'] = None  # Ou algum valor padrão


        df_prov_sp = df_prov_sp[['CR','CHP','Circuitos','Splice Name','CSA Total','CSA Right','CSA Left','Extra Component PN','USCAR_45', 'GMW17136']].rename(columns={'Extra Component PN':'Termo'})

        df_prov = df_prov_sp.groupby(["CHP", "Termo"], as_index=False).agg(
            {   "CR":"first",
                "Circuitos": lambda x: ",".join(dict.fromkeys(map(str, x))),
                "Splice Name": lambda x: ",".join(dict.fromkeys(map(str, x))),
                "USCAR_45": lambda x: ",".join(dict.fromkeys(map(str, x))),
                "GMW17136": lambda x: ",".join(dict.fromkeys(map(str, x))),
                'CSA Total': lambda x: ",".join(dict.fromkeys(map(str, x))),
                'CSA Right': lambda x: ",".join(dict.fromkeys(map(str, x))),
                'CSA Left': lambda x: ",".join(dict.fromkeys(map(str, x))),
            }
        )
        df_prov = df_prov[['CR', 'CHP', 'Circuitos', 'Splice Name', 'Termo','CSA Left','CSA Right','CSA Total', 'USCAR_45','GMW17136']]

        df_1 = df_prov[['CR', 'CHP', 'Circuitos', 'Splice Name','CSA Left','CSA Right','CSA Total', 'USCAR_45']].rename(columns={'USCAR_45':'Relatório'})
        df_1['Tipo de validação'] = 'USCAR45'
        df_2 = df_prov[['CR', 'CHP', 'Circuitos', 'Splice Name','CSA Left','CSA Right','CSA Total', 'Termo','GMW17136']].rename(columns={'GMW17136':'Relatório'})
        df_2['Tipo de validação'] = 'GMW17136'
    else:
        df_prov = pd.DataFrame()  # Inicialização vazia
        df_1 = pd.DataFrame(columns=['CR', 'CHP', 'Circuitos', 'Splice Name','CSA Left','CSA Right','CSA Total', 'Termo','Relatório','Tipo de validação'])  # Inicialização vazia
        df_2 = pd.DataFrame(columns=['CR', 'CHP', 'Circuitos', 'Splice Name','CSA Left','CSA Right','CSA Total', 'Termo','Relatório','Tipo de validação'])  # Inicialização vazia

    # Informações de Multicrimp -----------------------------------------------------------------------------------------------------------------
    if mult_df is not None:
        mult_df = mult_df.reset_index(drop=True)
        mult_df = mult_df[mult_df['Tab']=='To'].reset_index(drop=True)

        mult_df['Circuitos'] = None
        mult_df['CHP'] = None

        for i in mult_df.index:
            mult_name = mult_df.loc[i, 'M.Crimp Name']
            Terminal = mult_df.loc[i, 'Terminal']

            ckt  = ['W1', 'W2', 'W3','W4','W5','W6','W7','W8','W9','W10']
            csa  = ['W1_CSA','W2_CSA','W3_CSA','W4_CSA','W5_CSA','W6_CSA','W7_CSA','W8_CSA','W9_CSA','W10_CSA']

            cols_exist = [c for c in ckt if c in mult_df.columns]
            vals = mult_df.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            ckt_id = '+'.join(vals)

            cols_exist = [c for c in csa if c in mult_df.columns]
            vals = mult_df.loc[i, cols_exist].astype(str).tolist()
            vals = [v.strip() for v in vals if v.strip() not in ['', 'nan']]
            csa_id = '+'.join(vals)

            mult_df.loc[i, 'Circuitos'] = ckt_id
            mult_df.loc[i, 'CHP'] = csa_id

        colunas_add = ['M.Crimp Name', 'Extra Component','USCAR_38']
        for i in colunas_add:
            if i not in mult_df.columns:
                mult_df[i] = None

        mult_df = mult_df[['CR','Terminal','CSA Total', 'M.Crimp Name','Extra Component','USCAR_38', 'Circuitos', 'CHP']].rename(columns={'M.Crimp Name':'Processo','Extra Component':'Termo'})

        mult_df_prov = mult_df.groupby(["CHP", "Terminal","Termo"], as_index=False).agg(
            {   "CR":"first",
                "Circuitos": lambda x: ",".join(dict.fromkeys(map(str, x))),
                "Terminal": lambda x: ",".join(dict.fromkeys(map(str, x))),
                "USCAR_38": lambda x: ",".join(dict.fromkeys(map(str, x))),
                'CSA Total': lambda x: ",".join(dict.fromkeys(map(str, x)))
                # 'CSA Left': lambda x: ",".join(dict.fromkeys(map(str, x))),
                # 'CSA Right': lambda x: ",".join(dict.fromkeys(map(str, x))),
            }   
        )
        mult_df_prov = mult_df_prov[['CR', 'CHP', 'Circuitos', 'Terminal','CSA Total', 'Termo', 'USCAR_38']].rename(columns={'USCAR_38':'Relatório'})
        mult_df_prov['Tipo de validação'] = 'USCAR38'
    else:
        mult_df_prov = pd.DataFrame(columns=['CR', 'CHP', 'Circuitos', 'Terminal','CSA Total', 'Termo','Relatório','Tipo de validação'])


    df_final = pd.concat([uscar21_df, df_1, df_2], ignore_index=True)

    df_final = df_final[['CR', 'CHP', 'Circuitos','Splice Name','CSA Left','CSA Right','CSA Total', 'Termo','Relatório', 'Tipo de validação']].rename(columns={'Splice Name':'Processo'})


    df_final = pd.concat([df_final, mult_df_prov], ignore_index=True)

    cols_exist = ['CR', 'CHP','CSA Left','CSA Right','CSA Total', 'Circuitos','Processo', 'Terminal','Termo','Relatório', 'Tipo de validação']

    missing = [c for c in cols_exist if c not in df_final.columns]
    for c in missing:
        df_final[c] = pd.NA

    # Opcional: ordena/filtra para manter apenas as que você quer
    df_final = df_final[cols_exist]

    for i in df_final.index:
        if df_final.loc[i, 'Tipo de validação'] == 'USCAR21':
            df_final.loc[i, 'Terminal'] = str(df_final.loc[i, 'CHP']).split('-')[0]


    data_atual = datetime.now().strftime("%d-%m-%Y")  # Data no formato DD-MM-YYYY
    hora_atual = datetime.now().strftime("%H:%M:%S")  # Hora no formato HH:MM:SS


    df_final['Data'] = data_atual
    df_final['Hora'] = hora_atual
    df_final = df_final[['Data','Hora','CR', 'CHP','CSA Left','CSA Right','CSA Total', 'Circuitos','Processo', 'Terminal','Termo','Relatório', 'Tipo de validação']]
    return df_final


def atualizar_relatorio(caminho_arquivo: str = None, df_new: dict = None) -> pd.DataFrame:
    # Verificação de parâmetros
    if df_new is None:
        raise ValueError("O parâmetro 'df_new' não pode ser None.")
    
    # Dicionário de mapeamento de chaves para nomes de DataFrames
    chaves = ['Delta Uscar21', 'SPLICE', 'MULTICRIMP']
    dfs = {}

    # Iterando sobre as chaves e populando o dicionário de DataFrames
    for key in chaves:
        if key in df_new.keys():
            dfs[key] = df_new[key]

    # Agora você pode acessar os DataFrames através do dicionário 'dfs'
    df_rel = relatorio_consolidado(
        uscar21_df=dfs.get('Delta Uscar21'),
        splice_df=dfs.get('SPLICE'),
        mult_df=dfs.get('MULTICRIMP')
    )

    # Verificando se o arquivo existe, e criando se necessário
    if not os.path.exists(caminho_arquivo):
        new_df = pd.DataFrame(columns=['Data','Hora','CR', 'CHP','CSA Left','CSA Right','CSA Total', 
                                       'Circuitos','Processo', 'Terminal','Termo','Relatório', 'Tipo de validação'])
        new_df.to_excel(caminho_arquivo, index=False)

    # Lendo o arquivo Excel
    df_base = pd.read_excel(caminho_arquivo)


    colunas_add = ['Terminal']

    for i in colunas_add:
        if i in df_rel.columns:
            df_rel[i] = None


    # Garantindo que as colunas estejam no formato correto (string)
    for col in ['CSA Left', 'CSA Right', 'CSA Total']:
        df_base[col] = df_base[col].astype(str)
        df_rel[col] = df_rel[col].astype(str)

    # Realizando a junção

    colunas_form = ['Data','Hora','CR', 'CHP','CSA Left','CSA Right','CSA Total','Circuitos','Processo', 'Terminal','Termo','Relatório', 'Tipo de validação']

    for i in colunas_form:
        if i in df_base.columns:
            df_base[i] = df_base[i].astype(str)
        if i in df_rel.columns:
            df_rel[i] = df_rel[i].astype(str)


    df_joined = pd.merge(df_base, df_rel, how='outer', suffixes=('_df1', '_df2'))

    df_joined.to_excel(caminho_arquivo,index=False)


def consolidar_cuts(diretorio, cr_name: str = False):
    # try:
    #     encontrar_arquivos_zip(diretorio)
    #     extrair_zip(encontrar_arquivos_zip(diretorio),diretorio)
    # except: pass

    lista_de_arquivos = encontrar_arquivos_excel(diretorio)

    lista_de_path = encontrar_arquivos_excel_charted(diretorio)

    df_consolidado = {}

    itens_analisados = []
    contador = 0
    for path in tqdm(lista_de_arquivos, "[*] Processando...", colour="blue"):
        tqdm.write(
            f"[+] Iniciando a análise: {os.path.basename(path).replace('.xlsx', '')}"
        )

        try:
            abas = pd.read_excel(path, sheet_name=None)  # Retorna dict de abas
            nomes_abas = list(abas.keys())
            # continue aqui
        except Exception as e:
            logger.error(f"Erro ao ler {path}: {e}")

        df_WIRE_consolidado = pd.DataFrame()
        df_MULTICORE_consolidado = pd.DataFrame()
        df_TUBE_consolidado = pd.DataFrame()
        df_SPLICE_consolidado = pd.DataFrame()
        df_MULTICRIMP_consolidado = pd.DataFrame()
        dict_consolidado = {}

        for aba in nomes_abas:
            if aba != "Summary" and aba == "Composite":
                with open(path, "rb") as f:
                    df = pd.read_excel(f, sheet_name=aba)

                lista = ["DELTA WIRE", "MULTICORE", "TUBE", "SPLICE", "MULTICRIMP"]

                # Chama a função
                indices = encontrar_indices_palavras(df, lista)

                nome_arquivo = os.path.basename(path)

                diretorio_pai = os.path.dirname(path)

                nome_pasta = f"{os.path.basename(diretorio_pai)}_{contador}"

                # WIRE
                df_WIRE = (
                    df.loc[indices[0] + 1 : indices[1] - 1]
                    .dropna(how="all")
                    .reset_index(drop=True)
                )
                df_WIRE.columns = df_WIRE.iloc[
                    0
                ]  # Define a primeira linha como os nomes das colunas
                df_WIRE = df_WIRE.drop(0).reset_index(
                    drop=True
                )  # Remove a linha 0 e redefine o índice
                df_WIRE["Nome do arquivo"] = nome_arquivo
                df_WIRE = renomear_colunas(df_WIRE)

                df_WIRE_consolidado = pd.concat(
                    [df_WIRE_consolidado, df_WIRE], ignore_index=False
                )

                # MULTICORE
                df_MULTICORE = (
                    df.loc[indices[1] + 1 : indices[2] - 1]
                    .dropna(how="all")
                    .reset_index(drop=True)
                )
                df_MULTICORE.columns = df_MULTICORE.iloc[
                    0
                ]  # Define a primeira linha como os nomes das colunas
                df_MULTICORE = df_MULTICORE.drop(0).reset_index(
                    drop=True
                )  # Remove a linha 0 e redefine o índice
                df_MULTICORE = renomear_colunas(df_MULTICORE)
                df_MULTICORE_consolidado = pd.concat(
                    [df_MULTICORE_consolidado, df_MULTICORE], ignore_index=False
                )

                # TUBE
                if len(indices) > 3:
                    df_TUBE = (
                        df.loc[indices[2] + 1 : indices[3] - 1]
                        .dropna(how="all")
                        .reset_index(drop=True)
                    )
                    df_TUBE.columns = df_TUBE.iloc[
                        0
                    ]  # Define a primeira linha como os nomes das colunas
                    df_TUBE = df_TUBE.drop(0).reset_index(
                        drop=True
                    )  # Remove a linha 0 e redefine o índice
                    df_TUBE = renomear_colunas(df_TUBE)
                    df_TUBE_consolidado = pd.concat(
                        [df_TUBE_consolidado, df_TUBE], ignore_index=False
                    )
                else:
                    df_TUBE = pd.DataFrame()
                    df_TUBE_consolidado = pd.concat(
                        [df_TUBE_consolidado, df_TUBE], ignore_index=False
                    )

                # SPLICE
                if len(indices) > 4:
                    df_SPLICE = (
                        df.loc[indices[3] + 1 : indices[4] - 1]
                        .dropna(how="all")
                        .reset_index(drop=True)
                    )
                    df_SPLICE.columns = df_SPLICE.iloc[
                        0
                    ]  # Define a primeira linha como os nomes das colunas
                    df_SPLICE = df_SPLICE.drop(0).reset_index(
                        drop=True
                    )  # Remove a linha 0 e redefine o índice
                    df_SPLICE = renomear_colunas(df_SPLICE)
                    df_SPLICE_consolidado = pd.concat(
                        [df_SPLICE_consolidado, df_SPLICE], ignore_index=False
                    )
                else:
                    df_SPLICE = pd.DataFrame()
                    df_SPLICE_consolidado = pd.concat(
                        [df_SPLICE_consolidado, df_SPLICE], ignore_index=False
                    )

                # MULTICRIMP
                if len(indices) > 5:
                    df_MULTICRIMP = (
                        df.loc[indices[4] + 1 : indices[5] - 1]
                        .dropna(how="all")
                        .reset_index(drop=True)
                    )
                    df_MULTICRIMP.columns = df_MULTICRIMP.iloc[
                        0
                    ]  # Define a primeira linha como os nomes das colunas
                    df_MULTICRIMP = df_MULTICRIMP.drop(0).reset_index(
                        drop=True
                    )  # Remove a linha 0 e redefine o índice
                    df_MULTICRIMP = renomear_colunas(df_MULTICRIMP)
                    df_MULTICRIMP_consolidado = pd.concat(
                        [df_MULTICRIMP_consolidado, df_MULTICRIMP], ignore_index=False
                    )
                else:
                    df_MULTICRIMP = pd.DataFrame()
                    df_MULTICRIMP_consolidado = pd.concat(
                        [df_MULTICRIMP_consolidado, df_MULTICRIMP], ignore_index=False
                    )

        dict_consolidado["WIRE"] = df_WIRE_consolidado
        dict_consolidado["MULTICORE"] = df_MULTICORE_consolidado
        dict_consolidado["TUBE"] = df_TUBE_consolidado
        dict_consolidado["SPLICE"] = df_SPLICE_consolidado
        dict_consolidado["MULTICRIMP"] = df_MULTICRIMP_consolidado



        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 1. Problemas com a EVO, circuitos menores que 200 e pernas de splices.
        try:
            df_prob_evo = verificar_EVO(dict_consolidado["WIRE"])
        except:
            df_prob_evo = pd.DataFrame()

        if len(df_prob_evo) > 0:
            dict_consolidado["Problemas com EVO"] = df_prob_evo
            itens_analisados.append(f"1. Atenção: encontrados {len(df_prob_evo)} circuitos < 200 nas splices, o que pode gerar problemas na EVO.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 2. -> Checar se existe twister com bitola maior ou igual a 1.5, se sim não podem serem feitas na máquina sigma, imapcto no Lead Prep.
        try:
            df_prob_tw = verificar_twister_bitola(dict_consolidado["WIRE"])
        except:
            df_prob_tw = pd.DataFrame()

        if len(df_prob_tw) > 0:
            dict_consolidado["Problemas com TW 1.5"] = df_prob_tw
            itens_analisados.append(f"2. Atenção: encontrados {len(df_prob_tw)} Twisters com bitola ≥ 1.5, que não podem ser processados na Sigma, impactando o Lead Prep.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 3. -> Twister com 'open ends', uma perna menor que a outra, menores que 460mm, a sigma não processa - Problemas.
        try:
            df_prob_tw_comp = verificar_twister_comp(dict_consolidado["WIRE"])
        except:
            df_prob_tw_comp = pd.DataFrame()

        if len(df_prob_tw_comp) > 0:
            dict_consolidado["Problemas com TW Comp"] = df_prob_tw_comp
            itens_analisados.append(f"3. Atenção: encontrados {len(df_prob_tw_comp)} Twisters com 'open ends', uma perna menor e < 460mm, que não podem ser processados na Sigma, impactando o Lead Prep.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 4. Se a caracteristica critica (LGK-CC) mudou, se sim temos impacto no processo, criação de programas e rebalanceamento de maquinas.
        # 4.1 Se adicionou sim, e retirou tbm.
        df_1, df_2 = verificar_lgk_cc(dict_consolidado["WIRE"])

        if len(df_1) > 0:
            dict_consolidado["Problemas LGK-CC Adicionar"] = df_1
            itens_analisados.append(f'4. Atenção: inclusão de {len(df_1)} circuitos LGK-CC')
        if len(df_2) > 0:
            dict_consolidado["Problemas LGK-CC Remover"] = df_2
            itens_analisados.append(f"4.1. Atenção: exclusão de {len(df_2)} circuitos LGK-CC.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 5. Verificar se existe terminal com abastecimento a direita, não podemos ter.
        df_abs = verificar_term_abastecimento(dict_consolidado)

        if len(df_abs) > 0:
            dict_consolidado["Problemas com bobina de term."] = df_abs
            itens_analisados.append(f"5. Atenção: encontrados {len(df_abs)} terminais com abastecimento à direita.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 6. Verificar validação USCAR21:
        # 6.1 - Externo, sem considerar selos.
        # 6.2 - Interno, considerando selos.
        df_uscar = check_usar_21(dict_consolidado["WIRE"])

        if len(df_uscar) > 0:
            dict_consolidado["Análise WIRE Uscar21"] = df_uscar
            df_prov_uscar, _, _, _ = resumo_uscar21(
                dict_consolidado["Análise WIRE Uscar21"]
            )
            dict_consolidado["Resumo Uscar21"] = df_prov_uscar

            dict_consolidado["Delta Uscar21"] = relatorio_check_uscar_21(dict_consolidado["WIRE"],df_uscar)

            dict_consolidado["Problemas com Ranger de term"] = verificar_ranger_de_app(dict_consolidado["Resumo Uscar21"])
            itens_analisados.append(f"6. Analisados {len(df_uscar)} itens de Uscar21.")
            itens_analisados.append(f"6.1. Atenção: encontrados {len(dict_consolidado['Problemas com Ranger de term'])} circuitos com problemas no Ranger de aplicação.")


        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 7. Verificar validação USCAR45 + GMW.

        if len(dict_consolidado["SPLICE"]) > 0:
            arq_path = verificar_path_arquivos(path, lista_de_path)

            df_sp, df_U45, df_gmw17 = Check_splices(
                dict_consolidado["SPLICE"], dict_consolidado["WIRE"], arq_path
            )
            if len(df_sp) > 0:
                dict_consolidado["SPLICE"] = df_sp
            if len(df_U45) > 0:
                dict_consolidado["Análise SPLICE Uscar 45"] = df_U45
                itens_analisados.append(f"7. Analisados {len(df_U45)} itens de Uscar45.")
            if len(df_gmw17) > 0:
                dict_consolidado["Análise SPLICE GMW"] = df_gmw17
                itens_analisados.append(f"7.1. Analisados {len(df_gmw17)} itens de GMW17136.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 8. Verificar validação USCAR38 + GMW.

        if len(dict_consolidado["MULTICRIMP"]) > 0:
            arq_path = verificar_path_arquivos(path, lista_de_path)

            df_multic, df_u_38, df_gm_38 = check_multicrimp(
                dict_consolidado["MULTICRIMP"], dict_consolidado["WIRE"], arq_path
            )

            if len(df_multic) > 0:
                dict_consolidado["MULTICRIMP"] = df_multic

            if len(df_u_38) > 0:
                dict_consolidado["Análise MULT Uscar 38"] = df_u_38
                itens_analisados.append(f"8. Analisados {len(df_u_38)} itens de Uscar38.")

            if len(df_gm_38) > 0:
                dict_consolidado["Análise MULT GMW"] = df_gm_38
                itens_analisados.append(f"8.1. Analisados {len(df_gm_38)} itens de GMW17136.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 9. Análise de Tubos
        if len(dict_consolidado["TUBE"]) > 0:
            df_t = check_tubo(dict_consolidado["TUBE"])
            if len(df_t) > 0:
                dict_consolidado["Análise TUBOS"] = df_t
                itens_analisados.append(f"9. Analisados {len(df_t)} tubos.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 10. Quantidade Racks
        if (
            len(dict_consolidado["WIRE"]) > 0
            or len(dict_consolidado["SPLICE"]) > 0
            or len(dict_consolidado["MULTICRIMP"]) > 0
        ):
            df_rack = check_rack(
                dict_consolidado["WIRE"],
                dict_consolidado["SPLICE"],
                dict_consolidado["MULTICRIMP"],
            )
            if len(df_rack) > 0:
                dict_consolidado["Quantidade Racks"] = df_rack
                itens_analisados.append(f"10. Analisados {len(df_rack)} itens para racks.")

                # 10.1. Calculado papelaria
                if len(dict_consolidado["Quantidade Racks"]) > 0:
                    df_papel = add_papelaria(dict_consolidado["Quantidade Racks"])
                    dict_consolidado["Papelaria"] = df_papel
                    itens_analisados.append(f"10.1. Analisados {len(df_papel)} itens de papelaria.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 11. Quantidade de aplicadores
        if len(dict_consolidado["WIRE"]) > 0:
            df_appl = Check_quantidade_app(dict_consolidado["WIRE"])
            if len(df_appl) > 0:
                dict_consolidado["Quantidade Tooling"] = df_appl
                itens_analisados.append(f"11. Analisados {len(df_appl)} itens quanto à quantidade de aplicadores.")

        # -----------------------------------------------------------------------------------------------------------------------------------------
        # 12. Teste Impedância
        if len(dict_consolidado["MULTICORE"]) > 0:
            df_imp = verificar_impedancia(dict_consolidado["MULTICORE"])
            if len(df_imp) > 0:
                dict_consolidado["Teste Impedância - TW"] = df_imp
                itens_analisados.append(f"12. Atenção: encontrados {len(df_imp)} circuitos diretos para Twister.")


        # -----------------------------------------------------------------------------------------------------------------------------------------        
        # Resumo Consolidado
        df_consolid = report_resumo(dict_consolidado)
        if len(df_consolid) > 0:
            dict_consolidado["Resumo Consolidado"] = df_consolid

        ordem_desejada = [
            "Resumo Consolidado",
            "Análise WIRE Uscar21",
            "Resumo Uscar21",
            "Delta Uscar21",
            "Problemas com Ranger de term",
            "Quantidade Racks",
            "Papelaria",
            "Quantidade Tooling",
            "Problemas com EVO",
            "Problemas com TW 1.5",
            "Problemas com TW Comp",
            "Problemas LGK-CC Adicionar",
            "Problemas LGK-CC Remover",
            "Problemas com bobina de term.",
            "Teste Impedância - TW",
            "Análise SPLICE Uscar 45",
            "Análise SPLICE GMW",
            "Análise MULT Uscar 38",
            "Análise MULT GMW",
            "Análise TUBOS",
            "WIRE",
            "MULTICORE",
            "TUBE",
            "SPLICE",
            "MULTICRIMP",
        ]

        dict_consolidado = {
            k: dict_consolidado[k] for k in ordem_desejada if k in dict_consolidado
        }

        for k in dict_consolidado.keys():
            dict_consolidado[k] = limpar_colunas_redundantes(dict_consolidado[k])
            #dict_consolidado[k]['CR'] = cr_name


        contador += 1





        for k in dict_consolidado.keys():
            if len(dict_consolidado[k]) > 0:
                # Garante que seja DataFrame
                df_temp = dict_consolidado[k].copy()

                # Adiciona a coluna 'CR' com o nome da pasta
                df_temp["CR"] = cr_name if cr_name is None else nome_pasta

                # Reordena as colunas, colocando 'CR' primeiro
                colunas_ord = ["CR"]
                df_temp = reordenar_colunas(df_temp, colunas_ord)

                # Cria chave no df_consolidado se não existir
                if k not in df_consolidado:
                    df_consolidado[k] = pd.DataFrame()

                # Concatena no consolidado
                df_consolidado[k] = pd.concat(
                    [df_consolidado[k], df_temp], ignore_index=False
                )


        # diretorio = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Documents\2025\11.Nov\24-11-2025\Análise Investimentos"
        # caminho_arquivo = (
        #     f"{diretorio}/Resposta_CR_{cr_name}_Total_{contador}.xlsx"
        # )
        # salvar_dict_df_em_excel(
        #     dict_consolidado,
        #     caminho_arquivo,
        # )


        tqdm.write("[+] Finalizado.\n")
        os.system("cls")

    df_consolidado = melhorar_saida(df_consolidado)
    ordem_desejada = [
        "Resumo Consolidado",
        "Análise WIRE Uscar21",
        "Resumo Uscar21",
        "Delta Uscar21",
        "Problemas com Ranger de term",
        "Quantidade Racks",
        "Papelaria",
        "Quantidade Tooling",
        "Problemas com EVO",
        "Problemas com TW 1.5",
        "Problemas com TW Comp",
        "Problemas LGK-CC Adicionar",
        "Problemas LGK-CC Remover",
        "Problemas com bobina de term.",
        "Teste Impedância - TW",
        "Análise SPLICE Uscar 45",
        "Análise SPLICE GMW",
        "Análise MULT Uscar 38",
        "Análise MULT GMW",
        "Análise TUBOS",
        "WIRE",
        "MULTICORE",
        "TUBE",
        "SPLICE",
        "MULTICRIMP",
    ]
    df_consolidado = {
        k: df_consolidado[k] for k in ordem_desejada if k in df_consolidado
    }

    df_consolidado = adicionar_volumes(df_consolidado)

    return df_consolidado, itens_analisados

# # CÓDIGO
def listar_pastas(diretorio: str) -> list:
    """
    Lista todas as pastas (diretórios) em um diretório especificado, retornando os caminhos completos.
    
    :param diretorio: Caminho do diretório onde as pastas serão listadas.
    :return: Lista com os caminhos completos das pastas (diretórios) encontrados.
    """
    try:
        # Listar todas as pastas no diretório e obter o caminho completo
        pastas = [os.path.join(diretorio, pasta) for pasta in os.listdir(diretorio) if os.path.isdir(os.path.join(diretorio, pasta))]
        return pastas
    except FileNotFoundError:
        logger.error(f"O diretório {diretorio} não foi encontrado.")
        return []
    except PermissionError:
        logger.error(f"Permissão negada para acessar o diretório {diretorio}.")
        return []


def analisar(pasta_cr: str = None, pasta_salvar_racional: str = None, pasta_relatorio: str = None) -> None:
    # Análise
    df_consol, lista_itens = consolidar_cuts(pasta_cr) # pasta_cr

    # Atualiza o relatório com as CR analisadas
    atualizar_relatorio(pasta_relatorio,df_new=df_consol)

    # Salva o Racional
    caminho_arquivo = f"{pasta_salvar_racional}/Analise_CR_{pasta_cr.split("\\")[-1]}.xlsx"
    salvar_dict_df_em_excel(df_consol, caminho_arquivo)

    return lista_itens


def classificar_pastas(caminho):
    pastas_vazias = []
    pastas_cheias = []

    # Percorre todos os itens do diretório
    for nome in os.listdir(caminho):
        caminho_completo = os.path.join(caminho, nome)

        # Verifica se é uma pasta
        if os.path.isdir(caminho_completo):
            # Verifica se a pasta está vazia
            if not os.listdir(caminho_completo):  # Lista vazia → pasta vazia
                pastas_vazias.append(nome)
            else:
                pastas_cheias.append(nome)

    return pastas_vazias, pastas_cheias


def extrair_zips_flat(pasta):
    """
    Função que extrai arquivos de todos os arquivos .zip dentro da pasta
    fornecida, colocando os arquivos extraídos diretamente na pasta, sem
    recriar a estrutura de pastas interna do .zip.
    
    Args:
    pasta (str): O caminho da pasta onde os arquivos .zip estão localizados.
    """
    
    # Listar todos os arquivos .zip na pasta
    for arquivo in os.listdir(pasta):
        arquivo_zip = os.path.join(pasta, arquivo)

        # Verifica se é um arquivo .zip
        if arquivo_zip.endswith('.zip'):
            try:
                # Abrir o arquivo .zip
                with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
                    # Extrair todos os arquivos do .zip para a pasta de destino
                    for file_info in zip_ref.infolist():
                        # Pega o nome do arquivo sem as subpastas dentro do .zip
                        extracted_path = os.path.join(pasta, os.path.basename(file_info.filename))

                        # Se o arquivo extraído não for um diretório, extrai
                        if not file_info.is_dir():
                            # Verifica se o diretório onde o arquivo será extraído existe
                            extracted_dir = os.path.dirname(extracted_path)
                            if not os.path.exists(extracted_dir):
                                os.makedirs(extracted_dir)  # Cria as subpastas necessárias

                            # Extraímos o arquivo para o destino
                            with open(extracted_path, 'wb') as extracted_file:
                                extracted_file.write(zip_ref.read(file_info.filename))
                
                logger.info(f"Arquivos extraídos de {arquivo_zip.split("\\")[-1]} com sucesso!")

            except Exception as e:
                logger.error(f"Erro ao extrair o arquivo {arquivo_zip.split("\\")[-1]}: {e}")
        else:
            pass
            #logger.error(f"{arquivo} não é um arquivo .zip e foi ignorado.")


def analisador():
    # Limpeza da tela de forma cross-platform
    if os.name == 'nt':  # Para Windows
        os.system("cls")
    else:  # Para Linux/MacOS
        os.system("clear")

    logger.info("Analisador de CR")

    barras = 75

    while True:
        # Solicita a entrada do usuário
        numero = input("1. Para analisar uma CR por vez.\n2. Para analisar várias CR.\n3. Sair.\nEscolha uma opção (1/2/3): ")

        # Tenta converter a entrada para inteiro e verificar se está nas opções válidas
        try:
            numero = int(numero)  # Converte a entrada para inteiro
            if numero in [1, 2, 3]:
                break  # Sai do loop se a entrada for válida
            else:
                logger.error("Opção inválida. Tente novamente.")
        except ValueError:
            logger.verifique("Por favor, digite um número válido (1, 2 ou 3).")

    if numero == 1:

        logger.info("Entre com o caminho do arquivo do relatório")
        pasta_relatorio = input("[>] ").replace("/", "\\").replace('"', "")

        logger.info("Entre com o caminho da pasta onde quer salvar o racional")
        pasta_salvar_racional = input("[>] ").replace("/", "\\").replace('"', "")

        while True:

            logger.info("Entre com o caminho da pasta da CR ou Digite [Sair]")
            pasta_cr = input("[>] ").replace("/", "\\").replace('"', "")

            if pasta_cr.lower() == 'sair':
                break

            if os.path.exists(pasta_cr):  # Verifica se o diretório existe
                texto = f'Analisando a {pasta_cr.split("\\")[-1]}'
                logger.info(f'{texto} {"#" * (barras - len(texto))}')

                extrair_zips_flat(pasta_cr)

                lista_itens = analisar(pasta_cr=pasta_cr, pasta_salvar_racional=pasta_salvar_racional, pasta_relatorio=pasta_relatorio)

                logger.info(f'Itens encontrados e analisados nessa {pasta_cr.split("\\")[-1]}:')

                for i in lista_itens:
                    if 'Atenção' in i:
                        logger.atencao(f"{i}")
                    elif 'Analisados' in i:
                        logger.verifique(f"{i}")
                    else:
                        logger.info(f"{i}")

                texto = f'FIM'
                logger.info(f'{texto} {"#" * (barras - len(texto))}')
                print("\n")                      
            else:
                logger.error(f"Diretório {pasta_cr} não encontrado. Tente novamente.")
    
    elif numero == 2:
        logger.info("Entre com o caminho do arquivo do relatório")
        pasta_relatorio = input("[>] ").replace("/", "\\").replace('"', "")

        logger.info("Entre com o caminho da pasta onde quer salvar o racional")
        pasta_salvar_racional = input("[>] ").replace("/", "\\").replace('"', "")

        logger.info("Entre com o caminho do diretório onde estão todas as pastas das CR")
        pasta_cr = input("[>] ").replace("/", "\\").replace('"', "")

        vazias, cheias = classificar_pastas(pasta_cr)

        for p in vazias:
            logger.error(f'Pastas vazias: {p}')

        logger.info('Analisando')
        print('\n\n')

        if os.path.exists(pasta_cr):
            pasta_com_cr = listar_pastas(diretorio=pasta_cr) 
            for idx, pasta in enumerate(pasta_com_cr,start=1):
                if str(pasta.split("\\")[-1]) in cheias:

                    texto = f'Analisando a {pasta.split("\\")[-1]}'
                    logger.info(f'{texto} {"#" * (barras - len(texto))}')

                    extrair_zips_flat(pasta)
                    lista_itens = analisar(pasta_cr=pasta, pasta_salvar_racional=pasta_salvar_racional, pasta_relatorio=pasta_relatorio)

                    texto = f'Itens e encontrados e analisados nessa {pasta.split("\\")[-1]}'
                    logger.info(f'Itens encontrados e analisados nessa {pasta.split("\\")[-1]}:')

                    for i in lista_itens:
                        if 'Atenção' in i:
                            logger.atencao(f"{i}")
                        elif 'Analisados' in i:
                            logger.verifique(f"{i}")
                        else:
                            logger.info(f"{i}")

                    texto = f'FIM'
                    logger.info(f'{texto} {"#" * (barras - len(texto))}')
                    print("\n")
                    texto = f'Total: {len(pasta_com_cr)} | Analisadas: {idx} | {(idx / len(pasta_com_cr)) * 100:.2f}%'
                    logger.info(f'{texto} {"*" * (barras - len(texto))}')
                    print("\n")
        else:
            logger.error(f"Diretório {pasta_cr} não encontrado. Tente novamente.")
    
    elif numero == 3:
        logger.info("Saindo do programa...")
    logger.info("Análise Finalizada!")



