import os
import ctypes
import shutil
import tempfile
from send2trash import send2trash
from src.function import *

logger = LoggerTerminal(salvar_log=False, typing=True)


def limpar_temporarios():
    try:
        # Caminho dos arquivos temporários do sistema
        temp_system_dir = r"C:\Windows\Temp"
        temp_user_dir = tempfile.gettempdir()

        # Limpeza de arquivos temporários do sistema
        if os.path.exists(temp_system_dir):
            for file_name in os.listdir(temp_system_dir):
                file_path = os.path.join(temp_system_dir, file_name)
                if os.path.isfile(file_path):
                    send2trash(file_path)
                    logger.info(
                        f"Arquivo temporário do sistema movido para a lixeira: {file_path}"
                    )
                elif os.path.isdir(file_path):
                    try:
                        shutil.rmtree(file_path)  # Remove diretórios temporários
                        logger.info(
                            f"Diretório temporário do sistema removido: {file_path}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Erro ao remover diretório temporário {file_path}: {e}"
                        )

        # Limpeza de arquivos temporários do usuário
        if os.path.exists(temp_user_dir):
            for file_name in os.listdir(temp_user_dir):
                file_path = os.path.join(temp_user_dir, file_name)
                if os.path.isfile(file_path):
                    send2trash(file_path)
                    logger.info(
                        f"Arquivo temporário do usuário movido para a lixeira: {file_path}"
                    )
                elif os.path.isdir(file_path):
                    try:
                        shutil.rmtree(file_path)  # Remove diretórios temporários
                        logger.info(
                            f"Diretório temporário do usuário removido: {file_path}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Erro ao remover diretório temporário {file_path}: {e}"
                        )
    except Exception as e:
        logger.error(f"Erro ao limpar temporários: {e}")


def limpar_lixeira():
    try:
        # Chamando a função do Windows para limpar a lixeira
        ctypes.windll.shell32.SHEmptyRecycleBinW(0, None, 0)  # Limpa a lixeira
        logger.info("Lixeira limpa com sucesso!")
    except Exception as e:
        logger.error(f"Erro ao limpar a lixeira: {e}")


def limpar_completo():
    os.system("cls")
    logo("SystemScrub")

    limpar_temporarios()
    limpar_lixeira()
    logger.info("Limpeza completa concluída!")
