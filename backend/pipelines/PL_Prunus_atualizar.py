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


def carregar_json_existente(caminho: str) -> Dict:
    """
    Carrega o JSON existente e converte para dicionário para facilitar merge.

    Args:
        caminho: Caminho do arquivo JSON

    Returns:
        Dicionário com estrutura {(Cliente, CPF, Banker): {data: valor}}
    """
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)

        # Converter lista para dicionário
        dados_dict = {}
        for record in dados:
            cliente = record["Cliente"]
            cpf = record["CPF"]
            banker = record["Banker"]

            key = (cliente, cpf, banker)
            dados_dict[key] = {
                k: v for k, v in record.items() if k not in ["Cliente", "CPF", "Banker"]
            }

        print(f"✓ Carregado arquivo com {len(dados_dict)} clientes")
        return dados_dict, dados
    except FileNotFoundError:
        print(f"⚠ Arquivo {caminho} não encontrado. Será criado um novo.")
        return {}, []
    except json.JSONDecodeError:
        print(f"⚠ Erro ao decodificar JSON. Iniciando novo arquivo.")
        return {}, []


def obter_ultima_data(dados_existentes: Dict) -> str:
    """
    Encontra a data mais recente nos dados existentes.

    Args:
        dados_existentes: Dicionário de dados existentes

    Returns:
        Data mais recente no formato YYYY-MM-DD, ou data inicial se não houver dados
    """
    if not dados_existentes:
        return "2025-11-01"

    todas_datas = set()
    for cliente_dados in dados_existentes.values():
        todas_datas.update(cliente_dados.keys())

    if not todas_datas:
        return "2025-11-01"

    ultima_data = max(todas_datas)
    return (datetime.strptime(ultima_data, "%Y-%m-%d") + timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )


def processar_dados_novos(
    datas: List[str],
    clientes_prunus: List[str],
    mapeamento_banker: Dict[str, str],
    dados_existentes: Dict,
) -> Dict:
    """
    Processa dados novos e faz merge com dados existentes.

    Args:
        datas: Lista de datas a processar
        clientes_prunus: Lista de clientes da Prunus para filtrar
        mapeamento_banker: Dicionário cliente -> banker
        dados_existentes: Dados já carregados do JSON

    Returns:
        Dicionário atualizado com dados novos
    """
    resultados_novos = []
    dados_atualizados = dados_existentes.copy()

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

            key = (nome_cliente, cpf_cliente, banker)

            # Atualizar ou criar entrada
            if key not in dados_atualizados:
                dados_atualizados[key] = {}

            if soma_usd > 0:
                dados_atualizados[key][data] = soma_usd

        print(f"  {len(clientes)} clientes Prunus processados")

    return dados_atualizados


def converter_para_lista(dados_dict: Dict) -> List[Dict]:
    """
    Converte dicionário de volta para lista de registros.

    Args:
        dados_dict: Dicionário {(Cliente, CPF, Banker): {data: valor}}

    Returns:
        Lista de registros com as colunas de data
    """
    registros = []

    for (cliente, cpf, banker), datas_valores in dados_dict.items():
        record = {
            "Cliente": cliente,
            "CPF": cpf,
            "Banker": banker,
        }
        # Adicionar datas ordenadas
        for data in sorted(datas_valores.keys()):
            record[data] = datas_valores[data]

        registros.append(record)

    return registros


def salvar_atualizacao(dados_dict: Dict, caminho_json: str):
    """
    Salva os dados atualizados em JSON.

    Args:
        dados_dict: Dicionário atualizado de dados
        caminho_json: Caminho onde salvar o JSON
    """
    registros = converter_para_lista(dados_dict)

    # Garantir que a estrutura de diretórios existe
    os.makedirs(os.path.dirname(caminho_json), exist_ok=True)

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Dados atualizados salvos em: {caminho_json}")


def main():
    """Função principal"""
    print("=" * 60)
    print("ATUALIZAÇÃO DE P&L DIÁRIA - AVENUE (CLIENTES PRUNUS)")
    print("=" * 60)

    # Caminho do arquivo JSON
    json_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "PL", "json", "evolucao_pl_diaria.json"
    )

    # Autenticar com Looker
    print("\n1. Autenticando com API Looker...")
    try:
        token = autenticar_looker()
    except Exception as e:
        print(f"✗ Falha na autenticação: {e}")
        return

    # Carregar dados existentes
    print("\n2. Carregando dados existentes...")
    dados_existentes, lista_original = carregar_json_existente(json_path)

    # Obter última data processada
    ultima_data = obter_ultima_data(dados_existentes)
    print(f"   Última data processada: {ultima_data}")
    print(f"   Atualizando a partir de: {ultima_data}")

    # Carregar clientes Prunus
    print("\n3. Carregando lista de clientes Prunus...")
    clientes_prunus = carregar_clientes_prunus(
        os.path.join(os.path.dirname(__file__), "..", "prunus_list.txt")
    )

    if not clientes_prunus:
        print("⚠ Nenhum cliente Prunus carregado!")
        return

    # Carregar mapeamento Banker
    print("\n4. Carregando mapeamento de Bankers...")
    mapeamento_banker = carregar_mapeamento_banker(
        os.path.join(os.path.dirname(__file__), "..", "banker_list.txt")
    )

    # Gerar datas desde última processada até hoje
    print("\n5. Gerando datas para atualização...")
    datas = gerar_datas_diarias(ultima_data)
    print(f"   Total de dias a processar: {len(datas)}")

    if len(datas) == 0:
        print("   ✓ Dados já estão atualizados!")
        return

    # Processar dados novos
    print("\n6. Puxando dados do Looker (excluindo Balance US Banking)...")
    dados_atualizados = processar_dados_novos(
        datas, clientes_prunus, mapeamento_banker, dados_existentes
    )

    # Salvar atualização
    print("\n7. Salvando atualização...")
    salvar_atualizacao(dados_atualizados, json_path)

    # Exibir resumo
    print("\n8. Resumo dos dados:")
    print(f"   Total de clientes: {len(dados_atualizados)}")

    # Contar total de datas
    todas_as_datas = set()
    for cliente_dados in dados_atualizados.values():
        todas_as_datas.update(cliente_dados.keys())

    print(f"   Total de dias com dados: {len(todas_as_datas)}")
    if todas_as_datas:
        print(f"   Período: {min(todas_as_datas)} a {max(todas_as_datas)}")

    print("\n" + "=" * 60)
    print("✓ Processo concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()
