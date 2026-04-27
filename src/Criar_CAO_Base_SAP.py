import pandas as pd
import os
from tqdm import tqdm
from datetime import datetime
from src.function import *
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


def converter_nan(x):
    if pd.isna(x):  # cobre np.nan, None, pd.NaT, etc.
        return 0
    if isinstance(x, str):
        if x.strip().lower() in {"", "nan", "none", "null"}:
            return 0
    return str(x)


def Comp_SAP_vs_CAO(
    path_sap,
    path_cao,
    fam_sap=None,
    fam_cao=None,
    retirar_undeline_sap=False,
    retirar_undeline_cao=False,
    atualizar_dimensional=False,
):
    logger.info(
        f"Carregando o arquivo SAP: {os.path.basename(path_sap).replace('.xlsx', '')}"
    )
    with open(path_sap, "rb") as f:
        df1 = pd.read_excel(f)

    logger.info(
        f"Carregando o arquivo CAO: {os.path.basename(path_cao).replace('.csv', '')}"
    )
    with open(path_cao, "rb") as f:
        df2 = pd.read_csv(f, sep=";")
        df2 = df2.applymap(corrigir_valor)

    df1 = df1[
        (df1["Internal Family"] == fam_sap)
        & (pd.to_numeric(df1["SECTIONN"], errors="coerce") >= 0.35)
    ].reset_index(drop=True)

    df2 = df2[
        (df2["Leadset"].str.startswith(fam_cao, na=False))
        & (df2["ProdVersion"] == 0)
        & (~df2["Description"].str.contains("OBSOLETO", na=False))
    ].reset_index(drop=True)

    df1 = df1.sort_values(by=["WIRE_TUBE_SPLICE"]).reset_index(drop=True)
    df2 = df2.reset_index(drop=True).sort_values(by=["Wire1Key"])

    lista_ckt_diretos_add = []
    lista_ckt_tw_add = []

    df_comp = pd.DataFrame()

    linha_controle = 0

    leadset_SAP = df1["Leadset"].dropna().unique().tolist()

    for ckt in tqdm(leadset_SAP, desc="Processando 1", colour="blue"):
        ckt1 = ckt

        if retirar_undeline_sap:
            ckt1 = f"{ckt[:3]}{ckt[4:]}"

        if retirar_undeline_cao:
            if ckt[3] != "_":
                ckt1 = f"{ckt[:3]}_{ckt[3:]}"

        df_prov_sap = df1[df1["Leadset"] == ckt].reset_index(drop=True)
        df_prov_cao = df2[df2["Leadset"] == ckt1].reset_index(drop=True)

        # CABOS DIRETOS
        if len(df_prov_sap) == 1 and len(df_prov_cao) == 1:
            leadset_sap = df_prov_sap.loc[0, "Leadset"]
            cabo_sap = converter_nan(df_prov_sap.loc[0, "WIRE_TUBE_SPLICE"])
            comp_sap = int(df_prov_sap.loc[0, "LENGTH"])
            termA_sap = converter_nan(df_prov_sap.loc[0, "TERM_A"])
            termB_sap = converter_nan(df_prov_sap.loc[0, "TERM_B"])
            seloA_sap = converter_nan(df_prov_sap.loc[0, "SEAL_A"])
            seloB_sap = converter_nan(df_prov_sap.loc[0, "SEAL_B"])

            leadset_cao = df_prov_cao.loc[0, "Leadset"]
            cabo_cao = str(df_prov_cao.loc[0, "Wire1Key"])
            comp_cao = int(df_prov_cao.loc[0, "Wire1Length"])

            # Leitura
            termA_cao = converter_nan(df_prov_cao.loc[0, "Terminal1Key"])
            termB_cao = converter_nan(df_prov_cao.loc[0, "Terminal2Key"])
            seloA_cao = converter_nan(df_prov_cao.loc[0, "Seal1Key"])
            seloB_cao = converter_nan(df_prov_cao.loc[0, "Seal2Key"])

            # Boleta
            termA_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText1"])
            termB_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText2"])
            seloA_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText3"])
            seloB_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText4"])

            if cabo_sap == cabo_cao:
                pass
            else:
                df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                df_comp.loc[linha_controle, "Wire Atual"] = cabo_cao
                df_comp.loc[linha_controle, "Wire Novo"] = cabo_sap

            if comp_sap == comp_cao:
                pass
            else:
                df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                df_comp.loc[linha_controle, "Length Atual"] = comp_cao
                df_comp.loc[linha_controle, "Length Novo"] = comp_sap

            # APLICADO
            if (termA_sap == termA_cao and termB_sap == termB_cao) or (
                termA_sap == termB_cao and termB_sap == termA_cao
            ):
                pass
            else:
                if termA_sap != termA_cao and termB_sap == termB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term A Atual"] = termA_cao
                    df_comp.loc[linha_controle, "Term A Novo"] = termA_sap

                elif termA_sap == termA_cao and termB_sap != termB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term B Atual"] = termB_cao
                    df_comp.loc[linha_controle, "Term B Novo"] = termB_sap

            if (seloA_sap == seloA_cao and seloB_sap == seloB_cao) or (
                seloA_sap == seloB_cao and seloB_sap == seloA_cao
            ):
                pass
            else:
                if seloA_sap != seloA_cao and seloB_sap == seloB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo A Atual"] = seloA_cao
                    df_comp.loc[linha_controle, "Selo A Novo"] = seloA_sap

                elif seloA_sap == seloA_cao and seloB_sap != seloB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo B Atual"] = seloB_cao
                    df_comp.loc[linha_controle, "Selo B Novo"] = seloB_sap

            # BOLETA
            if (termA_sap == termA_cao_bol and termB_sap == termB_cao_bol) or (
                termA_sap == termB_cao_bol and termB_sap == termA_cao_bol
            ):
                pass
            else:
                if termA_sap != termA_cao_bol and termB_sap == termB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term A Atual [Boleta]"] = termA_cao_bol
                    df_comp.loc[linha_controle, "Term A Novo [Boleta]"] = termA_sap

                elif termA_sap == termA_cao_bol and termB_sap != termB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term B Atual [Boleta]"] = termB_cao_bol
                    df_comp.loc[linha_controle, "Term B Novo [Boleta]"] = termB_sap

            if (seloA_sap == seloA_cao_bol and seloB_sap == seloB_cao_bol) or (
                seloA_sap == seloB_cao_bol and seloB_sap == seloA_cao_bol
            ):
                pass
            else:
                if seloA_sap != seloA_cao_bol and seloB_sap == seloB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo A Atual [Boleta]"] = seloA_cao_bol
                    df_comp.loc[linha_controle, "Selo A Novo [Boleta]"] = seloA_sap

                elif seloA_sap == seloA_cao_bol and seloB_sap != seloB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo B Atual [Boleta]"] = seloB_cao_bol
                    df_comp.loc[linha_controle, "Selo B Novo [Boleta]"] = seloB_sap

            linha_controle += 1

        # CABOS TWISTERS
        elif len(df_prov_sap) == 2 and len(df_prov_cao) == 1:
            leadset_sap = df_prov_sap.loc[0, "Leadset"]
            cabo_sap1 = str(df_prov_sap.loc[0, "WIRE_TUBE_SPLICE"])
            cabo_sap2 = str(df_prov_sap.loc[1, "WIRE_TUBE_SPLICE"])
            comp_sap = int(df_prov_sap.loc[0, "Comp TW"])
            termA_sap = converter_nan(df_prov_sap.loc[0, "TERM_A"])
            termB_sap = converter_nan(df_prov_sap.loc[0, "TERM_B"])
            seloA_sap = converter_nan(df_prov_sap.loc[0, "SEAL_A"])
            seloB_sap = converter_nan(df_prov_sap.loc[0, "SEAL_B"])

            cabo_cao1 = converter_nan(df_prov_cao.loc[0, "Wire1Key"])
            cabo_cao2 = converter_nan(df_prov_cao.loc[0, "Wire2Key"])
            comp_cao = int(df_prov_cao.loc[0, "Wire1Length"])

            # Leitura
            leadset_cao = df_prov_cao.loc[0, "Leadset"]
            termA_cao = converter_nan(df_prov_cao.loc[0, "Terminal1Key"])
            termB_cao = converter_nan(df_prov_cao.loc[0, "Terminal2Key"])
            seloA_cao = converter_nan(df_prov_cao.loc[0, "Seal1Key"])
            seloB_cao = converter_nan(df_prov_cao.loc[0, "Seal2Key"])

            # Boleta
            termA_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText1"])
            termB_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText2"])
            seloA_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText3"])
            seloB_cao_bol = converter_nan(df_prov_cao.loc[0, "UserText4"])

            if (cabo_sap1 == cabo_cao1 and cabo_sap2 == cabo_cao2) or (
                cabo_sap1 == cabo_cao2 and cabo_sap2 == cabo_cao1
            ):
                pass
            else:
                if cabo_sap1 != cabo_cao1 and cabo_sap2 == cabo_cao2:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Wire Atual"] = cabo_cao1
                    df_comp.loc[linha_controle, "Wire Novo"] = cabo_sap1
                elif cabo_sap1 == cabo_cao1 and cabo_sap2 != cabo_cao2:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Wire2 Atual"] = cabo_cao2
                    df_comp.loc[linha_controle, "Wire2 Novo"] = cabo_sap2
                else:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Wire Atual"] = cabo_cao1
                    df_comp.loc[linha_controle, "Wire Novo"] = cabo_sap1
                    df_comp.loc[linha_controle, "Wire2 Atual"] = cabo_cao2
                    df_comp.loc[linha_controle, "Wire2 Novo"] = cabo_sap2

            if comp_sap == comp_cao:
                pass
            else:
                df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                df_comp.loc[linha_controle, "Length TW Atual"] = comp_cao
                df_comp.loc[linha_controle, "Length TW Novo"] = comp_sap

            # APLICADO
            if (termA_sap == termA_cao and termB_sap == termB_cao) or (
                termA_sap == termB_cao and termB_sap == termA_cao
            ):
                pass
            else:
                if termA_sap != termA_cao and termB_sap == termB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term A Atual"] = termA_cao
                    df_comp.loc[linha_controle, "Term A Novo"] = termA_sap

                elif termA_sap == termA_cao and termB_sap != termB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term B Atual"] = termB_cao
                    df_comp.loc[linha_controle, "Term B Novo"] = termB_sap

            if (seloA_sap == seloA_cao and seloB_sap == seloB_cao) or (
                seloA_sap == seloB_cao and seloB_sap == seloA_cao
            ):
                pass
            else:
                if seloA_sap != seloA_cao and seloB_sap == seloB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo A Atual"] = seloA_cao
                    df_comp.loc[linha_controle, "Selo A Novo"] = seloA_sap

                elif seloA_sap == seloA_cao and seloB_sap != seloB_cao:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo B Atual"] = seloB_cao
                    df_comp.loc[linha_controle, "Selo B Novo"] = seloB_sap

            # BOLETA
            if (termA_sap == termA_cao_bol and termB_sap == termB_cao_bol) or (
                termA_sap == termB_cao_bol and termB_sap == termA_cao_bol
            ):
                pass
            else:
                if termA_sap != termA_cao_bol and termB_sap == termB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term A Atual [Boleta]"] = termA_cao_bol
                    df_comp.loc[linha_controle, "Term A Novo [Boleta]"] = termA_sap

                elif termA_sap == termA_cao_bol and termB_sap != termB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Term B Atual [Boleta]"] = termB_cao_bol
                    df_comp.loc[linha_controle, "Term B Novo [Boleta]"] = termB_sap

            if (seloA_sap == seloA_cao_bol and seloB_sap == seloB_cao_bol) or (
                seloA_sap == seloB_cao_bol and seloB_sap == seloA_cao_bol
            ):
                pass
            else:
                if seloA_sap != seloA_cao_bol and seloB_sap == seloB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo A Atual [Boleta]"] = seloA_cao_bol
                    df_comp.loc[linha_controle, "Selo A Novo [Boleta]"] = seloA_sap

                elif seloA_sap == seloA_cao_bol and seloB_sap != seloB_cao_bol:
                    df_comp.loc[linha_controle, "Leadset Atual"] = leadset_cao
                    df_comp.loc[linha_controle, "Leadset Novo"] = leadset_sap
                    df_comp.loc[linha_controle, "Selo B Atual [Boleta]"] = seloB_cao_bol
                    df_comp.loc[linha_controle, "Selo B Novo [Boleta]"] = seloB_sap

            linha_controle += 1

        elif len(df_prov_sap) == 1 and len(df_prov_cao) == 0:
            lista_ckt_diretos_add.append(ckt)

        elif len(df_prov_sap) == 2 and len(df_prov_cao) == 0:
            lista_ckt_tw_add.append(ckt)

    colunas_ord = [
        "Leadset Atual",
        "Leadset Novo",
        "Wire Atual",
        "Wire Novo",
        "Wire2 Atual",
        "Wire2 Novo",
        "Length Atual",
        "Length Novo",
        "Length TW Atual",
        "Length TW Novo",
        "Term A Atual",
        "Term A Novo",
        "Term B Atual",
        "Term B Novo",
        "Selo A Atual",
        "Selo A Novo",
        "Selo B Atual",
        "Selo B Novo",
        "Term A Atual [Boleta]",
        "Term A Novo [Boleta]",
        "Term B Atual [Boleta]",
        "Term B Novo [Boleta]",
        "Selo A Atual [Boleta]",
        "Selo A Novo [Boleta]",
        "Selo B Atual [Boleta]",
        "Selo B Novo [Boleta]",
    ]
    df_comp = reordenar_colunas(df_comp, colunas_ord)

    df_comp = df_comp.reset_index(drop=True)

    dict_comp = {}
    dict_comp1 = {}
    if "Length Novo" in df_comp.columns:
        dict_comp = {
            row["Leadset Novo"]: int(row["Length Novo"])
            for i, row in df_comp.dropna(subset=["Length Novo"]).iterrows()
        }

    if "Length TW Novo" in df_comp.columns:
        dict_comp1 = {
            row["Leadset Novo"]: int(row["Length TW Novo"])
            for i, row in df_comp.dropna(subset=["Length TW Novo"]).iterrows()
        }

    if dict_comp and dict_comp1:
        dict_comp.update(dict_comp1)

    elif dict_comp1:
        dict_comp = dict_comp1

    # ATUALIZANDO CAO
    new_df_cao = df2[df2["Leadset"].str.startswith("G", na=False)].copy()

    for i in tqdm(new_df_cao.index, desc="Processando 2", colour="blue"):
        leadset = new_df_cao.loc[i, "Leadset"]

        if retirar_undeline_sap:
            if leadset[3] != "_":
                leadset = f"{leadset[:3]}_{leadset[3:]}"

        if retirar_undeline_cao:
            leadset = f"{leadset[:3]}{leadset[4:]}"

        if leadset[:1] == fam_cao[:1]:
            new_df_cao.loc[i, "Leadset"] = leadset

            if len(leadset) >= 4 and leadset[3] == "_" and leadset[4] == "_":
                new_df_cao.loc[i, "UserWSText7"] = f"{leadset[:3]}-{leadset[5:]}"
            elif len(leadset) >= 4 and leadset[3] == "_":
                new_df_cao.loc[i, "UserWSText7"] = f"{leadset[:3]}-{leadset[4:]}"
            else:
                new_df_cao.loc[i, "UserWSText7"] = f"{leadset[:3]}-{leadset[4:]}"

            if dict_comp and atualizar_dimensional:
                new_df_cao.loc[i, "Wire1Length"] = dict_comp.get(
                    new_df_cao.loc[i, "Leadset"], new_df_cao.loc[i, "Wire1Length"]
                )

                new_df_cao.loc[i, "Wire2Length"] = dict_comp.get(
                    new_df_cao.loc[i, "Leadset"], new_df_cao.loc[i, "Wire2Length"]
                )

                new_df_cao.loc[i, "TwistWireLength"] = dict_comp.get(
                    new_df_cao.loc[i, "Leadset"], new_df_cao.loc[i, "TwistWireLength"]
                )

    ckt_add = pd.DataFrame(
        lista_ckt_diretos_add + lista_ckt_tw_add, columns=["Leadset"]
    )

    ckt_add["Status"] = "Adicionar"

    return df_comp, ckt_add, new_df_cao


def comparar_fam_sap_cao():
    os.system("cls")

    logo("Atualizar CAO")

    logger.info("Entre com o caminho do arquivo SAP")
    caminho_sap = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo CAO [Master Data]")
    caminho_cao = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    logger.info("Entre o código UCS para Filtrar o SAP")
    famSap = input("[>] ").replace(" ", "").upper()

    logger.info("Entre o código UCS para Filtrar o CAO")
    famCao = input("[>] ").replace(" ", "").upper()

    logger.info("Deseja remover o underline do SAP? [S/N]")
    while True:
        resposta = input("[>] ").strip().lower()

        if resposta in ["s", "y", "sim", "yes"]:
            remover_underline_sap = True
            break
        elif resposta in ["n", "nao", "não", "no"]:
            remover_underline_sap = False
            break
        else:
            logger.atencao("Entrada inválida. Por favor, responda com S ou N.")

    logger.info("Deseja remover o underline do CAO? [S/N]")
    while True:
        resposta = input("[>] ").strip().lower()
        if resposta in ["s", "y", "sim", "yes"]:
            retirar_undeline_cao = True
            break
        elif resposta in ["n", "nao", "não", "no"]:
            retirar_undeline_cao = False
            break
        else:
            logger.atencao("Entrada inválida. Por favor, responda com S ou N.")

    logger.info("Atualizar dimensional do CAO? [S/N]")
    while True:
        resposta = input("[>] ").strip().lower()
        if resposta in ["s", "y", "sim", "yes"]:
            atualizar_dimensional = True
            break
        elif resposta in ["n", "nao", "não", "no"]:
            atualizar_dimensional = False
            break
        else:
            logger.atencao("Entrada inválida. Por favor, responda com S ou N.")

    dict_consolidado = {}

    df_prov, add_ckt, df_new_cao = Comp_SAP_vs_CAO(
        caminho_sap,
        caminho_cao,
        fam_sap=famSap,
        fam_cao=famCao,
        retirar_undeline_sap=remover_underline_sap,
        retirar_undeline_cao=retirar_undeline_cao,
        atualizar_dimensional=atualizar_dimensional,
    )

    dict_consolidado["Análise"] = df_prov
    dict_consolidado["Add Circuitos"] = add_ckt
    dict_consolidado["Cadastro CAO"] = df_new_cao

    data_atual = datetime.now().strftime("%Y_%m_%d")

    salvar_dict_df_em_excel(
        dict_consolidado, f"{caminho_output}\{famSap}_Análise_CAO_{data_atual}.xlsx"
    )

    df_new_cao.to_csv(
        f"{caminho_output}\{famSap}_Cadastro_CAO_{data_atual}.csv", sep=";", index=False
    )
    df_new_cao.dropna(how="all", axis=1).to_excel(
        f"{caminho_output}\{famSap}_Cadastro_CAO_{data_atual}.xlsx", index=False
    )
