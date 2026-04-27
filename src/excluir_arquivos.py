
import os

def listar_arquivos_por_tamanho(diretorio):
    arquivos = []
    for root, _, files in os.walk(diretorio):
        for file in files:
            caminho = os.path.join(root, file)
            try:
                tamanho = os.path.getsize(caminho)  # tamanho em bytes
                arquivos.append((caminho, tamanho))
            except Exception as e:
                print(f"Erro ao acessar {caminho}: {e}")
    # Ordena do maior para o menor
    arquivos.sort(key=lambda x: x[1], reverse=True)
    return arquivos

def excluir_arquivos_maiores(arquivos, limite_mb):
    limite_bytes = limite_mb * 1024 * 1024
    excluidos = []
    for caminho, tamanho in arquivos:
        if tamanho >= limite_bytes:
            try:
                os.remove(caminho)
                excluidos.append((caminho, tamanho))
                print(f"Excluído: {caminho} ({tamanho / (1024*1024):.2f} MB)")
            except Exception as e:
                print(f"Erro ao excluir {caminho}: {e}")
    return excluidos

def  excluir_arq():
    diretorio = input("Informe o caminho do diretório: ").strip()
    arquivos = listar_arquivos_por_tamanho(diretorio)

    print("\nArquivos encontrados (Top 10):")
    for i, (caminho, tamanho) in enumerate(arquivos[:10], start=1):
        print(f"{i}. {caminho} - {tamanho / (1024*1024):.2f} MB")

    limite_mb = float(input("\nExcluir arquivos maiores que (MB): ").strip())
    excluir_arquivos_maiores(arquivos, limite_mb)

if __name__ == "__main__":
    excluir_arq()


