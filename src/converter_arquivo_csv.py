import os
import csv
from art import *
from src.function import *


logger = LoggerTerminal(salvar_log=False, typing=True)


def converter_csv_para_ponto_virgula():
    os.system("cls")

    logo("Converte arquivo csv")

    logger.info("Digite o caminho do arquivo CSV: ")
    caminho_arquivo = input("").replace('"', "")

    if not caminho_arquivo.lower().endswith(".csv"):
        logger.atencao("O arquivo informado não é um CSV.")
        return

    if not os.path.exists(caminho_arquivo):
        logger.erro("Caminho inválido ou arquivo não encontrado.")
        return

    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            amostra = f.read(
                1024
            )  # lê os primeiros 1024 bytes para verificar o separador
            f.seek(0)

            sniffer = csv.Sniffer()
            dialecto = sniffer.sniff(amostra)

            if dialecto.delimiter != ",":
                logger.atencao(
                    "O arquivo não usa vírgula como separador. Nenhuma conversão necessária."
                )
                return

            leitor = csv.reader(f, delimiter=",")
            linhas = list(leitor)

        # Criar novo nome de arquivo
        pasta, nome_arquivo = os.path.split(caminho_arquivo)
        nome_base, ext = os.path.splitext(nome_arquivo)
        novo_nome = f"{nome_base}_convertido{ext}"
        novo_caminho = os.path.join(pasta, novo_nome)

        # Escrever com novo separador (;)
        with open(novo_caminho, "w", newline="", encoding="utf-8") as f:
            escritor = csv.writer(f, delimiter=";")
            escritor.writerows(linhas)

        logger.info(f"Conversão concluída. Novo arquivo salvo em: {novo_caminho}")

    except Exception as e:
        logger.erro(f"Erro ao processar o arquivo: {e}")
