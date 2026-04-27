
import pandas as pd
import sys
import os
from datetime import datetime
import warnings
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
warnings.simplefilter("ignore")

root_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

# Agora você pode importar normalmente
from src.function import *
from src.extrair_cuts import *


def fazer_previsao(path_base1:pd.DataFrame = None, path_base2:pd.DataFrame = None) -> pd.DataFrame:
    # Historico de oderns no CAO
    path_base1 =r"C:\Users\tgodoi01\Downloads\Ordens.xlsx"

    # EXPORT SAP
    path_base2 = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Desktop\Projeto 2027&Carbon\Analise CARBON\Extrato_SAP_2026_01_05.xlsx"

    with open(path_base1, 'rb' ) as f:
        dados_ordens = pd.read_excel(f)[['Leadset','Work Station']]

    with open(path_base2, 'rb' ) as f:
        dados_sap = pd.read_excel(f)


    dict_SECTIONN = {'0 1':0.1, '0 0':0}
    dados_sap['SECTIONN'] = dados_sap['SECTIONN'].map(dict_SECTIONN).fillna(dados_sap['SECTIONN'])
    dados_sap['SECTIONN'].fillna(0,inplace=True)


    dados_ordens = dados_ordens.dropna(subset=['Work Station']).reset_index(drop=True)

    dados_sap_alt = dados_sap[['Leadset', 'WIRE_TUBE_SPLICE','LENGTH', 'SECTIONN', 'TERM_A', 'STRIP_A','SEAL_A', 'JOINT_TO_A', 'RMKS_A', 'TERM_B', 'STRIP_B', 'SEAL_B','JOINT_TO_B', 'RMKS_B']]

    df_merged = dados_ordens.merge(dados_sap_alt, on='Leadset', how='left')
    df_merged.dropna(how='all',subset=['WIRE_TUBE_SPLICE', 'LENGTH', 'SECTIONN',
                                    'TERM_A', 'STRIP_A', 'SEAL_A', 'JOINT_TO_A', 
                                    'RMKS_A', 'TERM_B','STRIP_B', 'SEAL_B', 
                                    'JOINT_TO_B', 'RMKS_B'],inplace=True)
    
    def app_proj(x):
        if pd.isna(x):
            return None

        x = str(x)

        if x.startswith('S'):
            return 'SPIN'
        elif x.startswith('G'):
            return 'GEM'
        elif x.startswith('V'):
            return 'VS30'
        elif x.startswith('B'):
            return 'U11'
        elif x.startswith('X'):
            return 'XDF'
        else:
            return None  # explícito

    df_merged['Projeto'] = df_merged['Leadset'].apply(app_proj)

    df_merged['Multicore'] = df_merged['Leadset'].apply(lambda x: 'Tw' if 'TW' in x else None)

    df_merged = df_merged[~df_merged['Work Station'].isin(['VRT','VIRTUAL'])].reset_index(drop=True)

    # -----------------------------
    # 1️⃣ Definindo target e features
    # -----------------------------
    y = df_merged['Work Station'].astype(str)

    # Definindo colunas numéricas e categóricas
    num_cols = ['LENGTH','SECTIONN','STRIP_A', 'STRIP_B']  # mantemos NaN
    cat_cols = ['WIRE_TUBE_SPLICE', 'TERM_A', 'TERM_B', 
                'SEAL_A', 'SEAL_B', 'RMKS_A', 'RMKS_B','JOINT_TO_A', 'JOINT_TO_B','Multicore','Projeto']

    X_num = df_merged[num_cols]
    X_cat = df_merged[cat_cols]

    # -----------------------------
    # 2️⃣ One-hot apenas nas categóricas
    # -----------------------------
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_cat_encoded = encoder.fit_transform(X_cat)

    # Concatenando features numéricas e codificadas
    X_encoded = np.hstack([X_num.values, X_cat_encoded])

    # -----------------------------
    # 3️⃣ Split treino/teste (estratificado)
    # -----------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X_encoded, y, test_size=0.2, random_state=42, stratify=y
    )

    # -----------------------------
    # 4️⃣ Treinando o modelo
    # -----------------------------

    clf = HistGradientBoostingClassifier(
        max_iter=500,
        max_depth=10,
        learning_rate=0.05,
        min_samples_leaf=20,
        random_state=42,
        early_stopping=True,
        validation_fraction=0.1,
        n_iter_no_change=20,
        verbose=2
    )
    clf.fit(X_train, y_train)

    # -----------------------------
    # 5️⃣ Avaliação
    # -----------------------------
    y_pred = clf.predict(X_test)

    print("Acurácia:", accuracy_score(y_test, y_pred))
    print("\nRelatório de classificação:\n", classification_report(y_test, y_pred))

    # -----------------------------
    # 6️⃣ Previsão em novos dados (dados_sap)
    # -----------------------------

    dados_sap['Multicore'] = dados_sap['Leadset'].apply(lambda x: 'Tw' if 'TW' in x else None)

    dados_sap['Projeto'] = dados_sap['Leadset'].apply(app_proj)

    X_num_new = dados_sap[num_cols]
    X_cat_new = dados_sap[cat_cols]

    # Transformando categóricas com o encoder já treinado
    X_cat_new_encoded = encoder.transform(X_cat_new)

    # Concatenando numéricas e codificadas
    X_new_encoded = np.hstack([X_num_new.values, X_cat_new_encoded])

    # Prevendo
    y_new_pred = clf.predict(X_new_encoded)

    # Adicionando coluna de previsão ao DataFrame original
    dados_sap['Máq'] = y_new_pred

    colunas_alvo = ['Leadset','Máq']
    dados_sap = reordenar_colunas(dados_sap, colunas_prioritarias=colunas_alvo)

    dados_sap.drop(columns=['Multicore','Projeto'],inplace=True)

    return dados_sap


def prever():
    os.system("cls")

    logo("Add Maq - Cut list")

    logger.info("Entre com o caminho do arquivo de report de Ordens")
    path_df = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do Extrato_SAP")
    path_analise = input("[>] ").replace("/", "\\").replace('"', "")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    caminho_output = input("[>] ")

    

    try:
        dados_prev = fazer_previsao(path_df, path_analise)

        salvar_arquivo(dados_prev, caminho_pasta=caminho_output, nome_arquivo='Lista_Extrato_SAP_com_Maq',formato='excel')

    except Exception as e:
        traceback.print_exc()
        logger.error(f"Erro ao ler o arquivo: {e}")

    logger.info("Arquivo Salvo!")