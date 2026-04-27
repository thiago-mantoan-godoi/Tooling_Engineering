import pandas as pd
import sys
import os
import warnings
from datetime import datetime

warnings.simplefilter("ignore")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_PATH = os.path.join(BASE_DIR, "src")

if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from function import *


def padronizar_lista_corte(dados: pd.DataFrame):
    # Colunas principais
    colunas_cor = [
        "Nome do arquivo",
        "Fase",
        "ProcessoA",
        "ProcessoB",
        "UCS",
        "Leadset",
        "Wire Nb",
        "Multicore",
        "T",
        "CSA",
        "Length",
        "C1",
        "C2",
        "Int.PN",
        "Term. 1",
        "Strip 1",
        "Seal 1",
        "Node 1",
        "T_1",
        "Joint 1",
        "Note 1",
        "Term. 2",
        "Strip 2",
        "Seal 2",
        "Node 2",
        "T_2",
        "Joint 2",
        "Note 2",
    ]
    colunas_cor = list(dict.fromkeys(colunas_cor))  # remove duplicatas

    # Reordena colunas principais
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_cor)

    # Renomeia colunas ProcessoA/B
    dados.rename(
        columns={"ProcessoA": "C.Process1", "ProcessoB": "C.Process2"}, inplace=True
    )

    # Colunas corte
    colunas_corte = [
        "##0",
        "C.TypeCkt",
        "C.AttrSafety",
        "C.Wire #Strands",
        "C.Process1",
        "C.Seal1Use",
        "C.T1Type",
        "C.T1Method",
        "C.T1Feeding",
        "C.Process2",
        "C.Seal2Use",
        "C.T2Type",
        "C.T2Method",
        "C.T2Feeding",
        "##1",
        "C.Vol/day_LCR",
        "C.Vol/day_MCR",
        "C.DoH_days",
        "C.Diversity",
        "C.Vol/Lot",
        "##2",
        "C.Bundlesize",
        "C.Bundlecount",
        "C.Time_Batch(h)",
        "C.Elastic",
        "C.ProtectCup",
        "C.Hangers",
        "C.Rack Aloc",
        "##3",
        "C.CrossSection",
        "C.InkJet",
        "C.VisionSystem",
        "C.MiddleStrip",
        "C.Micrograph",
        "C.CktType",
        "C.CktsCount",
        "C.Process",
        "C.Lclass",
        "##4",
        "C.Mch_Name",
        "C.Mch_Type",
        "C.ID_Mch",
        "C.Rate(pc/h)",
        "C.RunningT(h)",
        "C.SetupT(h)",
        "C.WorkTime(h)",
        "C.WorkTime_MCR(h)",
        "C.ConveyorLength",
        "##5",
        "C.PressTypeA",
        "C.ApplicatorA",
        "C.PressADoH",
        "C.PressDiversA",
        "C.PressVol/LotA",
        "C.PressRateA",
        "C.PressRunningTA",
        "C.PressRunningTA_MCR",
        "C.PressSetupA",
        "C.PressWorkTimeA",
        "##6",
        "C.PressTypeB",
        "C.ApplicatorB",
        "C.PressBDoH",
        "C.PressDiversB",
        "C.PressVol/LotB",
        "C.PressRateB",
        "C.PressRunningTB",
        "C.PressRunningTB_MCR",
        "C.PressSetupB",
        "C.PressWorkTimeB",
    ]
    colunas_corte = list(dict.fromkeys(colunas_corte))  # remove duplicatas

    # Cria colunas faltantes
    for coluna in colunas_corte + ["Nome do arquivo", "Fase", "UCS", "Leadset"]:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Ordem final
    colunas_ord = ['Nome do arquivo','Fase','UCS','Leadset',
                   '##0','C.TypeCkt','C.AttrSafety','C.Wire #Strands','C.T1Type','C.T1Method','C.T1Feeding','C.T2Type','C.T2Method','C.T2Feeding',
                   '##1','C.Vol/day_LCR','C.Vol/day_MCR','C.DoH_days','C.Diversity','C.Vol/Lot',
                   '##2','C.Bundlesize','C.Bundlecount','C.Time_Batch(h)','C.Elastic','C.ProtectCup','C.Hangers','C.Rack Aloc',
                   '##3','C.CrossSection','C.InkJet','C.VisionSystem','C.MiddleStrip','C.Micrograph','C.CktType','C.CktsCount','C.Process','C.Lclass',
                   '##4','C.Mch_Name','C.Mch_Type','C.ID_Mch','C.Rate(pc/h)','C.RunningT(h)','C.SetupT(h)','C.WorkTime(h)','C.WorkTime_MCR(h)','C.ConveyorLength',
                   '##5','C.PressTypeA','C.ApplicatorA','C.PressADoH','C.PressDiversA','C.PressVol/LotA','C.PressRateA','C.PressRunningTA','C.PressRunningTA_MCR','C.PressSetupA','C.PressWorkTimeA',
                   '##6','C.PressTypeB','C.ApplicatorB','C.PressBDoH','C.PressDiversB','C.PressVol/LotB','C.PressRateB','C.PressRunningTB','C.PressRunningTB_MCR','C.PressSetupB','C.PressWorkTimeB',
                   'Wire Nb','Multicore','T','CSA','Length','C1','C2','Int.PN','Term. 1','C.Process1','C.Seal1Use','Strip 1','Seal 1','Node 1','T_1','Joint 1','Note 1','Term. 2','C.Process2','C.Seal2Use',
                   'Strip 2','Seal 2','Node 2','T_2','Joint 2','Note 2']

    # Reordena colunas
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_ord)

    return dados


def padronizar_lista_splice(dados: pd.DataFrame):
    # Colunas a remover
    colunas_remove = [
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
        "USCAR_45",
        "GMW17136",
        "count_left_1",
        "count_left_0.5",
        "count_right_0.5",
        "count_right_1.5",
        "count_left_1.0",
        "count_right_1.0",
        "L11",
        "R11",
        "L12",
        "R12",
        "L13",
        "R13",
        "L14",
        "R14",
        "L15",
        "R15",
        "L16",
        "R16",
        "L17",
        "R17",
        "L18",
        "R18",
        "L19",
        "R19",
        "L20",
        "R20",
        "L21",
        "R21",
        "L22",
        "R22",
        "L23",
        "R23",
        "L24",
        "R24",
    ]
    dados.drop(columns=colunas_remove, inplace=True, errors="ignore")

    # Colunas Splice
    colunas_splice = [
        "##0",
        "SP.Vol/Day_LCR",
        "SP.Vol/Day_MCR",
        "SP.DoH",
        "SP.Diversity",
        "SP.Vol/Lot",
        "##1",
        "SP.Ckt_Count_Right",
        "SP.Ckt_Count_Left",
        "SP.Ckt_Count",
        "SP.Config",
        "SP.CSA_SUM",
        "SP.Technology",
        "7x1 Machine",
        "SP.Mch",
        "SP.Rate",
        "SP.Trun_MCR",
        "SP.Trun_LCR",
        "SP.SetupT",
        "Sp.WorkTime",
        "SP.Attr.Safatey",
        "SP.Attr.Twister",
        "##2",
        "SP.Bundle",
        "SP.Bundle_Count",
        "SP.Hanglers",
        "SP.Alocacions",
        "##3",
        "SP.CoverType",
        "SP.Cover",
        "SP.Cover.Rate",
        "SP.Cover.Trun",
        "SP.Cover.TrunMCR",
        "SP.Cover.Setup",
        "SP.Cover.Worktime",
        "##4",
        "SP.BubbleTest",
        "SP.BubbleTest.Freq",
        "SP.BubbleTest.Rate",
        "SP.BubbleTest.Vol",
        "SP.BubbleTest.RunningT",
        "SP.BubbleTest.Setup",
        "SP.BubbleTest.WorkTime",
        "##5",
    ]
    colunas_splice = list(dict.fromkeys(colunas_splice))  # remove duplicatas

    # Colunas prioritárias
    colunas_ord = [
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
        "X1",
        "Node",
        "Note",
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
    ] + colunas_splice
    colunas_ord = list(dict.fromkeys(colunas_ord))  # remove duplicatas

    # Cria todas as colunas faltantes
    for coluna in colunas_ord:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Reordena colunas
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_ord)

    return dados


def padronizar_lista_twister(dados: pd.DataFrame):
    # Colunas a remover
    colunas_remove = [
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
    dados.drop(columns=colunas_remove, inplace=True, errors="ignore")

    # Colunas Twister
    colunas_twister = [
        "##0",
        "TW.Vol/day",
        "TW.Vol/day MCR",
        "TW.Estoque",
        "TW.Vol/lote",
        "TW.Tipos",
        "##1",
        "TW.Bundle Size",
        "TW.Qnt Bundle",
        "TW.Hanglers",
        "TW.BatchTime",
        "TW.Locations",
        "##2",
        "TW.Corte",
        "TW.Processo",
        "TW.Pernas",
        "TW.Lcalss",
        "TW.Machine_Length",
        "TW.Maquina",
        "TW.Maquina ID",
        "TW.Maquina Process",
        "TW.Rate",
        "TW.RunningT(h)",
        "TW.RunningT(h)_MCR",
        "TW.Setup(h)",
        "TW.WorkTime(h)",
        "TW.Baumuster Certifc",
        "##3",
        "TW.Hipot Rate",
        "TW.Hipot",
        "##4",
        "TW.SpotTape",
        "TW.RateSpotTape",
        "TW.STWorkTime(h)",
        "##5",
        "TW.OndalTape",
        "TW.Ondal",
        "##6",
    ]
    colunas_twister = list(dict.fromkeys(colunas_twister))  # remove duplicatas

    # Colunas prioritárias (ordem desejada)
    colunas_ord = [
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
        "W3",
        "W4",
        "W5",
    ] + colunas_twister
    colunas_ord = list(dict.fromkeys(colunas_ord))  # remove duplicatas

    # Cria todas as colunas faltantes antes de reordenar
    for coluna in colunas_ord:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Reordena colunas
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_ord)

    return dados


def padronizar_lista_tubos(dados: pd.DataFrame):
    colunas_tubos = [
        "##0",
        "TU.Vol/day",
        "TU.Vol/day_MCR",
        "TU.DoH",
        "TU.Vol/Lot",
        "TU.Diversity",
        "##1",
        "TU.LClass",
        "TU.Process",
        "TU.Mch",
        "TU.Mch_ID",
        "TU.Rate",
        "TU.Trun",
        "TU.Setup",
        "TU.Ttotal",
        "TU.Ttotal_MCR",
        "TU.IDTube",
        "TU.Box",
        "##2",
    ]
    colunas_tubos = list(dict.fromkeys(colunas_tubos))  # remove duplicatas

    # Colunas prioritárias (ordem desejada)
    colunas_ord = [
        "Nome do arquivo",
        "Fase",
        "UCS",
        "Sleeve Nb",
        "Int.PN",
        "Length",
        "key",
        "Type",
        "Pack",
        "Description",
        "Mater.",
        "Type_1",
        "Width",
        "Group",
        "Color",
        "Slit",
        "Conv",
        "Wall Th.",
        "Layer",
        "Node 1",
        "Node 2",
        "Item",
    ] + colunas_tubos
    colunas_ord = list(dict.fromkeys(colunas_ord))  # remove duplicatas

    # Cria todas as colunas faltantes antes de reordenar
    for coluna in colunas_ord:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Reordena colunas
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_ord)

    return dados


def padronizar_lista_mult(dados: pd.DataFrame):
    # Colunas múltiplas
    colunas_mult = [
        "##0",
        "MC.Vol",
        "MC.Vol/day_MCR",
        "MC.DoH",
        "MC.Vol/Lot",
        "MC.Tipos",
        "MC.Type",
        "C.Feeding",
        "##1",
        "MC.Machine",
        "MC.Process",
        "MC.Rate",
        "MC.Trun",
        "MC.Setup",
        "MC.Total",
        "MC.",
        "##2",
        "MC.HS",
        "MC.HS.Rate",
        "MC.HS.Vol_Day",
        "MC.HS.Trun",
        "MC.HS.Setup",
        "MC.HS.WorkTime",
        "MC.HS.BubbleTest.Rate",
        "MC.HS.BubbleTest.Time",
        "##3",
        "MC.Bundle",
        "MC.Bundle_Count",
        "MC.Hanglers",
        "MC.Alocacions",
        "MC.Certification.Type",
        "MC.Certifications",
        "##4",
        "MC.BubbleTest",
        "MC.BubbleTest.Freq",
        "MC.BubbleTest.Rate",
        "MC.BubbleTest.Vol",
        "MC.BubbleTest.RunningT",
        "MC.BubbleTest.Setup",
        "MC.BubbleTest.WorkTime",
        "##5",
        "MC.Splice1",
        "MC.Splice2",
        "MC.Splice3",
        "MC.Splice5",
        "MC.W1",
        "MC.W2",
        "MC.W3",
        "MC.W4",
        "MC.W5",
        "MC.W6",
        "MC.W7",
        "MC.W8",
        "MC.W9",
        "MC.W10",
        "MC.W11",
        "MC.W12",
        "MC.W13",
        "MC.W14",
        "MC.W15",
    ]

    # Remove duplicatas mantendo a ordem
    colunas_mult = list(dict.fromkeys(colunas_mult))

    # Cria colunas faltantes com None
    for coluna in colunas_mult:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Colunas prioritárias (ordem desejada)
    colunas_ord = [
        "Nome do arquivo",
        "Fase",
        "UCS",
        "MC.Terminal",
        "MC.Type",
        "C.Feeding",
        "Note 2",
        "MC.Splice1",
        "MC.Splice2",
        "MC.Splice3",
        "MC.Splice5",
        "MC.Splice6",
        "MC.Splice7",
        "MC.Splice8",
        "MC.Splice9",
        "MC.Splice10",
        "MC.W1",
        "MC.W2",
        "MC.W3",
        "MC.W4",
        "MC.W5",
        "MC.W6",
        "MC.W7",
        "MC.W8",
        "MC.W9",
        "MC.W10",
        "MC.W11",
        "MC.W12",
        "MC.W13",
        "MC.W14",
        "MC.W15",
        "MC.W16",
        "MC.W17",
        "MC.W18",
        "MC.W19",
        "MC.W20",
    ] + colunas_mult

    # Remove duplicatas da lista final
    colunas_ord = list(dict.fromkeys(colunas_ord))

    # Cria colunas faltantes antes de reordenar
    for coluna in colunas_ord:
        if coluna not in dados.columns:
            dados[coluna] = None

    # Reordena as colunas
    dados = reordenar_colunas(dados, colunas_prioritarias=colunas_ord)

    return dados


def add_BOM_wire(df_base: pd.DataFrame):
    with open(consultar_arquivos_base("terminais_sem"), "rb") as f:
        df_term = pd.read_excel(f)

    dict_Delivery = {
        row["Part Number"]: row["Feed Type/Delivery Form"]
        for i, row in df_term.iterrows()
    }
    dict_Technology = {
        row["Part Number"]: row["Connection Technology"]
        for i, row in df_term.iterrows()
    }

    df_base["C.T1Method"] = df_base["Term. 1"].map(dict_Technology)
    df_base["C.T2Method"] = df_base["Term. 2"].map(dict_Technology)

    df_base["C.T1Feeding"] = df_base["Term. 1"].map(dict_Delivery)
    df_base["C.T2Feeding"] = df_base["Term. 2"].map(dict_Delivery)

    return df_base


def add_BOM_mult(df_base: pd.DataFrame):
    with open(consultar_arquivos_base("terminais_sem"), "rb") as f:
        df_term = pd.read_excel(f)

    dict_Delivery = {
        row["Part Number"]: row["Feed Type/Delivery Form"]
        for i, row in df_term.iterrows()
    }
    dict_Technology = {
        row["Part Number"]: row["Connection Technology"]
        for i, row in df_term.iterrows()
    }

    df_base["MC.Type"] = df_base["MC.Terminal"].map(dict_Technology)
    df_base["C.Feeding"] = df_base["MC.Terminal"].map(dict_Delivery)

    return df_base


logger = LoggerTerminal(salvar_log=False, typing=True)


def gerar_base_para_c5():
    os.system("cls")

    logo("Gerar Base para C5")

    logger.info("Entre com o caminho do arquivo [Arquivo gerado do item 1]")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    dict_df = {
        "Wire_Nb": None,
        "Splice_Nb": None,
        "MultWire_Nb": None,
        "Sleeve_Nb": None,
        "Multcrimp_Nb": None,
    }

    # Abre o Excel usando 'with' para garantir que seja fechado corretamente
    with pd.ExcelFile(caminho_base) as df_base:
        lista_corte = pd.read_excel(df_base, sheet_name="Wire_Nb")
        dict_df["Wire_Nb"] = padronizar_lista_corte(lista_corte)
        dict_df["Wire_Nb"] = add_BOM_wire(dict_df["Wire_Nb"])
        logger.sucesso(
            f"Wire_Nb carregado: {len(dict_df['Wire_Nb'])} linhas processadas."
        )

        lista_splice = pd.read_excel(df_base, sheet_name="Splice_Nb")
        dict_df["Splice_Nb"] = padronizar_lista_splice(lista_splice)
        logger.sucesso(
            f"Splice_Nb carregado: {len(dict_df['Splice_Nb'])} linhas processadas."
        )

        lista_twister = pd.read_excel(df_base, sheet_name="MultWire_Nb")
        dict_df["MultWire_Nb"] = padronizar_lista_twister(lista_twister)
        logger.sucesso(
            f"MultWire_Nb carregado: {len(dict_df['MultWire_Nb'])} linhas processadas."
        )

        lista_tubos = pd.read_excel(df_base, sheet_name="Sleeve_Nb")
        dict_df["Sleeve_Nb"] = padronizar_lista_tubos(lista_tubos)
        logger.sucesso(
            f"Sleeve_Nb carregado: {len(dict_df['Sleeve_Nb'])} linhas processadas."
        )

        lista_Multcrimp = pd.read_excel(df_base, sheet_name="Multcrimp_Nb - Estudo")
        dict_df["Multcrimp_Nb"] = padronizar_lista_mult(lista_Multcrimp)
        dict_df["Multcrimp_Nb"] = add_BOM_mult(dict_df["Multcrimp_Nb"])
        logger.sucesso(
            f"Multcrimp_Nb carregado: {len(dict_df['Multcrimp_Nb'])} linhas processadas."
        )

    data_atual = datetime.now().strftime("%d-%m-%Y")
    salvar_dict_df_em_excel(dict_df, f"{caminho_output}/Base_C5_{data_atual}.xlsx")

    logger.info("Arquivo Salvo!")
