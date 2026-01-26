import os
import json
import requests
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict
import sys

# Adicionar diretório pai ao path para importar utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    carregar_clientes_prunus,
    carregar_mapeamento_banker,
    gerar_datas_diarias,
    salvar_banco_dados,
    pivotar_dados,
)

LOOKER_BASE_URL = "https://avenueanalytics.cloud.looker.com"
LOGIN_ENDPOINT = "/api/4.0/login"
QUERY_ENDPOINT = "/api/4.0/queries/run/json"

CLIENT_ID = os.getenv("LOOKER_CLIENT_ID")
CLIENT_SECRET = os.getenv("LOOKER_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("LOOKER_CLIENT_ID e LOOKER_CLIENT_SECRET não definidos")

# Token de acesso será obtido dinamicamente
ACCESS_TOKEN = None


def autenticar_looker() -> str:
    """
    Autentica com a API Looker usando OAuth2 (client_id e client_secret).

    Returns:
        Token de acesso para usar nas requisições
    """
    global ACCESS_TOKEN

    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    try:
        resp = requests.post(
            f"{LOOKER_BASE_URL}{LOGIN_ENDPOINT}",
            data=payload,
            headers=headers,
            timeout=30,
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            raise RuntimeError("Token de acesso não retornado pela API Looker")
        ACCESS_TOKEN = token
        print(f"✓ Autenticação bem-sucedida. Token válido.")
        return token
    except Exception as e:
        raise RuntimeError(f"Erro ao autenticar com Looker: {e}")


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
        "Authorization": f"token {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        resp = requests.post(
            f"{LOOKER_BASE_URL}{QUERY_ENDPOINT}",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar dados para {data}: {e}")
        return []


def processar_dados(
    datas: List[str], clientes_prunus: List[str], mapeamento_banker: Dict[str, str]
) -> pd.DataFrame:
    """
    Processa dados diários e cria DataFrame pivotado com soma de auc_usd por cliente por dia.

    Args:
        datas: Lista de datas a processar
        clientes_prunus: Lista de clientes da Prunus para filtrar
        mapeamento_banker: Dicionário cliente -> banker

    Returns:
        DataFrame com clientes nas linhas e datas nas colunas
    """
    resultados = []

    for i, data in enumerate(datas, 1):
        print(f"Processando dia {i}/{len(datas)} - Data: {data}")

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
            banker = mapeamento_banker.get(nome_cliente.lower(), "Desconhecido")
            resultados.append(
                {
                    "Cliente": nome_cliente,
                    "CPF": cpf_cliente,
                    "Banker": banker,
                    "Data": data,
                    "Soma_USD": soma_usd if soma_usd > 0 else None,
                }
            )

        print(f"  {len(clientes)} clientes Prunus processados")

    # Usar função de pivot genérica do utils
    df_pivot = pivotar_dados(
        resultados,
        indice=["Cliente", "CPF", "Banker"],
        colunas="Data",
        valores="Soma_USD",
    )

    return df_pivot


def salvar_banco_dados(df: pd.DataFrame):
    """
    Salva o DataFrame em múltiplos formatos (CSV e JSON).

    Args:
        df: DataFrame a ser salvo
    """
    from utils import salvar_banco_dados as save_data

    save_data(df, prefixo="evolucao_pl_diaria")


def main():
    """Função principal"""
    print("=" * 60)
    print("EVOLUÇÃO DE P&L DIÁRIA - AVENUE (CLIENTES PRUNUS)")
    print("=" * 60)

    # Autenticar com Looker
    print("\n1. Autenticando com API Looker...")
    try:
        token = autenticar_looker()
    except Exception as e:
        print(f"✗ Falha na autenticação: {e}")
        return

    # Carregar clientes Prunus
    print("\n2. Carregando lista de clientes Prunus...")
    clientes_prunus = carregar_clientes_prunus("prunus_list.txt")

    if not clientes_prunus:
        print("⚠ Nenhum cliente Prunus carregado!")
        return

    # Carregar mapeamento Banker
    print("\n3. Carregando mapeamento de Bankers...")
    mapeamento_banker = carregar_mapeamento_banker("banker_list.txt")

    # Gerar datas diárias
    print("\n4. Gerando datas diárias de 01/11/2025 até hoje...")
    datas = gerar_datas_diarias("2025-11-01")
    print(f"   Total de dias: {len(datas)}")
    print(f"   Período: {datas[0]} a {datas[-1]}")

    # Processar dados
    print("\n5. Puxando dados do Looker (excluindo Balance US Banking)...")
    df = processar_dados(datas, clientes_prunus, mapeamento_banker)

    if df.empty:
        print("\n⚠ Nenhum dado foi retornado!")
        return

    # Exibir resumo
    print("\n6. Resumo dos dados:")
    print(f"   Total de clientes: {len(df)}")
    print(
        f"   Total de dias: {len([col for col in df.columns if col not in ['Cliente', 'CPF', 'Banker']])}"
    )

    # Salvar banco de dados
    print("\n7. Salvando banco de dados...")
    salvar_banco_dados(df)

    # Exibir amostra
    print("\n8. Primeiras linhas dos dados:")
    print(df.head(10).to_string(index=False))

    print("\n" + "=" * 60)
    print("✓ Processo concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
