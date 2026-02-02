"""
API Backend para Avenue Dashboard
Fornece dados agregados de P&L, clientes e bankers
"""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS com origens específicas
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Carregando dados de P&L
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PL_JSON_PATH = os.path.join(DATA_DIR, "PL", "json", "evolucao_pl_diaria.json")
CLIENTE_PERFIL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "frontend", "data", "cliente_perfil.txt"
)


def load_pl_data() -> List[Dict[str, Any]]:
    """Carrega dados de P&L do arquivo JSON"""
    with open(PL_JSON_PATH, "r") as f:
        return json.load(f)


def load_cliente_emails() -> Dict[str, str]:
    """Carrega emails dos clientes do arquivo cliente_perfil.txt"""
    emails = {}
    try:
        with open(CLIENTE_PERFIL_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Pula o header (primeira linha)
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    nome = parts[0]
                    email = parts[2]
                    emails[nome] = email
    except Exception as e:
        print(f"Erro ao carregar cliente_perfil.txt: {e}")
    return emails


def aggregate_total_pl(data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Agrega P&L total de todos os clientes por data

    Args:
        data: Lista de clientes com seus P&L diários

    Returns:
        Dicionário com datas como chaves e P&L total agregado como valores
    """
    pl_total = {}

    for cliente in data:
        for key, value in cliente.items():
            # Pula campos que não são datas
            if key in ["Cliente", "CPF", "Banker"]:
                continue

            # Trata datas no formato YYYY-MM-DD
            if (
                isinstance(key, str)
                and len(key) == 10
                and key[4] == "-"
                and key[7] == "-"
            ):
                if value is not None:  # Ignora valores nulos
                    if key not in pl_total:
                        pl_total[key] = 0
                    try:
                        pl_total[key] += float(value)
                    except (ValueError, TypeError):
                        # Ignora valores que não podem ser convertidos
                        pass

    return pl_total


@app.route("/api/pl/total", methods=["GET"])
def get_total_pl():
    """
    Retorna P&L total agregado de todos os clientes
    Formato: Lista de objetos {date, value}
    Filtra apenas dados a partir de 2025-12-01
    """
    try:
        data = load_pl_data()
        pl_total = aggregate_total_pl(data)

        # Converte para formato de lista ordenada por data
        # Filtra apenas dados a partir de 2025-12-01
        result = [
            {"date": date, "value": round(value, 2)}
            for date, value in sorted(pl_total.items())
            if date >= "2025-12-01"
        ]

        return jsonify(
            {
                "success": True,
                "data": result,
                "startDate": result[0]["date"] if result else None,
                "endDate": result[-1]["date"] if result else None,
                "totalRecords": len(result),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/pl/stats", methods=["GET"])
def get_pl_stats():
    """
    Retorna estatísticas do P&L total
    """
    try:
        data = load_pl_data()
        pl_total = aggregate_total_pl(data)

        if not pl_total:
            return jsonify({"success": False, "error": "No data available"}), 404

        values = list(pl_total.values())
        max_value = max(values)
        min_value = min(values)
        avg_value = sum(values) / len(values)

        return jsonify(
            {
                "success": True,
                "stats": {
                    "max": round(max_value, 2),
                    "min": round(min_value, 2),
                    "average": round(avg_value, 2),
                    "totalClients": len(data),
                    "totalDays": len(pl_total),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clients/pl", methods=["GET"])
def get_clients_pl():
    """
    Retorna P&L de cada cliente na última data disponível com email
    """
    try:
        data = load_pl_data()
        emails = load_cliente_emails()

        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

        # Encontra a última data
        all_dates = set()
        for cliente in data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        if not all_dates:
            return jsonify({"success": False, "error": "No dates found"}), 404

        last_date = sorted(all_dates)[-1]

        # Filtra apenas dados a partir de 2025-12-01
        clients_data = []
        for cliente in data:
            cliente_nome = cliente.get("Cliente", "")
            cpf = cliente.get("CPF", "")
            banker = cliente.get("Banker", "")
            email = emails.get(cliente_nome, "")

            # Verifica se tem dados na última data (inclui P&L = 0)
            if last_date in cliente:
                pl_value = (
                    float(cliente[last_date]) if cliente[last_date] is not None else 0
                )
                clients_data.append(
                    {
                        "nome": cliente_nome,
                        "cpf": cpf,
                        "banker": banker,
                        "email": email,
                        "pl": round(pl_value, 2),
                        "data": last_date,
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": clients_data,
                "lastDate": last_date,
                "totalClients": len(clients_data),
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """
    Retorna métricas principais do dashboard:
    - Total de novos clientes no período (01/12/2025 a ultima data)
    - PL Total na última data
    - Captação no período (de /api/captacao/evolucao)
    - Top 3 bankers com maior captação
    """
    try:
        data = load_pl_data()
        net_inflow_path = os.path.join(
            DATA_DIR, "NetInflow", "json", "net_inflow_raw.json"
        )

        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

        # Encontra todas as datas disponíveis
        all_dates = set()
        for cliente in data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        if not all_dates:
            return jsonify({"success": False, "error": "No dates found"}), 404

        sorted_dates = sorted(all_dates)
        first_date = sorted_dates[0]  # 2025-12-01
        last_date = sorted_dates[-1]  # 2026-01-20

        # 1. Contar novos clientes (aqueles que aparecem em last_date mas não em first_date)
        clientes_primeira_data = set()
        clientes_ultima_data = set()
        pl_total_primeira_data = 0
        pl_total_ultima_data = 0

        for cliente in data:
            nome = cliente.get("Cliente", "")

            # Verifica se tem dados na primeira data
            if first_date in cliente and cliente[first_date] is not None:
                clientes_primeira_data.add(nome)
                pl_total_primeira_data += float(cliente[first_date])

            # Verifica se tem dados na última data
            if last_date in cliente and cliente[last_date] is not None:
                clientes_ultima_data.add(nome)
                pl_total_ultima_data += float(cliente[last_date])

        novos_clientes = len(clientes_ultima_data - clientes_primeira_data)

        # Calcula variação percentual do PL
        if pl_total_primeira_data != 0:
            pl_variacao_pct = (
                (pl_total_ultima_data - pl_total_primeira_data) / pl_total_primeira_data
            ) * 100
        else:
            pl_variacao_pct = 0

        # 2. Calcular captação total do período (usa a mesma lógica do endpoint de evolução)
        # Cria mapa cliente -> banker para busca rápida
        cliente_to_banker = {}
        for cliente in data:
            cliente_nome = cliente.get("Cliente", "")
            banker = cliente.get("Banker", "Sem Banker")
            cliente_to_banker[cliente_nome] = banker

        # Agrupa Net Inflow positivo por data E por banker
        captacao_by_date = {}
        bankers_captacao = {}

        try:
            with open(net_inflow_path, "r", encoding="utf-8") as f:
                net_inflow_data = json.load(f)

            if isinstance(net_inflow_data, list):
                for flow in net_inflow_data:
                    cliente_nome = flow.get("net_inflow.client_name", "")
                    flow_date = flow.get("net_inflow.date", "")
                    flow_value = flow.get("net_inflow.net_inflow_usd", 0)

                    # Encontra o banker do cliente
                    banker = cliente_to_banker.get(cliente_nome)
                    if not banker:
                        continue

                    # Exclui dados de Alan da métrica de captação
                    if "alan" in banker.lower():
                        continue

                    # Só conta valores positivos de Net Inflow
                    if flow_value > 0:
                        if flow_date not in captacao_by_date:
                            captacao_by_date[flow_date] = 0
                        captacao_by_date[flow_date] += flow_value

                        # Agrupar por banker também
                        if banker not in bankers_captacao:
                            bankers_captacao[banker] = 0
                        bankers_captacao[banker] += flow_value

            # Adiciona primeiro PL de novos clientes por banker
            for cliente in data:
                cliente_nome = cliente.get("Cliente", "")
                banker = cliente.get("Banker", "Sem Banker")

                # Exclui Alan da métrica de captação
                if "alan" in banker.lower():
                    continue

                # Encontra primeiro PL deste cliente
                for date in sorted_dates:
                    if date in cliente and cliente[date] is not None:
                        primeiro_pl = float(cliente[date])

                        # Se data do primeiro PL não é 2025-12-01, é novo cliente
                        if date != "2025-12-01":
                            if date not in captacao_by_date:
                                captacao_by_date[date] = 0
                            captacao_by_date[date] += primeiro_pl

                            # Adiciona ao banker também
                            if banker not in bankers_captacao:
                                bankers_captacao[banker] = 0
                            bankers_captacao[banker] += primeiro_pl
                        break

            # Calcula captação total acumulada (excluindo Alan)
            captacao_total = sum(captacao_by_date.values())

            # Top 3 bankers com maior captação (excluindo Alan)
            top_3 = sorted(bankers_captacao.items(), key=lambda x: x[1], reverse=True)[
                :3
            ]
            top_3_formatted = [
                {"nome": nome, "captacao": round(valor, 2)} for nome, valor in top_3
            ]

        except Exception as e:
            print(f"Erro ao calcular captação: {e}")
            captacao_total = 0
            top_3_formatted = []

        return jsonify(
            {
                "success": True,
                "metrics": {
                    "totalClientes": len(clientes_ultima_data),
                    "novosClientes": novos_clientes,
                    "plTotal": round(pl_total_ultima_data, 2),
                    "plVariacao": round(pl_variacao_pct, 2),
                    "captacaoPeriodo": round(captacao_total, 2),
                    "top3Bankers": top_3_formatted,
                    "periodoInicio": first_date,
                    "periodoFim": last_date,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clients/evolution", methods=["GET"])
def get_clients_evolution():
    """
    Retorna evolução de P&L para cada cliente no período (01/12/2025 a última data)
    """
    try:
        data = load_pl_data()
        emails = load_cliente_emails()

        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

        # Encontra todas as datas disponíveis
        all_dates = set()
        for cliente in data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        if not all_dates:
            return jsonify({"success": False, "error": "No dates found"}), 404

        sorted_dates = sorted(all_dates)

        # Prepara dados para cada cliente
        clients_evolution = []
        for cliente in data:
            nome = cliente.get("Cliente", "")
            cpf = cliente.get("CPF", "")
            banker = cliente.get("Banker", "")
            email = emails.get(nome, "")

            # Coleta dados diários do cliente
            evolution_data = []
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    pl_value = float(cliente[date])
                    evolution_data.append({"date": date, "value": round(pl_value, 2)})

            # Apenas inclui clientes com dados
            if evolution_data:
                clients_evolution.append(
                    {
                        "nome": nome,
                        "cpf": cpf,
                        "banker": banker,
                        "email": email,
                        "evolution": evolution_data,
                        "pl_inicial": evolution_data[0]["value"]
                        if evolution_data
                        else 0,
                        "pl_final": evolution_data[-1]["value"]
                        if evolution_data
                        else 0,
                        "variacao": round(
                            evolution_data[-1]["value"] - evolution_data[0]["value"], 2
                        )
                        if evolution_data
                        else 0,
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": clients_evolution,
                "totalClientes": len(clients_evolution),
                "periodoInicio": sorted_dates[0],
                "periodoFim": sorted_dates[-1],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/bankers/evolution", methods=["GET"])
def get_bankers_evolution():
    """
    Retorna evolução de P&L para cada banker (somando P&L de seus clientes)
    """
    try:
        data = load_pl_data()

        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

        # Encontra todas as datas disponíveis
        all_dates = set()
        for cliente in data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        if not all_dates:
            return jsonify({"success": False, "error": "No dates found"}), 404

        sorted_dates = sorted(all_dates)

        # Agrupa clientes por banker e calcula P&L agregado
        bankers_data = {}

        for cliente in data:
            banker = cliente.get("Banker", "Sem Banker")

            if banker not in bankers_data:
                bankers_data[banker] = {"evolution": {}, "clientes": []}

            bankers_data[banker]["clientes"].append(cliente.get("Cliente", ""))

            # Coleta dados diários
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    if date not in bankers_data[banker]["evolution"]:
                        bankers_data[banker]["evolution"][date] = 0
                    bankers_data[banker]["evolution"][date] += float(cliente[date])

        # Converte para formato de resposta
        bankers_evolution = []
        for banker_nome, banker_info in bankers_data.items():
            evolution_list = []
            for date in sorted_dates:
                if date in banker_info["evolution"]:
                    evolution_list.append(
                        {
                            "date": date,
                            "value": round(banker_info["evolution"][date], 2),
                        }
                    )

            if evolution_list:
                bankers_evolution.append(
                    {
                        "nome": banker_nome,
                        "clientes_count": len(banker_info["clientes"]),
                        "evolution": evolution_list,
                        "pl_inicial": evolution_list[0]["value"]
                        if evolution_list
                        else 0,
                        "pl_final": evolution_list[-1]["value"]
                        if evolution_list
                        else 0,
                        "variacao": round(
                            evolution_list[-1]["value"] - evolution_list[0]["value"], 2
                        )
                        if evolution_list
                        else 0,
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": bankers_evolution,
                "totalBankers": len(bankers_evolution),
                "periodoInicio": sorted_dates[0],
                "periodoFim": sorted_dates[-1],
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/bankers/captacao", methods=["GET"])
def get_bankers_captacao():
    """
    Retorna evolução de captação para cada banker
    Captação = soma de Net Inflow positivos + primeiro PL de novos clientes
    """
    try:
        pl_data = load_pl_data()

        # Carrega dados de Net Inflow
        netinflow_path = os.path.join(
            DATA_DIR, "NetInflow", "json", "net_inflow_raw.json"
        )
        with open(netinflow_path, "r", encoding="utf-8") as f:
            netinflow_data = json.load(f)

        if not pl_data or not netinflow_data:
            return jsonify({"success": False, "error": "No data available"}), 404

        # Encontra todas as datas do PL
        all_dates = set()
        for cliente in pl_data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        sorted_dates = sorted(all_dates)

        # Cria mapa de cliente para PL inicial (primeiro valor não nulo)
        cliente_pl_inicial = {}
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    cliente_pl_inicial[cliente_nome] = (date, float(cliente[date]))
                    break

        # Cria mapa cliente -> banker para busca rápida
        cliente_to_banker = {}
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            banker = cliente.get("Banker", "Sem Banker")
            cliente_to_banker[cliente_nome] = banker

        # Agrupa Net Inflow positivo por banker e data
        netinflow_by_banker = {}

        for flow in netinflow_data:
            cliente_nome = flow.get("net_inflow.client_name", "")
            flow_date = flow.get("net_inflow.date", "")
            flow_value = flow.get("net_inflow.net_inflow_usd", 0)

            # Encontra o banker do cliente
            banker = cliente_to_banker.get(cliente_nome)
            if not banker:
                continue

            # Só conta valores positivos de Net Inflow
            if flow_value > 0:
                if banker not in netinflow_by_banker:
                    netinflow_by_banker[banker] = {}
                if flow_date not in netinflow_by_banker[banker]:
                    netinflow_by_banker[banker][flow_date] = 0
                netinflow_by_banker[banker][flow_date] += flow_value

        # Agrupa captação por banker (Net Inflow + primeiro PL de novos clientes)
        bankers_captacao = {}

        # Adiciona Net Inflow
        for banker, dates_data in netinflow_by_banker.items():
            if banker not in bankers_captacao:
                bankers_captacao[banker] = {}
            for date, value in dates_data.items():
                if date not in bankers_captacao[banker]:
                    bankers_captacao[banker][date] = 0
                bankers_captacao[banker][date] += value

        # Adiciona primeiro PL de novos clientes
        # Clientes novos = aqueles cuja primeira data é >= 01/11/2025 e != 01/12/2025
        # Também inclui clientes cuja primeira data é 01/11/2025 (clientes iniciais com dados desde novembro)
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            banker = cliente.get("Banker", "Sem Banker")

            # Encontra primeiro valor de PL
            first_pl_date = None
            first_pl_value = None
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    first_pl_date = date
                    first_pl_value = float(cliente[date])
                    break

            # Inclui clientes cuja primeira data é >= 01/11/2025 como captação inicial
            # (seja cliente novo após 01/12 ou cliente inicial em 01/11)
            if first_pl_date and first_pl_date >= "2025-11-01":
                if banker not in bankers_captacao:
                    bankers_captacao[banker] = {}
                if first_pl_date not in bankers_captacao[banker]:
                    bankers_captacao[banker][first_pl_date] = 0
                bankers_captacao[banker][first_pl_date] += first_pl_value

        # Converte para formato de resposta com evolução acumulada
        bankers_evolution = []
        cutoff_date = "2025-11-01"

        for banker in sorted(bankers_captacao.keys()):
            evolution_list = []
            accumulated = 0

            # Combina todas as datas: PL + Net Inflow
            all_dates_for_banker = set(sorted_dates)
            if banker in netinflow_by_banker:
                all_dates_for_banker.update(netinflow_by_banker[banker].keys())

            # Garante que começa a partir de 01/11/2025
            all_dates_for_banker.add(cutoff_date)

            sorted_dates_for_banker = sorted(all_dates_for_banker)

            for date in sorted_dates_for_banker:
                # Filtra apenas datas a partir de 01/11/2025
                if date < cutoff_date:
                    continue

                if date in bankers_captacao[banker]:
                    accumulated += bankers_captacao[banker][date]
                evolution_list.append({"date": date, "value": round(accumulated, 2)})

            # Só inclui bankers que têm dados a partir de 01/11
            if evolution_list:
                bankers_evolution.append(
                    {
                        "nome": banker,
                        "evolution": evolution_list,
                        "captacao_total": round(accumulated, 2),
                        "captacao_inicial": round(evolution_list[0]["value"], 2)
                        if evolution_list
                        else 0,
                        "captacao_final": round(evolution_list[-1]["value"], 2)
                        if evolution_list
                        else 0,
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": bankers_evolution,
                "totalBankers": len(bankers_evolution),
                "periodoInicio": sorted_dates[0] if sorted_dates else None,
                "periodoFim": sorted_dates[-1] if sorted_dates else None,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/captacao/evolucao", methods=["GET"])
def get_captacao_evolucao():
    """
    Retorna evolução de captação total (soma de todos os bankers) por data
    """
    try:
        pl_data = load_pl_data()

        # Carrega dados de Net Inflow
        netinflow_path = os.path.join(
            DATA_DIR, "NetInflow", "json", "net_inflow_raw.json"
        )
        with open(netinflow_path, "r", encoding="utf-8") as f:
            netinflow_data = json.load(f)

        if not pl_data or not netinflow_data:
            return jsonify({"success": False, "error": "No data available"}), 404

        # Encontra todas as datas do PL
        all_dates = set()
        for cliente in pl_data:
            for key in cliente.keys():
                if (
                    key not in ["Cliente", "CPF", "Banker"]
                    and len(key) == 10
                    and key[4] == "-"
                    and key[7] == "-"
                ):
                    all_dates.add(key)

        sorted_dates = sorted(all_dates)

        # Cria mapa cliente -> banker para busca rápida
        cliente_to_banker = {}
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            banker = cliente.get("Banker", "Sem Banker")
            cliente_to_banker[cliente_nome] = banker

        # Agrupa Net Inflow positivo por data
        captacao_by_date = {}

        for flow in netinflow_data:
            cliente_nome = flow.get("net_inflow.client_name", "")
            flow_date = flow.get("net_inflow.date", "")
            flow_value = flow.get("net_inflow.net_inflow_usd", 0)

            # Encontra o banker do cliente
            banker = cliente_to_banker.get(cliente_nome)
            if not banker:
                continue

            # Só conta valores positivos de Net Inflow
            if flow_value > 0:
                if flow_date not in captacao_by_date:
                    captacao_by_date[flow_date] = 0
                captacao_by_date[flow_date] += flow_value

        # Adiciona primeiro PL de novos clientes
        cliente_pl_inicial = {}
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    cliente_pl_inicial[cliente_nome] = (date, float(cliente[date]))
                    break

        for cliente_nome, (first_date, first_value) in cliente_pl_inicial.items():
            # Inclui clientes cuja primeira data é >= 01/11/2025
            if first_date >= "2025-11-01":
                if first_date not in captacao_by_date:
                    captacao_by_date[first_date] = 0
                captacao_by_date[first_date] += first_value

        # Converte para formato de resposta com evolução acumulada
        evolution_list = []
        accumulated = 0

        # Combina todas as datas: PL + Net Inflow
        all_dates_captacao = set(sorted_dates)
        all_dates_captacao.update(captacao_by_date.keys())
        sorted_dates_captacao = sorted(all_dates_captacao)

        for date in sorted_dates_captacao:
            if date in captacao_by_date:
                accumulated += captacao_by_date[date]
            evolution_list.append({"date": date, "value": round(accumulated, 2)})

        return jsonify(
            {
                "success": True,
                "data": evolution_list,
                "captacao_total": round(accumulated, 2),
                "periodoInicio": sorted_dates_captacao[0]
                if sorted_dates_captacao
                else None,
                "periodoFim": sorted_dates_captacao[-1]
                if sorted_dates_captacao
                else None,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(debug=debug, port=port, host="0.0.0.0")
