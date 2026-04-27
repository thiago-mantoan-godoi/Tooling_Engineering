import os
import time
from art import text2art
from rich.console import Console
import traceback
import logging



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)


# === IMPORTAÇÃO DAS FUNÇÕES ===
from src.extrair_cuts import consolidar_cuts
from src.converter_arquivo_csv import converter_csv_para_ponto_virgula
from src.extrair_circuitos_especiais import extrair_ckt_especiais
from src.cadastro_cao import cadastro
from src.esvazir_lixeira import limpar_completo
from src.extrair_email import extrairEmail
from src.convert_SAP import converter
from src.gerar_comunz import comunization
from src.comparar_CAO_SAP import comparar
from src.comparar_fam_SAP import comparar_fam
from src.Criar_CAO_Base_SAP import comparar_fam_sap_cao
from src.Criar_CAO_Base_SAP_Completo import comparar_fam_sap_cao_completo
from src.Converter_tabela_cmz_sap import converter_cmz_sap
from src.analise_cao_vs_SAP import comparar_ordens
from src.gerar_base_c5 import gerar_base_para_c5
from src.excluir_arquivos import excluir_arq
from src.extrair_derivativo_sap import extrair_pn
from src.analise_de_cr import analisador
from src.gerar_comunz_Rev_1 import comunization as cmz
from src.prever_maquina import prever
from src.analisar_cmz_sap import analise_comunization

console = Console()

# ============================================================
#                      CONFIGURAÇÃO
# ============================================================

FERRAMENTAS = {
    "1": ("Consolidar Cuts", consolidar_cuts),
    "2": ("Converter Arquivos CSV", converter_csv_para_ponto_virgula),
    "3": ("Extrair Circuitos Especiais", extrair_ckt_especiais),
    "4": ("Responder CR", analisador),
    "5": ("Cadastro CAO", cadastro),
    "6": ("Converter Arquivo SAP", converter),
    "7": ("Gerar Comunização [SAP]", None),
    "8": ("Extrair Anexos do E-mail [CR]", extrairEmail),
    "9": ("Limpeza total do sistema", limpar_completo),
    "10": ("Comparar CAO vs SAP [Ordens, ZMM385, Master Data, Permit]", comparar),
    "11": ("Comparar FAM do SAP", comparar_fam),
    "12": ("Atualizar CAO com Base SAP", comparar_fam_sap_cao),
    "13": ("Atualizar CAO com Base SAP [Completo]", comparar_fam_sap_cao_completo),
    "14": ("Converter Lista de Corte p/ Cadastro", None),
    "15": ("Converte tabela de comunizado SAP", converter_cmz_sap),
    "16": ("Comparar CAO vs SAP [Ordens, Análise CAO vs SAP, Permit]", comparar_ordens),
    "17": ("Gerar base para fazer o C5", gerar_base_para_c5),
    '18':("Excluir arquivos com base no tamanho",excluir_arq),
    '19':('Extrair derivativos do arquivo EXPORT SAP',extrair_pn),
    "20": ("Gerar Comunização [SAP]. rev.01", cmz),
    "21": ("Adicionar Máquinas na lista de corte", prever),
    "22": ("Análisar e Corrigir tabela de comunização do SAP", analise_comunization),
    "30": ("Sair", "sair")
}


# ============================================================
#                      FUNÇÕES VISUAIS
# ============================================================

def logo():
    os.system("cls" if os.name == "nt" else "clear")
    titulo = text2art("Engineering", font="small")
    rodape = "\nDeveloped by TMG | v1.0 | 2025\n"

    console.print(f"[bold cyan]{titulo}[/bold cyan]")
    for char in rodape:
        print(char, end="", flush=True)
        time.sleep(0.02)
    print()


def exibir_menu():
    console.print(f"[cyan]{'=' * 65}[/cyan]")
    console.print("       [bold yellow]ENGINEERING CUT AND LEAD PREP - MENU[/bold yellow]")
    console.print(f"[cyan]{'=' * 65}[/cyan]")

    for chave, (nome, _) in FERRAMENTAS.items():
        console.print(
            f"[yellow][{int(chave):02d}][/yellow] {nome.upper()} "
            + "-" * (59 - len(nome))
        )

    console.print(f"[cyan]{'=' * 65}[/cyan]")


# ============================================================
#                      LOOP PRINCIPAL
# ============================================================

def executar_opcao(opcao):
    nome, func = FERRAMENTAS[opcao]

    if func == "sair":
        console.print("\n[bold yellow]Saindo do programa...[/bold yellow]\n")
        return False

    if func is None:
        console.print("[bold red]Função ainda não implementada.[/bold red]")
        return True

    try:
        func()
    except Exception as e:
        #console.print(f"[bold red]Erro ao executar '{nome}': {e}[/bold red]")

        logging.error("Erro capturado: %s", e)
        # Imprime o stack trace completo
        traceback.print_exc()
        # Ou registra o stack trace no log
        logging.error("Stack trace:\n%s", traceback.format_exc())


    input("\nAperte ENTER para continuar...")
    return True


def main():
    while True:
        logo()
        exibir_menu()
        opcao = input("\n[?] Escolha uma opção: ").strip()
        try:
            if opcao not in FERRAMENTAS:
                console.print("[bold red]Opção inválida. Tente novamente.[/bold red]\n")
                continue
        except Exception as e:
            console.print(f"[bold red]Err: {e}.[/bold red]\n")

        if not executar_opcao(opcao):
            break


if __name__ == "__main__":
    main()
