import pandas as pd
from datetime import datetime
import os

# Nome do arquivo Excel
arquivo_excel = (
    r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Desktop\registro_atividades.xlsx"
)
df_existente = pd.read_excel(arquivo_excel, engine="openpyxl")

print("Programa de registro de atividades iniciado. Pressione Ctrl+C para encerrar.\n")

while True:
    try:
        # Solicita os dados ao usuário
        atividade = input("Digite a atividade realizada: ").strip().title()
        hora_inicio = input(f"Digite a hora de inicio (HH:MM):")
        hora_fim = input("Digite a hora de fim (HH:MM): ").strip()
        status = input("Digite o status da atividade: ").strip().title()

        # Obtém a data atual
        data_atual = datetime.now().date()

        # Cria um dicionário com os dados
        registro = {
            "Data": [data_atual.strftime("%Y-%m-%d")],
            "Hora Início": [hora_inicio],
            "Hora Fim": [hora_fim],
            "Atividade": [atividade],
            "Status": [status],
        }

        # Converte para DataFrame
        df_novo = pd.DataFrame(registro)

        # Verifica se o arquivo já existe
        if os.path.exists(arquivo_excel):
            df_existente = pd.read_excel(arquivo_excel, engine="openpyxl")
            df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        else:
            df_final = df_novo

        # Salva no arquivo Excel
        df_final.to_excel(arquivo_excel, index=False, engine="openpyxl")

        print("✅ Registro salvo com sucesso!\n")

    except KeyboardInterrupt:
        print("\nPrograma encerrado pelo usuário.")
        break
