import pandas as pd
from tqdm import tqdm
from datetime import datetime
from collections import Counter
import traceback

import sys
import os

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from src.function import *
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


def gerar_comunizacao_arquivo_sap(path_dados:str = None) -> pd.DataFrame:
    with open(path_dados, 'rb') as f:
        dados = pd.read_excel(f)

    dados = dados.sort_values(by=["Internal Family"]).reset_index(drop=True)

    colunas = ['WIRE_TUBE_SPLICE', 'LENGTH', 'Comp TW','SECTIONN',
            'TERM_A', 'STRIP_A', 'SEAL_A',
            'TERM_B', 'STRIP_B', 'SEAL_B']

    # Converter tudo para string antes de usar Counter
    dados['linha_key'] = dados[colunas].apply(
        lambda row: tuple(sorted((str(k), v) for k, v in Counter(row).items())),
        axis=1
    )

    dados['Status'] = None

    # Agrupar por essa chave
    grupos = dados.groupby('linha_key').indices
    id = 1
    # Mostrar grupos com mais de uma linha
    for key, indices in grupos.items():
        if len(indices) > 1:
            dados.loc[indices,'Status'] = id
            id+=1

    dados.drop(columns=['linha_key'],inplace=True)

    dados['CIRC_MASTER'] = None
    dados['CIRC_MASTER'] = None
    dados['CIRC_COMUNS'] = None


    id_list = dados['Status'].dropna().unique().tolist()
    for i in id_list:
        index_number = dados[dados['Status']==i].index[0]
        index_list = dados[dados['Status']==i].index

        dados.loc[index_list,'CIRC_MASTER'] = dados.loc[index_number,'Leadset']
        dados.loc[index_number,'CIRC_COMUNS'] = dados.loc[index_number,'Leadset']
        for j in index_list[1:]:
            dados.loc[j,'CIRC_COMUNS'] = dados.loc[j,'Leadset']

        item_master = dados[dados['Status']==i]['CIRC_MASTER'].unique()
        item_comum = dados[dados['Status']==i]['CIRC_COMUNS'].unique()

        if len(item_master)==1  and len(item_comum)==1:
            
            dados.loc[index_list,'CIRC_MASTER'] = dados.loc[index_number,'Internal Family']+dados.loc[index_number,'CIRCUIT']
            dados.loc[index_number,'CIRC_COMUNS'] = dados.loc[index_number,'Internal Family']+dados.loc[index_number,'CIRCUIT']
            for j in index_list[1:]:
                dados.loc[j,'CIRC_COMUNS'] = dados.loc[j,'Internal Family']+dados.loc[j,'CIRCUIT']

        sectionn = dados[dados['Status']==i]['SECTIONN'].unique()

        if sectionn == '0 0' or sectionn == '0 1' or sectionn == '0.14'  or sectionn == '0.18':
            dados.loc[index_list,'CIRC_MASTER'] = None
            dados.loc[index_list,'CIRC_COMUNS'] = None
            dados.loc[index_list,'Status'] = None

    dados.drop(columns=['Status'], inplace=True)

    return dados

def comparar_tabela_sap(df0:pd.DataFrame=None, path_dados:str = None) -> pd.DataFrame:

    with open(path_dados, "rb") as f:
        df2 = pd.read_csv(f, sep=";")

    df1 = df0.copy()
    df1 = df1.dropna(subset=['CIRC_MASTER']).reset_index(drop=True)
    lista_master = df1['CIRC_MASTER'].unique().tolist()
    for i in lista_master:
        df_prov1 = sorted(df1[df1['CIRC_MASTER']==i]['CIRC_COMUNS'].unique().tolist())
        df_prov2 = sorted(df2[df2['CIRC_COMUNS'].isin(df_prov1)]['CIRC_COMUNS'].unique().tolist())

        if df_prov1!=df_prov2:
            if len(df_prov1) > 0 and len(df_prov2) == 0 :
                lista_index1 = df0[df0['CIRC_COMUNS'].isin(df_prov1)].index 
                df0.loc[lista_index1,'STATUS']='Adicionar'
            elif len(df_prov1) == 0 and len(df_prov2) > 0 :
                lista_index2 = df0[df0['CIRC_COMUNS'].isin(df_prov2)].index 
                df0.loc[lista_index2,'STATUS']='Remover'
        else:
            if len(df_prov1)==len(df_prov2):
                lista_index = df0[df0['CIRC_COMUNS'].isin(df_prov1)].index
                df0.loc[lista_index,'STATUS']='Já esta comunizado.'

    colunas = ['Leadset','TYPE','WERKS','External Family','FILE_LINE','STATUS_REGISTRO',
               'Internal Family','CIRC_MASTER','CIRC_COMUNS','STATUS','CIRCUIT','WIRE_TUBE_SPLICE',
               'LENGTH','Comp TW']
    df0 = reordenar_colunas(df0, colunas)

    return df0

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
        #dados, arquivo_sap = gerar_comunizacao_arquivo_sap(caminho_base)# caminho_cmz)


        dados = gerar_comunizacao_arquivo_sap(caminho_base)# caminho_cmz)

        dados = comparar_tabela_sap(dados, caminho_cmz) 

        data_atual = datetime.now().strftime("%d.%m.%Y")

        dados.to_excel(
            f"{caminho_output}\Lista_do_Corte_{data_atual}.xlsx", index=False
        )
        # arquivo_sap.to_csv(
        #     f"{caminho_output}/1600.Comuniza.{data_atual}_novo.csv",
        #     sep=";",
        #     index=False,
        # )

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
