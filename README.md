Este projeto é uma **Central de Automação (CLI)** robusta voltada para a engenharia de **Corte e Lead Prep** (preparação de fios e terminais). Ele funciona como um "canivete suíço" para analistas e engenheiros, consolidando diversas ferramentas de processamento de dados, integração com SAP e gestão de sistemas CAO em uma única interface de linha de comando.

Abaixo está uma proposta de **README.md** profissional para o seu repositório:

---

# 🛠️ Engineering Cut & Lead Prep - Toolbox

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/Status-v1.0-green.svg)
![Build](https://img.shields.io/badge/Interface-CLI-yellow.svg)

O **Engineering Toolbox** é uma aplicação de terminal desenvolvida para automatizar tarefas repetitivas e complexas no setor de engenharia industrial. O foco principal é o processamento de listas de corte, comparação de dados SAP vs. CAO e a automação de fluxos de trabalho de produção.

## 🚀 Principais Funcionalidades

A ferramenta está dividida em 22 módulos operacionais, incluindo:

*   **Integração SAP:** Conversão de arquivos exportados do SAP, extração de derivativos e análise de tabelas de comunização.
*   **Gestão CAO:** Cadastro de ordens, atualização de bases e comparação detalhada entre o Master Data e o SAP.
*   **Automação de E-mail:** Extração automática de anexos de e-mails para resposta de solicitações (CR).
*   **Processamento de Dados:** Consolidação de arquivos de corte (Cuts), conversão de CSVs e geração de bases para o sistema C5.
*   **Inteligência de Produção:** Adição automática de máquinas em listas de corte e análise de comunização (Rev.01).
*   **Manutenção:** Rotinas de limpeza total do sistema e exclusão inteligente de arquivos por tamanho.

## 🛠️ Tecnologias Utilizadas

*   **[Rich](https://github.com/Textualize/rich):** Interface de usuário rica e colorida no terminal.
*   **[Art](https://github.com/sepandhaghighi/art):** Geração de ASCII Art para branding da ferramenta.
*   **[Logging](https://docs.python.org/3/library/logging.html):** Sistema de rastreamento de erros com geração de arquivo `app.log`.
*   **[Traceback](https://docs.python.org/3/library/traceback.html):** Diagnóstico detalhado de exceções para depuração.

## 📁 Estrutura de Pastas

```text
PROJETO/
├── main.py             # Script principal (Menu e Loop)
├── app.log             # Registro de erros e operações
├── src/                # Módulos de funções específicas (Business Logic)
│   ├── extrair_cuts.py
│   ├── convert_SAP.py
│   ├── comparar_CAO_SAP.py
│   └── ... (demais módulos)
└── requirements.txt    # Dependências do projeto
```

## ⚙️ Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/engineering-toolbox.git
    cd engineering-toolbox
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o programa:**
    ```bash
    python main.py
    ```

## 📖 Como Usar

Ao iniciar, você verá um menu numerado. Basta digitar o número da ferramenta desejada e seguir as instruções no console:

1.  **Opção 01-03:** Focadas em arquivos de corte e circuitos.
2.  **Opção 04 & 08:** Gestão de CRs e leitura de e-mails.
3.  **Opção 06, 07, 11, 15, 20:** Ferramentas dedicadas ao ambiente SAP.
4.  **Opção 10, 12, 13, 16:** Sincronização e auditoria entre sistemas CAO e SAP.
5.  **Opção 21:** Inteligência para previsão de máquinas.

## 🪵 Logs e Diagnóstico

O sistema gera automaticamente um arquivo `app.log` no diretório raiz. Caso ocorra um erro inesperado em qualquer função, o log registrará o **Stack Trace** completo, permitindo que a equipe de desenvolvimento identifique a falha rapidamente.

## 👤 Desenvolvedor

*   **Autor:** TMG
*   **Versão:** 1.0
*   **Ano:** 2025

---
*Aviso: Algumas funções dependem de acesso a servidores internos e permissões específicas de sistema.*