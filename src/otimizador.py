import pandas as pd
import sys
import os
from datetime import datetime
import warnings
import math
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.cluster import AgglomerativeClustering
from gower import gower_matrix
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
warnings.simplefilter("ignore")

# EXPORT SAP
path_base2 = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Desktop\Projeto 2027&Carbon\Analise CARBON\Extrato_SAP_2026_01_05.xlsx"

with open(path_base2, 'rb' ) as f:
    dados_sap = pd.read_excel(f)
    
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
    
    
def app_calha(x):
    if x <= 8: 
        return 4
    elif x > 8 and x< 16:
        return 8
    else:
        return 12

dados_sap['Projeto'] = dados_sap['Leadset'].apply(app_proj)
dados_sap['Calha'] = dados_sap['LENGTH'].apply(lambda x: math.ceil(x/500))
dados_sap['Calha'] = dados_sap['Calha'].apply(app_calha)


dict_SECTIONN = {'0 1':0.1, '0 0':0}
dados_sap['SECTIONN'] = dados_sap['SECTIONN'].map(dict_SECTIONN).fillna(dados_sap['SECTIONN'])
dados_sap['SECTIONN'].fillna(0,inplace=True)


dados_sap_alt = dados_sap[['WIRE_TUBE_SPLICE','Calha', 'SECTIONN', 'TERM_A', 'SEAL_A','TERM_B', 'SEAL_B']]

dados_sap_alt.dropna(how='all', subset=['WIRE_TUBE_SPLICE', 'TERM_A', 'SEAL_A','TERM_B', 'SEAL_B'],inplace=True)




# dataframe
df = dados_sap_alt.copy()

# Selecionar colunas relevantes
cols = ['Calha', 'SECTIONN', 'TERM_A', 'SEAL_A', 'TERM_B', 'SEAL_B']
X = df[cols]

# Distância de Gower
gower_dist = gower_matrix(X)

# Clustering hierárquico
model = AgglomerativeClustering(
    n_clusters=4,
    metric='precomputed',
    linkage='average'
)

df['cluster'] = model.fit_predict(gower_dist)

df.to_excel(r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Desktop\Mapa lead Prep Novo\otimizador.xlsx",index=False)