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
            timeout=53
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


def fetch_net_inflow_looker(filtro: str = "last 53 days") -> List[Dict]:
    """
    Faz requisição ao Looker para net_inflow.

    Args:
        filtro: Filtro de data (padrão: últimos 53 dias)

    Returns:
        Lista de registros retornados pela API
    """
    payload = {
        "model": "avenue_b2b_office_api",
        "view": "net_inflow",
        "fields": [
            "net_inflow.date",
            "net_inflow.created_date",
            "net_inflow.settlement_date",
            "net_inflow.client_cpf",
            "net_inflow.client_email",
            "net_inflow.client_name",
            "net_inflow.foreign_finder_email",
            "net_inflow.foreign_finder_code",
            "net_inflow.foreign_finder_name",
            "net_inflow.office_cnpj",
            "net_inflow.office_name",
            "net_inflow.kind",
            "net_inflow.description",
            "net_inflow.product_cusip",
            "net_inflow.product_name",
            "net_inflow.product_type",
            "net_inflow.product_symbol",
            "net_inflow.net_inflow_brl",
            "net_inflow.net_inflow_usd"
        ],
        "filters": {"net_inflow.date": filtro},
    }

    headers = {
        "Authorization": f"token {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        resp = requests.post(
            f"{LOOKER_BASE_URL}{QUERY_ENDPOINT}", headers=headers, json=payload, timeout=120
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar dados de net_inflow: {e}")
        return []


def processar_net_inflow(dados: List[Dict], clientes_prunus: List[str], mapeamento_banker: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """
    Processa dados de net_inflow e agrupa por cliente Prunus.

    Args:
        dados: Lista de registros retornados pela API
        clientes_prunus: Lista de clientes da Prunus para filtrar
        mapeamento_banker: Dicionário cliente -> banker

    Returns:
        Dicionário com cliente como chave e DataFrame como valor
    """
    clientes_data = {}

    for registro in dados:
        cliente_name = registro.get("net_inflow.client_name", "").strip()

        # Verificar se cliente está na lista Prunus (case-insensitive)
        if cliente_name.lower() not in clientes_prunus:
            continue

        # Obter banker
        banker = mapeamento_banker.get(cliente_name.lower(), "Desconhecido")

        # Preparar dados do registro
        linha = {
            "Data": registro.get("net_inflow.date"),
            "Data Criação": registro.get("net_inflow.created_date"),
            "Data Liquidação": registro.get("net_inflow.settlement_date"),
            "CPF": registro.get("net_inflow.client_cpf"),
            "Email": registro.get("net_inflow.client_email"),
            "Cliente": cliente_name,
            "Banker": banker,
            "Email Foreign Finder": registro.get("net_inflow.foreign_finder_email"),
            "Código Foreign Finder": registro.get("net_inflow.foreign_finder_code"),
            "Foreign Finder": registro.get("net_inflow.foreign_finder_name"),
            "CNPJ Office": registro.get("net_inflow.office_cnpj"),
            "Office": registro.get("net_inflow.office_name"),
            "Tipo": registro.get("net_inflow.kind"),
            "Descrição": registro.get("net_inflow.description"),
            "CUSIP Produto": registro.get("net_inflow.product_cusip"),
            "Produto": registro.get("net_inflow.product_name"),
            "Tipo Produto": registro.get("net_inflow.product_type"),
            "Símbolo": registro.get("net_inflow.product_symbol"),
            "Net Inflow BRL": float(registro.get("net_inflow.net_inflow_brl", 0)),
            "Net Inflow USD": float(registro.get("net_inflow.net_inflow_usd", 0)),
        }

        # Adicionar à estrutura por cliente
        if cliente_name not in clientes_data:
            clientes_data[cliente_name] = []

        clientes_data[cliente_name].append(linha)

    # Converter listas em DataFrames
    dfs_por_cliente = {}
    for cliente, linhas in clientes_data.items():
        dfs_por_cliente[cliente] = pd.DataFrame(linhas)

    return dfs_por_cliente


def salvar_csvs_por_cliente(dfs_por_cliente: Dict[str, pd.DataFrame]) -> None:
    """
    Salva um CSV para cada cliente Prunus.

    Args:
        dfs_por_cliente: Dicionário com cliente -> DataFrame
    """
    dir_csv = "data/NetInflow/csv"
    os.makedirs(dir_csv, exist_ok=True)

    for cliente, df in dfs_por_cliente.items():
        # Sanitizar nome do cliente para usar como nome de arquivo
        cliente_sanitizado = cliente.replace(" ", "_").replace("/", "_")
        csv_path = os.path.join(dir_csv, f"{cliente_sanitizado}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"✓ Dados salvos em: {csv_path} ({len(df)} registros)")


def salvar_csv_raw(dados: List[Dict]) -> None:
    """
    Salva o CSV raw (bruto) da resposta da API.

    Args:
        dados: Lista de registros retornados pela API
    """
    dir_csv = "data/NetInflow/csv"
    os.makedirs(dir_csv, exist_ok=True)

    df = pd.DataFrame(dados)
    csv_path = os.path.join(dir_csv, "net_inflow_raw.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    print(f"✓ CSV raw salvo em: {csv_path} ({len(dados)} registros)")


def salvar_jsons_por_cliente(dfs_por_cliente: Dict[str, pd.DataFrame]) -> None:
    """
    Salva um JSON para cada cliente Prunus.

    Args:
        dfs_por_cliente: Dicionário com cliente -> DataFrame
    """
    dir_json = "data/NetInflow/json"
    os.makedirs(dir_json, exist_ok=True)

    for cliente, df in dfs_por_cliente.items():
        # Sanitizar nome do cliente para usar como nome de arquivo
        cliente_sanitizado = cliente.replace(" ", "_").replace("/", "_")
        json_path = os.path.join(dir_json, f"{cliente_sanitizado}.json")
        df.to_json(json_path, orient="records", indent=2, force_ascii=False)
        print(f"✓ Dados salvos em: {json_path} ({len(df)} registros)")


def salvar_json_raw(dados: List[Dict]) -> None:
    """
    Salva o JSON raw (bruto) da resposta da API.

    Args:
        dados: Lista de registros retornados pela API
    """
    dir_json = "data/NetInflow/json"
    os.makedirs(dir_json, exist_ok=True)

    json_path = os.path.join(dir_json, "net_inflow_raw.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)
    
    print(f"✓ JSON raw salvo em: {json_path} ({len(dados)} registros)")


def salvar_excel_abas_por_cliente(dfs_por_cliente: Dict[str, pd.DataFrame]) -> None:
    """
    Salva um Excel com uma aba para cada cliente Prunus.

    Args:
        dfs_por_cliente: Dicionário com cliente -> DataFrame
    """
    dir_excel = "data/NetInflow/excel"
    os.makedirs(dir_excel, exist_ok=True)

    excel_path = os.path.join(dir_excel, "net_inflow_prunus.xlsx")

    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            for cliente, df in dfs_por_cliente.items():
                # Sanitizar nome da aba (máximo 31 caracteres no Excel)
                aba_nome = cliente[:31]
                df.to_excel(writer, sheet_name=aba_nome, index=False)
        
        total_registros = sum(len(df) for df in dfs_por_cliente.values())
        print(f"✓ Excel com {len(dfs_por_cliente)} abas salvo em: {excel_path} ({total_registros} registros)")
    except ImportError:
        print("⚠ openpyxl não instalado. Pulando arquivo Excel.")
    except Exception as e:
        print(f"✗ Erro ao salvar Excel: {e}")


def main():
    """Função principal"""
    print("=" * 120)
    print("NET INFLOW - AVENUE (CLIENTES PRUNUS)")
    print("=" * 120)

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

    # Buscar dados de net_inflow
    print("\n4. Puxando dados de Net Inflow dos últimos 53 dias...")
    dados = fetch_net_inflow_looker("last 53 days")

    if not dados:
        print("⚠ Nenhum dado de net_inflow foi retornado!")
        return

    print(f"   Total de registros retornados: {len(dados)}")

    # Processar dados
    print("\n5. Processando dados para clientes Prunus...")
    dfs_por_cliente = processar_net_inflow(dados, clientes_prunus, mapeamento_banker)

    if not dfs_por_cliente:
        print("⚠ Nenhum dado foi encontrado para os clientes Prunus!")
        return

    print(f"   Clientes Prunus encontrados: {len(dfs_por_cliente)}")

    # Exibir resumo por cliente
    print("\n6. Resumo dos dados por cliente:")
    total_registros = 0
    for cliente, df in dfs_por_cliente.items():
        print(f"   - {cliente}: {len(df)} registros")
        total_registros += len(df)
    print(f"   Total de registros: {total_registros}")

    # Salvar CSVs por cliente
    print("\n7. Salvando CSVs por cliente...")
    salvar_csvs_por_cliente(dfs_por_cliente)

    # Salvar CSV raw
    print("\n8. Salvando CSV raw...")
    salvar_csv_raw(dados)

    # Salvar JSON raw
    print("\n9. Salvando JSON raw...")
    salvar_json_raw(dados)

    # Salvar Excel com abas por cliente
    print("\n10. Salvando Excel com abas por cliente...")
    salvar_excel_abas_por_cliente(dfs_por_cliente)

    print("\n" + "=" * 60)
    print("✓ Processo concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
