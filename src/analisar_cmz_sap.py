import pandas as pd
import sys
import os
from typing import Tuple

import warnings

import traceback


warnings.simplefilter("ignore")

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

# Agora você pode importar normalmente
from src.function import *

logger = LoggerTerminal(salvar_log=False, typing=True)

def analise_cmz(df_dados: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """
    Analisa o DataFrame removendo iterativamente registros onde CIRC_MASTER
    aparece também em CIRC_COMUNS (exceto quando são iguais na mesma linha).

    A cada iteração, remove apenas um CIRC_MASTER comum.
    
    Parameters
    ----------
    df_dados : pd.DataFrame
        DataFrame contendo as colunas 'CIRC_MASTER' e 'CIRC_COMUNS'
    verbose : bool, optional
        Se True, imprime os itens removidos

    Returns
    -------
    pd.DataFrame
        DataFrame tratado
    """

    df_dados = df_dados.copy()

    while True:
        # marca linhas onde os valores são exatamente iguais
        mask_iguais = df_dados['CIRC_MASTER'] == df_dados['CIRC_COMUNS']
        df_dados.loc[mask_iguais, '_tmp_master'] = True

        # dataframe para análise (exclui linhas iguais)
        df_check = (
            df_dados[df_dados['_tmp_master'].isna()]
            .drop(columns=['_tmp_master'])
        )

        lista1 = df_check['CIRC_MASTER'].dropna().unique()
        lista2 = df_check['CIRC_COMUNS'].dropna().unique()

        comuns = set(lista1) & set(lista2)

        # remove coluna temporária antes de decidir sair
        df_dados.drop(columns=['_tmp_master'], inplace=True, errors='ignore')

        if not comuns:
            break

        # remove apenas um item por iteração
        item = next(iter(comuns))

        if verbose:
            print(f'Item excluído: {item}')
        

        df_dados = df_dados[df_dados['CIRC_MASTER'] != item]

    try:
        print(f'Item excluído: {item}')
    except: pass
    return df_dados.reset_index(drop=True)


def comparar_dataframes(df1: pd.DataFrame,
                        df2: pd.DataFrame,
                        key_cols=('CIRC_MASTER', 'CIRC_COMUNS'),
                        return_rows=True,
                        drop_duplicates_keys=True):
    """
    Compara dois DataFrames com base em colunas-chave e retorna o delta:
    - comum: chaves presentes nos dois DataFrames
    - exclusivos_df1: chaves só no df1
    - exclusivos_df2: chaves só no df2
    - removidos: chaves presentes no df1 e ausentes no df2 (equivalente a exclusivos_df1)

    Parâmetros:
        df1, df2: DataFrames a comparar
        key_cols: tupla/list com os nomes das colunas-chave
        return_rows: se True, retorna linhas completas; se False, apenas DataFrames com as chaves
        drop_duplicates_keys: se True, desduplica pelas chaves antes de comparar para evitar falsos positivos

    Retorna:
        dict com DataFrames:
            {
              'comum': DataFrame,
              'exclusivos_df1': DataFrame,
              'exclusivos_df2': DataFrame,
              'removidos': DataFrame
            }
    """

    # Garantir que key_cols existe nos dois DFs
    for col in key_cols:
        if col not in df1.columns or col not in df2.columns:
            raise KeyError(f"Coluna-chave '{col}' não encontrada em ambos os DataFrames.")

    # Opcional: remover duplicidades pelas chaves para comparação mais limpa
    if drop_duplicates_keys:
        df1_keys = df1[list(key_cols)].drop_duplicates()
        df2_keys = df2[list(key_cols)].drop_duplicates()
    else:
        df1_keys = df1[list(key_cols)]
        df2_keys = df2[list(key_cols)]

    # Merge com indicador para classificar presença
    cmp = df1_keys.merge(df2_keys, on=list(key_cols), how='outer', indicator=True)

    # Conjuntos de chaves por categoria
    mask_comum = cmp['_merge'] == 'both'
    mask_exclusivos_df1 = cmp['_merge'] == 'left_only'
    mask_exclusivos_df2 = cmp['_merge'] == 'right_only'

    comum_keys = cmp.loc[mask_comum, list(key_cols)]
    exclusivos_df1_keys = cmp.loc[mask_exclusivos_df1, list(key_cols)]
    exclusivos_df2_keys = cmp.loc[mask_exclusivos_df2, list(key_cols)]

    # 'removidos' = presentes antes (df1) e ausentes agora (df2)
    removidos_keys = exclusivos_df1_keys.copy()

    if not return_rows:
        # Retorna apenas as chaves (sem outras colunas)
        return {
            'comum': comum_keys.reset_index(drop=True),
            'exclusivos_df1': exclusivos_df1_keys.reset_index(drop=True),
            'exclusivos_df2': exclusivos_df2_keys.reset_index(drop=True),
            'removidos': removidos_keys.reset_index(drop=True)
        }

    # Se você prefere retornar as LINHAS COMPLETAS
    # (filtradas pelo conjunto de chaves correspondente):
    def _filter_rows(df, keys_df):
        if keys_df.empty:
            return df.iloc[0:0].copy()  # DataFrame vazio com mesmas colunas
        # join para voltar às linhas originais que batem com as chaves
        # Observação: se houver duplicidades nas chaves em df, manterá todas as combinações
        return df.merge(keys_df, on=list(key_cols), how='inner')

    result = {
        'comum': _filter_rows(df1, comum_keys).reset_index(drop=True),
        'exclusivos_df1': _filter_rows(df1, exclusivos_df1_keys).reset_index(drop=True),
        'exclusivos_df2': _filter_rows(df2, exclusivos_df2_keys).reset_index(drop=True),
        'removidos': _filter_rows(df1, removidos_keys).reset_index(drop=True)
    }

    return result


def marcar_inversoes(df_de: pd.DataFrame, df_para: pd.DataFrame) -> pd.DataFrame:
    """
    Marca registros em df_de onde (CIRC_MASTER, CIRC_COMUNS)
    aparece invertido em df_para.
    """

    df_de = df_de.copy()
    df_para = df_para.copy()
    
    df_de['Status']=None

    # cria chaves como tuplas (seguro)
    df_de['key'] = list(zip(df_de['CIRC_MASTER'], df_de['CIRC_COMUNS']))
    df_para['key'] = list(zip(df_para['CIRC_MASTER'], df_para['CIRC_COMUNS']))
    df_para['key_inv'] = list(zip(df_para['CIRC_COMUNS'], df_para['CIRC_MASTER']))

    set_de = set(df_de['key'])
    set_para = set(df_para['key'])
    set_para_inv = set(df_para['key_inv'])

    inversoes = set_de & set_para_inv

    df_de.loc[df_de['key'].isin(inversoes), 'Status'] = (
        'Foi invertido o CIRC_MASTER e CIRC_COMUNS'
    )

    df_de['Status'] = df_de['Status'].fillna('Removido')

    return df_de.drop(columns=['key'])


def analise_final_cmz(
    df_atual: pd.DataFrame,
    df_novo: pd.DataFrame,
    verbose: bool = True
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Executa a análise final de CMZ:
    - Normaliza os dois DataFrames (analise_cmz)
    - Compara atual vs novo
    - Identifica registros removidos
    - Marca inversões de CIRC_MASTER e CIRC_COMUNS

    Parameters
    ----------
    df_atual : pd.DataFrame
        Base atual
    df_novo : pd.DataFrame
        Base nova
    verbose : bool, optional
        Exibe logs do processamento

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (delta_filtro, df_novo_tratado)
    """

    df_atual = analise_cmz(df_dados=df_atual.copy(), verbose=verbose)
    df_novo = analise_cmz(df_dados=df_novo.copy(), verbose=verbose)

    delta = comparar_dataframes(
        df_atual,
        df_novo,
        key_cols=('CIRC_MASTER', 'CIRC_COMUNS'),
        return_rows=True,
        drop_duplicates_keys=True
    )

    delta_filtro = (
        delta['removidos']
        .assign(_status=lambda x: x['CIRC_MASTER'] == x['CIRC_COMUNS'])
        .query('_status == False')
        .drop(columns='_status')
        .reset_index(drop=True)
    )

    delta_filtro = marcar_inversoes(delta_filtro, df_novo)

    return delta_filtro, df_novo

def arrumar_cmz(dados_atual: pd.DataFrame, dados_novo: pd.DataFrame) -> pd.DataFrame:
    lista_master = dados_atual['CIRC_MASTER'].dropna().unique()
    
    # 👇 congelar estado original
    dados_base = dados_novo.copy()

    for master in lista_master:
        dados_prov = dados_base[
            (dados_base['CIRC_MASTER'] == master) |
            (dados_base['CIRC_COMUNS'] == master)
        ]

        if not dados_prov.empty:
            old_master = dados_prov.iloc[0]['CIRC_MASTER']

            mask = dados_novo['CIRC_MASTER'] == old_master
            dados_novo.loc[mask, 'CIRC_MASTER'] = master
                
    return dados_novo


def analise_comunization():
    os.system("cls")

    logo("Análisar Comunização")

    logger.info("Entre com o caminho do arquivo de Comunização Atual [csv]")
    caminho_base = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do arquivo de Comunização Novo [csv]")
    caminho_cmz = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    caminho_base = caminho_base.replace("XLSX", "xlsx")

    try:
        dict_df = {}
        
        df_atual = pd.read_csv(caminho_base,sep=';').dropna(how='all',axis=0)
        df_novo = pd.read_csv(caminho_cmz,sep=';').dropna(how='all',axis=0)
        
        df_novo = arrumar_cmz(dados_atual=df_atual, dados_novo=df_novo)
        


        # REMOVER------------------------------------------------------------------------------------
        dict_df['Remover'], df_atualizado = analise_final_cmz(df_atual=df_atual, df_novo=df_novo, verbose=True)

        data_atual = datetime.now().strftime("%d.%m.%Y")


        
        df_atualizado.to_csv(
            f"{caminho_output}/1600.Comuniza.{data_atual}_corrigido.csv",
            sep=";",
            index=False,
        )
        
        # ADICIONAR
        #dict_df['Adicionar'], df_atualizado = analise_final_cmz(df_atual=df_novo, df_novo=df_atual, verbose=True)  
        
        #dict_df['Adicionar']['Status']='Adicionar'
        
        salvar_dict_df_em_excel(dfs_dict=dict_df,caminho_arquivo=f"{caminho_output}\Delta_da_alteração_Cmz_{data_atual}.xlsx")

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")
