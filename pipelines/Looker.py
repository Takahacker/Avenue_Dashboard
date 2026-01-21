import os
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict

LOOKER_BASE_URL = "https://avenueanalytics.cloud.looker.com:19999"
ENDPOINT = "/api/4.0/queries/run/json"

ACCESS_TOKEN = os.getenv("LOOKER_ACCESS_TOKEN")
if not ACCESS_TOKEN:
    raise RuntimeError("LOOKER_ACCESS_TOKEN não definido")


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


def gerar_datas_semanais(data_inicio: str = "2025-04-23") -> List[str]:
    """
    Gera lista de datas de 7 em 7 dias a partir de data_inicio até hoje.

    Args:
        data_inicio: Data inicial no formato YYYY-MM-DD

    Returns:
        Lista de datas em formato YYYY-MM-DD
    """
    inicio = datetime.strptime(data_inicio, "%Y-%m-%d")
    hoje = datetime.now()

    datas = []
    data_atual = inicio

    while data_atual <= hoje:
        datas.append(data_atual.strftime("%Y-%m-%d"))
        data_atual += timedelta(days=7)

    return datas


def fetch_dados_looker(data: str) -> List[Dict]:
    """
    Faz requisição ao Looker para uma data específica.

    Args:
        data: Data no formato YYYY-MM-DD

    Returns:
        Lista de registros retornados pela API
    """
    payload = {
        "model": "avenue_b2b_office_api",
        "view": "auc",
        "fields": [
            "auc.date",
            "auc.client_name",
            "auc.client_cpf",
            "auc.product_name",
            "auc.auc_usd",
        ],
        "filters": {"auc.date": data},
    }

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        resp = requests.post(
            f"{LOOKER_BASE_URL}{ENDPOINT}", headers=headers, json=payload, timeout=60
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar dados para {data}: {e}")
        return []


def processar_dados(datas: List[str], clientes_prunus: List[str]) -> pd.DataFrame:
    """
    Processa dados semanais e cria DataFrame pivotado com soma de auc_usd por cliente por semana.

    Args:
        datas: Lista de datas a processar
        clientes_prunus: Lista de clientes da Prunus para filtrar

    Returns:
        DataFrame com clientes nas linhas e datas nas colunas
    """
    resultados = []

    for i, data in enumerate(datas, 1):
        print(f"Processando semana {i}/{len(datas)} - Data: {data}")

        dados = fetch_dados_looker(data)

        if not dados:
            print(f"  Nenhum dado retornado para {data}")
            continue

        # Filtrar e agrupar por cliente (client_name e client_cpf)
        clientes = {}

        for registro in dados:
            # Pular "Balance US Banking"
            produto = registro.get("auc.product_name", "")
            if produto == "Balance US Banking":
                continue

            cliente_name = registro.get("auc.client_name", "")

            # Verificar se cliente está na lista Prunus (case-insensitive)
            if cliente_name.lower() not in clientes_prunus:
                continue

            cliente_key = (cliente_name, registro.get("auc.client_cpf"))
            auc_usd = float(registro.get("auc.auc_usd", 0))

            if cliente_key not in clientes:
                clientes[cliente_key] = 0

            clientes[cliente_key] += auc_usd

        # Adicionar resultados
        for (nome_cliente, cpf_cliente), soma_usd in clientes.items():
            resultados.append(
                {
                    "Cliente": nome_cliente,
                    "CPF": cpf_cliente,
                    "Data": data,
                    "Soma_USD": soma_usd if soma_usd > 0 else None,
                }
            )

        print(f"  {len(clientes)} clientes Prunus processados")

    # Criar DataFrame
    df = pd.DataFrame(resultados)

    if df.empty:
        return df

    # Pivotar: Cliente x Data
    df_pivot = df.pivot_table(
        index=["Cliente", "CPF"], columns="Data", values="Soma_USD", aggfunc="first"
    ).reset_index()

    # Reordenar colunas de data
    colunas_data = sorted(
        [col for col in df_pivot.columns if col not in ["Cliente", "CPF"]]
    )
    df_pivot = df_pivot[["Cliente", "CPF"] + colunas_data]

    return df_pivot


def salvar_banco_dados(df: pd.DataFrame):
    """
    Salva o DataFrame em múltiplos formatos (CSV e JSON).

    Args:
        df: DataFrame a ser salvo
    """
    os.makedirs("data", exist_ok=True)

    # Salvar como CSV
    csv_path = "data/evolucao_pl_semanal.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n✓ Dados salvos em: {csv_path}")

    # Salvar como JSON
    json_path = "data/evolucao_pl_semanal.json"
    df_json = df.reset_index() if df.index.name else df.copy()
    df_json.to_json(json_path, orient="records", indent=2, force_ascii=False)
    print(f"✓ Dados salvos em: {json_path}")

    # Salvar como Excel (se openpyxl estiver disponível)
    try:
        excel_path = "data/evolucao_pl_semanal.xlsx"
        df.to_excel(excel_path, sheet_name="Evolução PL")
        print(f"✓ Dados salvos em: {excel_path}")
    except ImportError:
        print("(openpyxl não instalado, pulando Excel)")


def main():
    """Função principal"""
    print("=" * 60)
    print("EVOLUÇÃO DE P&L SEMANAL - AVENUE (CLIENTES PRUNUS)")
    print("=" * 60)

    # Carregar clientes Prunus
    print("\n1. Carregando lista de clientes Prunus...")
    clientes_prunus = carregar_clientes_prunus("prunus_list.txt")

    if not clientes_prunus:
        print("⚠ Nenhum cliente Prunus carregado!")
        return

    # Gerar datas semanais
    print("\n2. Gerando datas semanais de 23/04/2025 até hoje...")
    datas = gerar_datas_semanais("2025-04-23")
    print(f"   Total de semanas: {len(datas)}")
    print(f"   Período: {datas[0]} a {datas[-1]}")

    # Processar dados
    print("\n3. Puxando dados do Looker (excluindo Balance US Banking)...")
    df = processar_dados(datas, clientes_prunus)

    if df.empty:
        print("\n⚠ Nenhum dado foi retornado!")
        return

    # Exibir resumo
    print("\n4. Resumo dos dados:")
    print(f"   Total de clientes: {len(df)}")
    print(
        f"   Total de semanas: {len([col for col in df.columns if col not in ['Cliente', 'CPF']])}"
    )

    # Salvar banco de dados
    print("\n5. Salvando banco de dados...")
    salvar_banco_dados(df)

    # Exibir amostra
    print("\n6. Primeiras linhas dos dados:")
    print(df.head(10).to_string(index=False))

    print("\n" + "=" * 60)
    print("✓ Processo concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
