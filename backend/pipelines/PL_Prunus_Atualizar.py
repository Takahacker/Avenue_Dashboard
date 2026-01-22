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


def carregar_dados_historicos(
    caminho_arquivo: str = "data/PL/json/evolucao_pl_diaria.json",
) -> pd.DataFrame:
    """
    Carrega dados históricos do arquivo JSON.

    Args:
        caminho_arquivo: Caminho do arquivo JSON com dados históricos

    Returns:
        DataFrame com dados históricos ou DataFrame vazio se arquivo não existir
    """
    if not os.path.exists(caminho_arquivo):
        print(f"⚠ Arquivo histórico não encontrado em: {caminho_arquivo}")
        return pd.DataFrame()

    try:
        df = pd.read_json(caminho_arquivo, orient="records")
        print(f"✓ Carregados dados históricos de {len(df)} linhas")
        return df
    except Exception as e:
        print(f"✗ Erro ao carregar dados históricos: {e}")
        return pd.DataFrame()


def obter_ultima_data_registrada(df: pd.DataFrame) -> str:
    """
    Identifica a última data registrada nos dados históricos.

    Args:
        df: DataFrame com dados históricos

    Returns:
        Data da última linha em formato YYYY-MM-DD
    """
    if df.empty:
        return None

    # Encontrar todas as colunas de data (excluindo Cliente, CPF, Banker)
    colunas_data = [
        col for col in df.columns if col not in ["Cliente", "CPF", "Banker"]
    ]

    if colunas_data:
        # Ordenar as colunas de data e pegar a última
        ultima_data = sorted(colunas_data)[-1]
        print(f"✓ Última data registrada: {ultima_data}")
        return ultima_data

    return None


def processar_dados_incrementais(
    datas: List[str], clientes_prunus: List[str], mapeamento_banker: Dict[str, str]
) -> pd.DataFrame:
    """
    Processa dados diários novos e cria DataFrame pivotado.

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


def mesclar_dados(df_historico: pd.DataFrame, df_novo: pd.DataFrame) -> pd.DataFrame:
    """
    Mescla dados históricos com dados novos, evitando duplicatas.

    Args:
        df_historico: DataFrame com dados históricos
        df_novo: DataFrame com dados novos

    Returns:
        DataFrame mesclado com dados combinados
    """
    if df_historico.empty:
        print("✓ Nenhum dado histórico, usando apenas dados novos")
        return df_novo

    if df_novo.empty:
        print("✓ Nenhum dado novo, usando apenas dados históricos")
        return df_historico

    # Identificar colunas de índice (Cliente, CPF, Banker)
    colunas_indice = ["Cliente", "CPF", "Banker"]

    # Identificar colunas de data em ambos os DataFrames
    colunas_data_hist = sorted(
        [col for col in df_historico.columns if col not in colunas_indice]
    )
    colunas_data_novo = sorted(
        [col for col in df_novo.columns if col not in colunas_indice]
    )

    # Reordenar e combinar
    df_combinado = df_historico.copy()

    # Adicionar colunas novas que não estão no histórico
    for col in colunas_data_novo:
        if col not in df_combinado.columns:
            df_combinado[col] = None

    # Fazer merge dos dados novos
    for _, row in df_novo.iterrows():
        cliente = row["Cliente"]
        cpf = row["CPF"]

        # Procurar cliente no histórico
        mask = (df_combinado["Cliente"] == cliente) & (df_combinado["CPF"] == cpf)

        if mask.any():
            # Cliente já existe, atualizar colunas de data
            idx = df_combinado[mask].index[0]
            for col in colunas_data_novo:
                df_combinado.at[idx, col] = row.get(col)
        else:
            # Cliente novo, adicionar como nova linha
            df_combinado = pd.concat(
                [df_combinado, pd.DataFrame([row])], ignore_index=True
            )

    # Reordenar colunas
    colunas_ordenadas = colunas_indice + sorted(
        [col for col in df_combinado.columns if col not in colunas_indice]
    )
    df_combinado = df_combinado[colunas_ordenadas]

    print(f"✓ Dados mesclados: {len(df_combinado)} clientes únicos")
    return df_combinado


def main():
    """Função principal"""
    print("=" * 60)
    print("ATUALIZAÇÃO INCREMENTAL DE P&L DIÁRIA - AVENUE (CLIENTES PRUNUS)")
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

    # Carregar dados históricos
    print("\n4. Carregando dados históricos...")
    df_historico = carregar_dados_historicos()

    # Determinar datas a processar
    print("\n5. Determinando datas a processar...")
    if df_historico.empty:
        # Se não houver histórico, começar de uma data inicial
        data_inicio = "2025-12-01"
        print(f"   Nenhum histórico encontrado. Começando de {data_inicio}")
    else:
        ultima_data = obter_ultima_data_registrada(df_historico)
        if ultima_data:
            # Processar a partir do dia seguinte à última data
            data_inicio_dt = datetime.strptime(ultima_data, "%Y-%m-%d") + timedelta(
                days=1
            )
            data_inicio = data_inicio_dt.strftime("%Y-%m-%d")
            print(f"   Continuando de {data_inicio}")
        else:
            data_inicio = "2025-12-01"
            print(
                f"   Não foi possível determinar última data. Começando de {data_inicio}"
            )

    # Gerar datas diárias
    datas = gerar_datas_diarias(data_inicio)
    print(f"   Total de dias para processar: {len(datas)}")

    if len(datas) == 0:
        print("✓ Já existem dados até hoje. Nenhuma atualização necessária.")
        return

    print(f"   Período: {datas[0]} a {datas[-1]}")

    # Processar dados novos
    print("\n6. Puxando dados novos do Looker (excluindo Balance US Banking)...")
    df_novo = processar_dados_incrementais(datas, clientes_prunus, mapeamento_banker)

    # Mesclar dados
    print("\n7. Mesclando dados históricos com novos...")
    df_final = mesclar_dados(df_historico, df_novo)

    if df_final.empty:
        print("\n⚠ Nenhum dado foi retornado!")
        return

    # Exibir resumo
    print("\n8. Resumo dos dados finais:")
    print(f"   Total de clientes: {len(df_final)}")
    print(
        f"   Total de dias: {len([col for col in df_final.columns if col not in ['Cliente', 'CPF', 'Banker']])}"
    )

    # Salvar banco de dados
    print("\n9. Salvando banco de dados atualizado...")
    salvar_banco_dados(df_final, prefixo="evolucao_pl_diaria")

    # Exibir amostra
    print("\n10. Primeiras linhas dos dados finais:")
    print(df_final.head(10).to_string(index=False))

    print("\n" + "=" * 60)
    print("✓ Atualização concluída com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
