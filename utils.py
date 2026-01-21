"""
Módulo utilitário com funções genéricas para pipelines Avenue Dashboard.
Contém funções para carregamento de dados, processamento e salvamento.
"""

import os
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta


def carregar_clientes_prunus(arquivo: str = "prunus_list.txt") -> List[str]:
    """
    Carrega lista de clientes do arquivo prunus_list.txt.

    Args:
        arquivo: Caminho do arquivo com a lista de clientes

    Returns:
        Lista com nomes dos clientes (em minúsculas para comparação)
    """
    clientes = []
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                cliente = linha.strip()
                if cliente:  # Ignora linhas vazias
                    clientes.append(cliente.lower())
        print(f"✓ Carregados {len(clientes)} clientes de {arquivo}")
        return clientes
    except FileNotFoundError:
        print(f"⚠ Arquivo {arquivo} não encontrado!")
        return []


def carregar_mapeamento_banker(arquivo: str = "banker_list.txt") -> Dict[str, str]:
    """
    Carrega mapeamento de clientes para bankers do arquivo banker_list.txt.

    Args:
        arquivo: Caminho do arquivo CSV com Cliente,Banker

    Returns:
        Dicionário com cliente (minúsculo) -> banker
    """
    mapeamento = {}
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            next(f)  # Pular cabeçalho
            for linha in f:
                partes = linha.strip().split(",")
                if len(partes) == 2:
                    cliente, banker = partes
                    mapeamento[cliente.strip().lower()] = banker.strip()
        print(f"✓ Carregado mapeamento para {len(mapeamento)} clientes de {arquivo}")
        return mapeamento
    except FileNotFoundError:
        print(f"⚠ Arquivo {arquivo} não encontrado!")
        return {}


def gerar_datas_diarias(data_inicio: str, data_fim: str = None) -> List[str]:
    """
    Gera lista de datas diariamente a partir de data_inicio até data_fim (ou hoje).

    Args:
        data_inicio: Data inicial no formato YYYY-MM-DD
        data_fim: Data final no formato YYYY-MM-DD (padrão: hoje)

    Returns:
        Lista de datas em formato YYYY-MM-DD
    """
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    
    if data_fim:
        fim = datetime.strptime(data_fim, "%Y-%m-%d")
    else:
        fim = datetime.now()

    datas = []
    data_atual = inicio

    while data_atual <= fim:
        datas.append(data_atual.strftime("%Y-%m-%d"))
        data_atual += timedelta(days=1)

    return datas


def salvar_banco_dados(
    df: pd.DataFrame,
    prefixo: str = "evolucao_pl_diaria",
    diretorio_base: str = "data/PL"
) -> None:
    """
    Salva o DataFrame em múltiplos formatos (CSV, JSON e Excel) em subdiretórios organizados.

    Args:
        df: DataFrame a ser salvo
        prefixo: Prefixo para o nome dos arquivos
        diretorio_base: Diretório base para salvar os arquivos (padrão: data/PL)
    """
    # Criar estrutura de diretórios
    dir_csv = os.path.join(diretorio_base, "csv")
    dir_json = os.path.join(diretorio_base, "json")
    dir_excel = os.path.join(diretorio_base, "excel")
    
    os.makedirs(dir_csv, exist_ok=True)
    os.makedirs(dir_json, exist_ok=True)
    os.makedirs(dir_excel, exist_ok=True)

    # Salvar como CSV
    csv_path = os.path.join(dir_csv, f"{prefixo}.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n✓ Dados salvos em: {csv_path}")

    # Salvar como JSON
    json_path = os.path.join(dir_json, f"{prefixo}.json")
    df_json = df.reset_index() if df.index.name else df.copy()
    df_json.to_json(json_path, orient="records", indent=2, force_ascii=False)
    print(f"✓ Dados salvos em: {json_path}")

    # Salvar como Excel (se openpyxl estiver disponível)
    try:
        excel_path = os.path.join(dir_excel, f"{prefixo}.xlsx")
        df.to_excel(excel_path, sheet_name="Evolução PL")
        print(f"✓ Dados salvos em: {excel_path}")
    except ImportError:
        print("(openpyxl não instalado, pulando Excel)")


def pivotar_dados(
    resultados: List[Dict],
    indice: List[str],
    colunas: str,
    valores: str
) -> pd.DataFrame:
    """
    Cria DataFrame pivotado a partir de uma lista de resultados.

    Args:
        resultados: Lista de dicionários com os dados
        indice: Lista de colunas para usar como índice
        colunas: Coluna para pivotar como colunas
        valores: Coluna com os valores a agregar

    Returns:
        DataFrame pivotado com colunas ordenadas
    """
    df = pd.DataFrame(resultados)

    if df.empty:
        return df

    # Pivotar dados
    df_pivot = df.pivot_table(
        index=indice,
        columns=colunas,
        values=valores,
        aggfunc="first"
    ).reset_index()

    # Reordenar colunas de data
    colunas_data = sorted(
        [col for col in df_pivot.columns if col not in indice]
    )
    df_pivot = df_pivot[indice + colunas_data]

    return df_pivot
