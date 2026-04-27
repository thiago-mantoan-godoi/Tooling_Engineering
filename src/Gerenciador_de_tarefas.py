import pandas as pd
from datetime import datetime, timedelta
import os
from rich.console import Console
from rich.table import Table
from typing import Optional

# ============================================================
# CONFIGURAÇÕES GLOBAIS
# ============================================================
ARQUIVO_EXCEL = r"C:\Users\tgodoi01\OneDrive - Lear Corporation\Documents\Atividades.xlsx"  # Salvará no mesmo diretório do script
DIAS_SEMANA = ["segunda", "terça", "quarta", "quinta", "sexta", "sábado", "domingo"]
PRIORIDADES = {"1": "Baixa", "2": "Média", "3": "Alta", "4": "Urgente"}

# Objeto do 'rich' para uma interface bonita no console
console = Console()


# ============================================================
# CLASSE PRINCIPAL DO GERENCIADOR
# ============================================================
class TaskManager:
    """
    Encapsula toda a lógica de gerenciamento de tarefas.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.df = self.carregar_tarefas()
        self.setup_inicial()

    def carregar_tarefas(self) -> pd.DataFrame:
        """Carrega as tarefas do Excel. Se não existir ou estiver inválido, cria um novo."""
        # Adicionamos 'comentario' à lista de colunas
        colunas_esperadas = [
            "nome",
            "descricao",
            "criacao",
            "prazo",
            "status",
            "prioridade",
            "recorrencia_dias",
            "comentario",
        ]

        try:
            df = pd.read_excel(self.filepath)

            if not set(colunas_esperadas).issubset(df.columns):
                raise ValueError("Colunas faltando no arquivo Excel.")

            df["prazo"] = pd.to_datetime(df["prazo"])
            df["criacao"] = pd.to_datetime(df["criacao"])

        except (FileNotFoundError, ValueError, KeyError):
            console.print(
                "[yellow]Arquivo não encontrado ou formato inválido. Criando nova tabela...[/yellow]"
            )
            df = pd.DataFrame(columns=colunas_esperadas)

        return df

    def salvar_tarefas(self):
        """Salva o DataFrame atual no arquivo Excel."""
        self.df.to_excel(self.filepath, index=False)

    def setup_inicial(self):
        """Adiciona tarefas fixas iniciais, se for a primeira execução."""
        if self.df.empty:
            tarefas_fixas = {
                "segunda": ["Fazer report do CAO", "Assinar DocuSign"],
                "terça": ["Cadastro P&A"],
                "quarta": ["Atualizar mapa de alocação do corte"],
                "quinta": ["Comunização"],
                "sexta": ["Estudo de capacidade do corte"],
            }

            hoje = datetime.now()
            for dia, nomes in tarefas_fixas.items():
                for nome in nomes:
                    dia_idx = DIAS_SEMANA.index(dia)
                    dias_ate_prazo = (dia_idx - hoje.weekday() + 7) % 7
                    prazo = hoje + timedelta(days=dias_ate_prazo)
                    prazo = prazo.replace(
                        hour=9, minute=0, second=0
                    )  # Define um horário padrão

                    self.adicionar_tarefa(
                        nome=nome,
                        descricao="Tarefa fixa semanal.",
                        prazo=prazo,
                        prioridade="Alta",
                        recorrencia_dias=7,  # Recorrência semanal
                        salvar=False,  # Salva apenas no final
                    )
            self.salvar_tarefas()
            console.print(
                "[bold green]Tarefas fixas iniciais configuradas![/bold green]"
            )

    # SUBSTITUA ESTE MÉTODO NO SEU CÓDIGO
    def adicionar_tarefa(
        self,
        nome: str,
        descricao: str,
        prazo: datetime,
        prioridade: str,
        recorrencia_dias: int,
        salvar: bool = True,
    ):
        """Adiciona uma nova tarefa ao DataFrame."""
        nova_tarefa = {
            "nome": nome,
            "descricao": descricao,
            "criacao": datetime.now(),
            "prazo": prazo,
            "status": "Pendente",
            "prioridade": prioridade,
            "recorrencia_dias": recorrencia_dias,
            "comentario": "",  # Inicializa o comentário como vazio
        }
        self.df = pd.concat([self.df, pd.DataFrame([nova_tarefa])], ignore_index=True)
        if salvar:
            self.salvar_tarefas()

    # SUBSTITUA ESTE MÉTODO NO SEU CÓDIGO
    def concluir_tarefa(self, index: int):
        """Marca uma tarefa como concluída. Se for recorrente, reagenda."""
        if index not in self.df.index:
            console.print("[bold red]Erro: Índice inválido![/bold red]")
            return

        # Pede o comentário ANTES de processar a conclusão
        comentario = console.input("Adicionar um comentário de conclusão (opcional): ")
        self.df.at[index, "comentario"] = comentario

        recorrencia = self.df.at[index, "recorrencia_dias"]
        nome_tarefa = self.df.at[index, "nome"]

        if pd.notna(recorrencia) and recorrencia > 0:
            # Tarefa recorrente: avança o prazo e mantém pendente
            prazo_antigo = self.df.at[index, "prazo"]
            novo_prazo = prazo_antigo + timedelta(days=int(recorrencia))
            self.df.at[index, "prazo"] = novo_prazo
            self.df.at[index, "status"] = "Pendente"
            console.print(
                f"[bold green]Tarefa recorrente '{nome_tarefa}' concluída e reagendada para {novo_prazo.strftime('%d/%m/%Y %H:%M')}.[/bold green]"
            )
        else:
            # Tarefa não recorrente: muda o status para 'Concluída'
            self.df.at[index, "status"] = "Concluída"
            console.print(
                f"[bold blue]Tarefa '{nome_tarefa}' concluída e arquivada![/bold blue]"
            )

        # Não precisamos mais do reset_index, pois não estamos mais usando .drop
        self.salvar_tarefas()

    # SUBSTITUA ESTE MÉTODO NO SEU CÓDIGO
    def exibir_tarefas(self, filtro_status: Optional[str] = None):
        """Exibe as tarefas em uma tabela formatada."""
        df_filtrado = self.df.copy()
        if filtro_status:
            df_filtrado = df_filtrado[
                df_filtrado["status"].str.lower() == filtro_status.lower()
            ]

        if df_filtrado.empty:
            console.print(
                "\n[yellow]Nenhuma tarefa encontrada com os critérios atuais.[/yellow]\n"
            )
            return

        # Ordena por prazo
        df_filtrado.sort_values(by="prazo", inplace=True)

        tabela = Table(
            title="Painel de Tarefas", show_header=True, header_style="bold magenta"
        )
        tabela.add_column("ID", style="dim", width=3)
        tabela.add_column("Nome da Tarefa", min_width=20)
        tabela.add_column("Prazo", width=16)
        tabela.add_column("Prioridade", width=10)
        tabela.add_column("Status", width=10)
        tabela.add_column("Dias Restantes", width=15)
        tabela.add_column("Comentário", min_width=20)  # Nova coluna na exibição

        hoje = datetime.now()

        for index, row in df_filtrado.iterrows():
            prazo = row["prazo"]
            delta = prazo - hoje
            dias_restantes = delta.days

            # Formatação baseada no prazo
            cor_prazo = "white"
            if row["status"] == "Pendente":
                if dias_restantes < 0:
                    cor_prazo = "red"
                    texto_dias = f"[bold {cor_prazo}]Atrasada {-dias_restantes} dia(s)[/bold {cor_prazo}]"
                elif dias_restantes == 0:
                    cor_prazo = "yellow"
                    texto_dias = f"[bold {cor_prazo}]Termina Hoje![/bold {cor_prazo}]"
                else:
                    texto_dias = f"{dias_restantes} dia(s)"
            else:
                texto_dias = "---"  # Não mostra dias restantes para tarefas concluídas

            # Formatação baseada na prioridade
            prioridade = row["prioridade"]
            if prioridade == "Urgente":
                cor_prioridade = "on red"
            elif prioridade == "Alta":
                cor_prioridade = "red"
            elif prioridade == "Média":
                cor_prioridade = "yellow"
            else:
                cor_prioridade = "green"

            # Formatação do Status
            status = row["status"]
            cor_status = "cyan" if status == "Pendente" else "green"

            # Pega o comentário, garantindo que seja uma string
            comentario = str(row.get("comentario", ""))

            tabela.add_row(
                str(index),
                row["nome"],
                f"[{cor_prazo}]{prazo.strftime('%d/%m/%Y %H:%M')}[/{cor_prazo}]",
                f"[{cor_prioridade}]{prioridade}[/{cor_prioridade}]",
                f"[{cor_status}]{status}[/{cor_status}]",
                texto_dias,
                comentario,  # Adiciona o comentário na linha da tabela
            )

        console.print(tabela)


# ============================================================
# FUNÇÕES DE INTERFACE (MENU)
# ============================================================
def menu_adicionar_tarefa(manager: TaskManager):
    """Coleta os dados do usuário para adicionar uma nova tarefa."""
    console.print("\n--- [bold]Adicionar Nova Tarefa[/bold] ---")
    nome = console.input("Nome da tarefa: ")
    descricao = console.input("Descrição (opcional): ")

    while True:
        try:
            prazo_str = console.input("Prazo (formato DD/MM/AAAA HH:MM): ")
            prazo = datetime.strptime(prazo_str, "%d/%m/%Y %H:%M")
            break
        except ValueError:
            console.print("[red]Formato de data inválido. Tente novamente.[/red]")

    console.print("Escolha a prioridade:")
    for key, value in PRIORIDADES.items():
        console.print(f"  {key} - {value}")

    while True:
        prioridade_key = console.input(
            f"Digite o número da prioridade (1-{len(PRIORIDADES)}): "
        )
        if prioridade_key in PRIORIDADES:
            prioridade = PRIORIDADES[prioridade_key]
            break
        else:
            console.print("[red]Opção inválida.[/red]")

    while True:
        try:
            recorrencia = int(
                console.input(
                    "Recorrência em dias (0 para tarefa única, 7 para semanal, etc.): "
                )
            )
            break
        except ValueError:
            console.print("[red]Por favor, digite um número.[/red]")

    manager.adicionar_tarefa(nome, descricao, prazo, prioridade, recorrencia)
    console.print(
        f"\n[bold green]Tarefa '{nome}' adicionada com sucesso![/bold green]\n"
    )


def menu_concluir_tarefa(manager: TaskManager):
    """Coleta o índice da tarefa a ser concluída."""
    console.print("\n--- [bold]Concluir Tarefa[/bold] ---")
    manager.exibir_tarefas("pendente")
    try:
        index_str = console.input("Digite o ID da tarefa a ser concluída: ")
        manager.concluir_tarefa(int(index_str))
    except (ValueError, IndexError):
        console.print(
            "[red]Entrada inválida. Por favor, digite um número de ID válido.[/red]"
        )


# ============================================================
# LOOP PRINCIPAL
# ============================================================
def main():
    """Função principal que executa o menu."""
    manager = TaskManager(ARQUIVO_EXCEL)

    while True:
        console.print(
            "\n✨ --- [bold cyan]Gerenciador de Atividades [/bold cyan] --- ✨"
        )
        console.print("1 - [green]Ver todas as tarefas pendentes[/green]")
        console.print("2 - [blue]Adicionar nova tarefa[/blue]")
        console.print("3 - [magenta]Concluir uma tarefa[/magenta]")
        console.print("4 - [yellow]Ver todas as tarefas (incluindo futuras)[/yellow]")
        console.print("5 - [red]Sair[/red]")

        opcao = console.input("\nEscolha uma opção: ")
        os.system("cls")

        if opcao == "1":
            manager.exibir_tarefas("pendente")
        elif opcao == "2":
            menu_adicionar_tarefa(manager)
        elif opcao == "3":
            menu_concluir_tarefa(manager)
        elif opcao == "4":
            manager.exibir_tarefas()
        elif opcao == "5":
            console.print("\n[bold]Até logo![/bold] 👋\n")
            break
        else:
            console.print("[bold red]Opção inválida! Tente novamente.[/bold red]")


if __name__ == "__main__":
    main()
