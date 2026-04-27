import win32com.client
import os
from src.function import *
from art import *
from tqdm import tqdm
import warnings

warnings.simplefilter("ignore")


logger = LoggerTerminal(salvar_log=False, typing=True)


def extrairEmail():
    os.system("cls")

    logo("Extrair Anexos de e-mail")

    logger.info("Entre com o caminho do diretório, onde quer salvar os arquivos")
    save_path = input("").replace("\\", "\\\\")

    logger.info("Entre com as palavras-chave, separadas por vírgula [,]:")
    entrada = input()
    keywords = [palavra.strip() for palavra in entrada.split(",")]

    # Garante que o diretório existe
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Lista de palavras-chave
    # keywords = ["delta-cut", "CHARTED CUTSHEET"]

    # Conectando ao Outlook
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = Caixa de Entrada
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # Ordena por data de recebimento (opcional)

    logger.info(f"Quantidade de e-mail: {len(messages)}")

    # Filtrando e salvando anexos
    for message in tqdm(messages, "[*] Processando...", colour="blue"):
        try:
            # if "CR" in subject and message.Attachments.Count > 0:
            for i in range(message.Attachments.Count):
                attachment = message.Attachments.Item(i + 1)
                filename = attachment.FileName.lower()
                if any(
                    keyword in filename for keyword in keywords
                ):  # and (filename.endswith(".xls") or filename.endswith(".xlsx")):
                    full_path = os.path.join(save_path, attachment.FileName)
                    attachment.SaveAsFile(full_path)
                    logger.info(f"Arquivo salvo: {full_path}")
                    break  # Para evitar múltiplos salvamentos por e-mail

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    logger.info(f"Arquivos salvos: {save_path}")
