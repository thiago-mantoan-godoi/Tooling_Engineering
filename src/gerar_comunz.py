import pandas as pd
from tqdm import tqdm
from datetime import datetime

import sys
import os

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.function import *
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


def gerar_comunization(path_sap, path_comz):
    with open(path_sap, "rb") as f:
        dados = pd.read_excel(f)

    with open(path_comz, "rb") as f:
        df_cmz_sap = pd.read_csv(f, sep=";")

    list_ckt = df_cmz_sap["CIRC_MASTER"].unique().tolist()

    # df_cmz_prov = df_cmz_sap[df_cmz_sap['CIRC_MASTER'] != df_cmz_sap['CIRC_COMUNS']].reset_index(drop=True)

    dict_comuns = {
        row["CIRC_COMUNS"]: "Esta comunizado!" for i, row in df_cmz_sap.iterrows()
    }

    dados["CIRC_MASTER"] = None
    dados["CIRC_COMUNS"] = None
    dados["STATUS"] = None

    dados = dados.sort_values(by=["Internal Family"]).reset_index(drop=True)

    tolerancia = 0

    for c in tqdm(list_ckt, desc="1. Processando", colour="Blue"):
        for i in dados.index:
            leadset = str(dados.at[i, "Internal Family"]) + str(dados.at[i, "CIRCUIT"])
            if leadset == c:
                if pd.isna(dados.at[i, "CIRC_MASTER"]):
                    fam_base = str(dados.at[i, "Internal Family"])[:1]
                    cor_base = str(dados.at[i, "COLOR1"]) + str(dados.at[i, "COLOR2"])
                    cabo_base = dados.at[i, "WIRE_TUBE_SPLICE"]
                    comp_base = dados.at[i, "LENGTH"]
                    termA_base = (
                        "" if pd.isna(dados.at[i, "TERM_A"]) else dados.at[i, "TERM_A"]
                    )
                    termB_base = (
                        "" if pd.isna(dados.at[i, "TERM_B"]) else dados.at[i, "TERM_B"]
                    )
                    seloA_base = (
                        "" if pd.isna(dados.at[i, "SEAL_A"]) else dados.at[i, "SEAL_A"]
                    )
                    seloB_base = (
                        "" if pd.isna(dados.at[i, "SEAL_B"]) else dados.at[i, "SEAL_B"]
                    )
                    stripA_base = (
                        ""
                        if pd.isna(dados.at[i, "STRIP_A"])
                        else dados.at[i, "STRIP_A"]
                    )
                    stripB_base = (
                        ""
                        if pd.isna(dados.at[i, "STRIP_B"])
                        else dados.at[i, "STRIP_B"]
                    )

                    for j in range(dados.shape[0]):
                        if i != j:
                            if pd.isna(dados.at[j, "CIRC_MASTER"]):
                                cor_comp = str(dados.at[j, "COLOR1"]) + str(
                                    dados.at[j, "COLOR2"]
                                )
                                fam_comp = str(dados.at[j, "Internal Family"])[:1]
                                cabo_comp = dados.at[j, "WIRE_TUBE_SPLICE"]
                                comp_comp = dados.at[j, "LENGTH"]
                                termA_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "TERM_A"])
                                    else dados.at[j, "TERM_A"]
                                )
                                termB_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "TERM_B"])
                                    else dados.at[j, "TERM_B"]
                                )
                                seloA_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "SEAL_A"])
                                    else dados.at[j, "SEAL_A"]
                                )
                                seloB_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "SEAL_B"])
                                    else dados.at[j, "SEAL_B"]
                                )
                                stripA_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "STRIP_A"])
                                    else dados.at[j, "STRIP_A"]
                                )
                                stripB_comp = (
                                    ""
                                    if pd.isna(dados.at[j, "STRIP_B"])
                                    else dados.at[j, "STRIP_B"]
                                )

                                if (
                                    fam_base == fam_comp
                                    and cabo_base == cabo_comp
                                    and cor_base == cor_comp
                                ):
                                    comp_base - comp_comp
                                    if abs(comp_base - comp_comp) <= tolerancia:
                                        if (
                                            (
                                                (
                                                    termA_base == termA_comp
                                                    and termB_base == termB_comp
                                                )
                                                or (
                                                    termA_base == termB_comp
                                                    and termB_base == termA_comp
                                                )
                                            )
                                            and (
                                                (
                                                    seloA_base == seloA_comp
                                                    and seloB_base == seloB_comp
                                                )
                                                or (
                                                    seloA_base == seloB_comp
                                                    and seloB_base == seloA_comp
                                                )
                                            )
                                            and (
                                                (
                                                    stripA_base == stripA_comp
                                                    and stripB_base == stripB_comp
                                                )
                                                or (
                                                    stripA_base == stripB_comp
                                                    and stripB_base == stripA_comp
                                                )
                                            )
                                        ):
                                            dados.at[i, "STATUS"] = "1"
                                            dados.at[j, "STATUS"] = "1"
                                            if "TW" in dados.at[i, "Leadset"]:
                                                dados.at[i, "CIRC_MASTER"] = str(
                                                    dados.at[i, "Internal Family"]
                                                ) + str(dados.at[i, "CIRCUIT"])
                                                dados.at[i, "CIRC_COMUNS"] = str(
                                                    dados.at[i, "Internal Family"]
                                                ) + str(dados.at[i, "CIRCUIT"])
                                                dados.at[j, "CIRC_MASTER"] = str(
                                                    dados.at[i, "Internal Family"]
                                                ) + str(dados.at[i, "CIRCUIT"])
                                                dados.at[j, "CIRC_COMUNS"] = str(
                                                    dados.at[j, "Internal Family"]
                                                ) + str(dados.at[j, "CIRCUIT"])

                                                dados.at[i, "STATUS"] = dict_comuns.get(
                                                    dados.at[i, "CIRC_COMUNS"], "Novo 1"
                                                )
                                                dados.at[j, "STATUS"] = dict_comuns.get(
                                                    dados.at[j, "CIRC_COMUNS"], "Novo 1"
                                                )

                                            else:
                                                dados.at[i, "CIRC_MASTER"] = dados.at[
                                                    i, "Leadset"
                                                ]
                                                dados.at[i, "CIRC_COMUNS"] = dados.at[
                                                    i, "Leadset"
                                                ]
                                                dados.at[j, "CIRC_MASTER"] = dados.at[
                                                    i, "Leadset"
                                                ]
                                                dados.at[j, "CIRC_COMUNS"] = dados.at[
                                                    j, "Leadset"
                                                ]

                                                dados.at[i, "STATUS"] = dict_comuns.get(
                                                    dados.at[i, "CIRC_COMUNS"], "Novo 1"
                                                )
                                                dados.at[j, "STATUS"] = dict_comuns.get(
                                                    dados.at[j, "CIRC_COMUNS"], "Novo 1"
                                                )

    for i in tqdm(dados.index, desc="2. Processando", colour="Blue"):
        if pd.isna(dados.at[i, "CIRC_MASTER"]):
            cor_base = str(dados.at[i, "COLOR1"]) + str(dados.at[i, "COLOR2"])
            ckt_base = str(dados.at[i, "Leadset"])
            fam_base = str(dados.at[i, "Internal Family"])[:1]
            cabo_base = dados.at[i, "WIRE_TUBE_SPLICE"]
            comp_base = dados.at[i, "LENGTH"]
            termA_base = "" if pd.isna(dados.at[i, "TERM_A"]) else dados.at[i, "TERM_A"]
            termB_base = "" if pd.isna(dados.at[i, "TERM_B"]) else dados.at[i, "TERM_B"]
            seloA_base = "" if pd.isna(dados.at[i, "SEAL_A"]) else dados.at[i, "SEAL_A"]
            seloB_base = "" if pd.isna(dados.at[i, "SEAL_B"]) else dados.at[i, "SEAL_B"]

            for j in range(i + 1, dados.shape[0]):
                if i != j:
                    if pd.isna(dados.at[j, "CIRC_MASTER"]):
                        cor_comp = str(dados.at[j, "COLOR1"]) + str(
                            dados.at[j, "COLOR2"]
                        )
                        ckt_comp = str(dados.at[j, "Leadset"])
                        fam_comp = str(dados.at[j, "Internal Family"])[:1]
                        cabo_comp = dados.at[j, "WIRE_TUBE_SPLICE"]
                        comp_comp = dados.at[j, "LENGTH"]
                        termA_comp = (
                            ""
                            if pd.isna(dados.at[j, "TERM_A"])
                            else dados.at[j, "TERM_A"]
                        )
                        termB_comp = (
                            ""
                            if pd.isna(dados.at[j, "TERM_B"])
                            else dados.at[j, "TERM_B"]
                        )
                        seloA_comp = (
                            ""
                            if pd.isna(dados.at[j, "SEAL_A"])
                            else dados.at[j, "SEAL_A"]
                        )
                        seloB_comp = (
                            ""
                            if pd.isna(dados.at[j, "SEAL_B"])
                            else dados.at[j, "SEAL_B"]
                        )

                        if (
                            fam_base == fam_comp
                            and cabo_base == cabo_comp
                            and cor_base == cor_comp
                        ):
                            comp_base - comp_comp
                            if abs(comp_base - comp_comp) <= tolerancia:
                                if (
                                    (
                                        termA_base == termA_comp
                                        and termB_base == termB_comp
                                    )
                                    or (
                                        termA_base == termB_comp
                                        and termB_base == termA_comp
                                    )
                                ) and (
                                    (
                                        seloA_base == seloA_comp
                                        and seloB_base == seloB_comp
                                    )
                                    or (
                                        seloA_base == seloB_comp
                                        and seloB_base == seloA_comp
                                    )
                                ):
                                    dados.at[i, "STATUS"] = "2"
                                    dados.at[j, "STATUS"] = "2"
                                    if "TW" in dados.at[i, "Leadset"]:
                                        dados.at[i, "CIRC_MASTER"] = str(
                                            dados.at[i, "Internal Family"]
                                        ) + str(dados.at[i, "CIRCUIT"])
                                        dados.at[i, "CIRC_COMUNS"] = str(
                                            dados.at[i, "Internal Family"]
                                        ) + str(dados.at[i, "CIRCUIT"])
                                        dados.at[j, "CIRC_MASTER"] = str(
                                            dados.at[i, "Internal Family"]
                                        ) + str(dados.at[i, "CIRCUIT"])
                                        dados.at[j, "CIRC_COMUNS"] = str(
                                            dados.at[j, "Internal Family"]
                                        ) + str(dados.at[j, "CIRCUIT"])

                                        dados.at[i, "STATUS"] = "Novo 2"
                                        dados.at[j, "STATUS"] = "Novo 2"
                                    else:
                                        if ckt_base != ckt_comp:
                                            dados.at[i, "CIRC_MASTER"] = dados.at[
                                                i, "Leadset"
                                            ]
                                            dados.at[i, "CIRC_COMUNS"] = dados.at[
                                                i, "Leadset"
                                            ]
                                            dados.at[j, "CIRC_MASTER"] = dados.at[
                                                i, "Leadset"
                                            ]
                                            dados.at[j, "CIRC_COMUNS"] = dados.at[
                                                j, "Leadset"
                                            ]

                                            dados.at[i, "STATUS"] = "Novo 2"
                                            dados.at[j, "STATUS"] = "Novo 2"

    colunas_add = [
        "Alocações",
        "Volume",
        "Vol/dia [LCR]",
        "Vol/dia [MCR]",
        "Vol/Lote",
        "Time_Batch(h)",
        "Rack Aloc",
        "Estoque/Dias",
        "Tipos",
        "Bundle size",
        "Bundle count",
        "Elastic",
        "Protect Cup",
        "Hangers",
        "Número de Kanbans",
        "Branco (Operacional)",
        "Amarelo (Alerta)",
        "Laranja (Segurança)",
        "Processo",
        "ProcessoA",
        "ProcessoB",
        "Lclass",
        "Conveyor Length",
        "Mch_Name",
        "Mch",
        "IDMch",
        "Rate",
        "Runtime",
        "Time Batch",
        "Tempo de setup/hs",
        "Tempo de setup/min",
        "Tempo total / dia",
        "Multicore",
        "Open ends",
        "Connection Technology_A",
        "Connection Technology_B",
        "Feed Type/Delivery Form_A",
        "Feed Type/Delivery Form_B",
        "InkJet",
        "VisionSystem",
        "MiddleStrip",
        "Micrograph",
        "CktType",
        "CktsCount",
        "##1",
        "##2",
        "##3",
        "##4",
        "##5",
        "##6",
        "##7",
        "##8",
        "##9",
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
        "##10",
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
        "##11",
        "C.PressLocation",
        "##12",
        "C.HSA",
        "C.HS.RateA",
        "C.HS.RunningTA",
        "C.HS.SetupTA",
        "C.HS.WorkTimeA",
        "C.HS.RunningTA_MCR",
        "##13",
        "C.HSB",
        "C.HS.RateB",
        "C.HS.RunningTB",
        "C.HS.SetupTB",
        "C.HS.WorkTimeB",
        "C.HS.RunningTB_MCR",
        "##14",
        "C.BubbleTest",
        "C.BubbleTest.Freq",
        "C.BubbleTest.Rate",
        "C.BubbleTest.Vol",
        "C.BubbleTest.RunningT",
        "C.BubbleTest.SetupT",
        "C.BubbleTest.WorkTime",
        "##15",
        "C.SolderA",
        "C.Solder.LoteA",
        "C.Solder.RateA",
        "C.Solder.RunningTA",
        "C.Solder.SetupTA",
        "C.Solder.WorkTimeA",
        "##16",
        "C.SolderB",
        "C.Solder.LoteB",
        "C.Solder.RateB",
        "C.Solder.RunningTB",
        "C.Solder.SetupTB",
        "C.Solder.WorkTimeB",
        "##17",
        "C.Strip",
        "C.Strip_VolDay",
        "C.Strip.Rate",
        "C.Strip.RunningT",
        "C.Strip.SetupT",
        "C.Strip.WorkTime",
        "##18",
    ]

    # for c in colunas_add:
    #     if c not in dados.columns:
    #         dados[c] = None

    colunas = [
        "Leadset",
        "CIRC_MASTER",
        "CIRC_COMUNS",
        "STATUS",
        "##1",
        "Alocações",
        "##2",
        "Volume",
        "Vol/dia [LCR]",
        "Vol/dia [MCR]",
        "Estoque/Dias",
        "Tipos",
        "Vol/Lote",
        "##3",
        "Bundle size",
        "Bundle count",
        "Time_Batch(h)",
        "Elastic",
        "Protect Cup",
        "Hangers",
        "Rack Aloc",
        "##4",
        "InkJet",
        "VisionSystem",
        "MiddleStrip",
        "Micrograph",
        "CktType",
        "CktsCount",
        "Processo",
        "Lclass",
        "##5",
        "Número de Kanbans",
        "Branco (Operacional)",
        "Amarelo (Alerta)",
        "Laranja (Segurança)",
        "##6",
        "ProcessoA",
        "ProcessoB",
        "##7",
        "Mch_Name",
        "Mch",
        "IDMch",
        "Rate",
        "Runtime",
        "Time Batch",
        "Tempo de setup/hs",
        "Tempo de setup/min",
        "Conveyor Length",
        "##8",
        "Tempo total / dia",
        "Multicore",
        "Open ends",
        "Connection Technology_A",
        "Feed Type/Delivery Form_A",
        "Connection Technology_B",
        "Feed Type/Delivery Form_B",
        "##9",
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
        "##10",
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
        "##11",
        "C.PressLocation",
        "##12",
        "C.HSA",
        "C.HS.RateA",
        "C.HS.RunningTA",
        "C.HS.SetupTA",
        "C.HS.WorkTimeA",
        "C.HS.RunningTA_MCR",
        "##13",
        "C.HSB",
        "C.HS.RateB",
        "C.HS.RunningTB",
        "C.HS.SetupTB",
        "C.HS.WorkTimeB",
        "C.HS.RunningTB_MCR",
        "##14",
        "C.BubbleTest",
        "C.BubbleTest.Freq",
        "C.BubbleTest.Rate",
        "C.BubbleTest.Vol",
        "C.BubbleTest.RunningT",
        "C.BubbleTest.SetupT",
        "C.BubbleTest.WorkTime",
        "##15",
        "C.SolderA",
        "C.Solder.LoteA",
        "C.Solder.RateA",
        "C.Solder.RunningTA",
        "C.Solder.SetupTA",
        "C.Solder.WorkTimeA",
        "##16",
        "C.SolderB",
        "C.Solder.LoteB",
        "C.Solder.RateB",
        "C.Solder.RunningTB",
        "C.Solder.SetupTB",
        "C.Solder.WorkTimeB",
        "##17",
        "C.Strip",
        "C.Strip_VolDay",
        "C.Strip.Rate",
        "C.Strip.RunningT",
        "C.Strip.SetupT",
        "C.Strip.WorkTime",
        "##18",
        "TYPE",
        "WERKS",
        "External Family",
        "FILE_LINE",
        "STATUS_REGISTRO",
        "Internal Family",
        "CIRCUIT",
        "WIRE_TUBE_SPLICE",
        "LENGTH",
        "Comp TW",
    ]
    dados = reordenar_colunas(dados, colunas)

    arq_sap = (
        dados[["CIRC_MASTER", "CIRC_COMUNS", "STATUS"]]
        .dropna(how="all")
        .reset_index(drop=True)
    )

    arq_sap = arq_sap.sort_values(by=["CIRC_MASTER", "CIRC_COMUNS"]).reset_index(
        drop=True
    )

    arq_sap["WERKS"] = 1600

    arq_sap = arq_sap[["WERKS", "CIRC_MASTER", "CIRC_COMUNS", "STATUS"]]

    dados = add_BOM(dados)
    dados = add_ALOC(dados)

    return dados, arq_sap


def comunization():
    os.system("cls")

    logo("Gerar comunização")

    logger.info("Entre com o caminho do arquivo SAP")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo de COMUNIZAÇÃO ENVIADO PARA SAP")
    caminho_cmz = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    caminho_base = caminho_base.replace("XLSX", "xlsx")

    try:
        dados, arquivo_sap = gerar_comunization(caminho_base, caminho_cmz)

        data_atual = datetime.now().strftime("%d.%m.%Y")

        dados.to_excel(
            f"{caminho_output}\Lista_do_Corte_{data_atual}.xlsx", index=False
        )
        arquivo_sap.to_csv(
            f"{caminho_output}/1600.Comuniza.{data_atual}_novo.csv",
            sep=";",
            index=False,
        )

    except Exception as e:
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
