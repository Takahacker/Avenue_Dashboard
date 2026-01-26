"""
API Backend para Avenue Dashboard
Fornece dados agregados de P&L, clientes e bankers
Wrapper para rodar na raiz com caminhos ajustados
"""

import json
import os
from typing import Dict, List, Any
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Configurar CORS com origens específicas
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Carregando dados de P&L - ajustar para raiz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "backend", "data")
PL_JSON_PATH = os.path.join(DATA_DIR, "PL", "json", "evolucao_pl_diaria.json")
CLIENTE_PERFIL_PATH = os.path.join(BASE_DIR, "frontend", "data", "cliente_perfil.txt")
NETINFLOW_PATH = os.path.join(DATA_DIR, "NetInflow", "json", "net_inflow_raw.json")


def load_pl_data() -> List[Dict[str, Any]]:
    """Carrega dados de P&L do arquivo JSON"""
    try:
        with open(PL_JSON_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: arquivo não encontrado em {PL_JSON_PATH}")
        return []


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


def load_cliente_bankers() -> Dict[str, str]:
    """Carrega bankers dos clientes do arquivo cliente_perfil.txt"""
    bankers = {}
    try:
        with open(CLIENTE_PERFIL_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Pula o header (primeira linha)
            for line in lines[1:]:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 2:
                    nome = parts[0]
                    banker = parts[1] if len(parts) > 1 else "Sem Banker"
                    bankers[nome] = banker
    except Exception as e:
        print(f"Erro ao carregar cliente_perfil.txt: {e}")
    return bankers


def aggregate_total_pl(data: List[Dict[str, Any]]) -> Dict[str, float]:
    """Agrega P&L total de todos os clientes por data"""
    pl_total = {}
    for cliente in data:
        for key, value in cliente.items():
            if key in ["Cliente", "CPF", "Banker"]:
                continue
            if (
                isinstance(key, str)
                and len(key) == 10
                and key[4] == "-"
                and key[7] == "-"
            ):
                if value is not None:
                    if key not in pl_total:
                        pl_total[key] = 0
                    try:
                        pl_total[key] += float(value)
                    except (ValueError, TypeError):
                        pass
    return pl_total


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})


@app.route("/api/pl/total", methods=["GET"])
def get_total_pl():
    """Retorna P&L total agregado de todos os clientes"""
    try:
        data = load_pl_data()
        pl_total = aggregate_total_pl(data)
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
        print(f"Erro em get_total_pl: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/pl/stats", methods=["GET"])
def get_pl_stats():
    """Retorna estatísticas do P&L total"""
    try:
        data = load_pl_data()
        pl_total = aggregate_total_pl(data)
        if not pl_total:
            return jsonify({"success": False, "error": "No data available"}), 404
        values = list(pl_total.values())
        return jsonify(
            {
                "success": True,
                "stats": {
                    "max": round(max(values), 2),
                    "min": round(min(values), 2),
                    "average": round(sum(values) / len(values), 2),
                    "totalClients": len(data),
                    "totalDays": len(pl_total),
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clients/pl", methods=["GET"])
def get_clients_pl():
    """Retorna P&L de cada cliente na última data disponível"""
    try:
        data = load_pl_data()
        emails = load_cliente_emails()
        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

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
        clients_data = []
        for cliente in data:
            if last_date in cliente:
                pl_value = (
                    float(cliente[last_date]) if cliente[last_date] is not None else 0
                )
                clients_data.append(
                    {
                        "nome": cliente.get("Cliente", ""),
                        "cpf": cliente.get("CPF", ""),
                        "banker": cliente.get("Banker", ""),
                        "email": emails.get(cliente.get("Cliente", ""), ""),
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


@app.route("/api/clients/evolution", methods=["GET"])
def get_clients_evolution():
    """Retorna evolução de P&L para cada cliente"""
    try:
        data = load_pl_data()
        emails = load_cliente_emails()
        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

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
        clients_evolution = []

        for cliente in data:
            evolution_data = []
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    pl_value = float(cliente[date])
                    evolution_data.append({"date": date, "value": round(pl_value, 2)})

            if evolution_data:
                clients_evolution.append(
                    {
                        "nome": cliente.get("Cliente", ""),
                        "cpf": cliente.get("CPF", ""),
                        "banker": cliente.get("Banker", ""),
                        "email": emails.get(cliente.get("Cliente", ""), ""),
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
    """Retorna evolução de P&L para cada banker"""
    try:
        data = load_pl_data()
        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

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
        bankers_data = {}

        for cliente in data:
            banker = cliente.get("Banker", "Sem Banker")
            if banker not in bankers_data:
                bankers_data[banker] = {"evolution": {}, "clientes": []}

            bankers_data[banker]["clientes"].append(cliente.get("Cliente", ""))
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    if date not in bankers_data[banker]["evolution"]:
                        bankers_data[banker]["evolution"][date] = 0
                    bankers_data[banker]["evolution"][date] += float(cliente[date])

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
    """Retorna evolução de captação para cada banker"""
    try:
        pl_data = load_pl_data()
        try:
            with open(NETINFLOW_PATH, "r", encoding="utf-8") as f:
                netinflow_data = json.load(f)
        except:
            netinflow_data = []

        if not pl_data:
            return jsonify({"success": False, "error": "No data available"}), 404

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
        cliente_to_banker = {}
        for cliente in pl_data:
            cliente_to_banker[cliente.get("Cliente", "")] = cliente.get(
                "Banker", "Sem Banker"
            )

        bankers_captacao = {}
        for flow in netinflow_data:
            cliente_nome = flow.get("net_inflow.client_name", "")
            flow_date = flow.get("net_inflow.date", "")
            flow_value = flow.get("net_inflow.net_inflow_usd", 0)
            banker = cliente_to_banker.get(cliente_nome)
            if banker and flow_value > 0:
                if banker not in bankers_captacao:
                    bankers_captacao[banker] = {}
                if flow_date not in bankers_captacao[banker]:
                    bankers_captacao[banker][flow_date] = 0
                bankers_captacao[banker][flow_date] += flow_value

        for cliente in pl_data:
            banker = cliente.get("Banker", "Sem Banker")
            first_pl_date = None
            first_pl_value = None
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    first_pl_date = date
                    first_pl_value = float(cliente[date])
                    break

            if first_pl_date and first_pl_date != "2025-12-01":
                if banker not in bankers_captacao:
                    bankers_captacao[banker] = {}
                if first_pl_date not in bankers_captacao[banker]:
                    bankers_captacao[banker][first_pl_date] = 0
                bankers_captacao[banker][first_pl_date] += first_pl_value

        bankers_evolution = []
        for banker in sorted(bankers_captacao.keys()):
            evolution_list = []
            accumulated = 0
            all_dates_banker = set(sorted_dates) | set(bankers_captacao[banker].keys())
            for date in sorted(all_dates_banker):
                if date in bankers_captacao[banker]:
                    accumulated += bankers_captacao[banker][date]
                evolution_list.append({"date": date, "value": round(accumulated, 2)})

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
    """Retorna evolução de captação total"""
    try:
        pl_data = load_pl_data()
        try:
            with open(NETINFLOW_PATH, "r", encoding="utf-8") as f:
                netinflow_data = json.load(f)
        except:
            netinflow_data = []

        if not pl_data:
            return jsonify({"success": False, "error": "No data available"}), 404

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
        cliente_to_banker = {}
        for cliente in pl_data:
            cliente_to_banker[cliente.get("Cliente", "")] = cliente.get(
                "Banker", "Sem Banker"
            )

        captacao_by_date = {}
        for flow in netinflow_data:
            cliente_nome = flow.get("net_inflow.client_name", "")
            flow_date = flow.get("net_inflow.date", "")
            flow_value = flow.get("net_inflow.net_inflow_usd", 0)
            banker = cliente_to_banker.get(cliente_nome)
            if banker and flow_value > 0:
                if flow_date not in captacao_by_date:
                    captacao_by_date[flow_date] = 0
                captacao_by_date[flow_date] += flow_value

        cliente_pl_inicial = {}
        for cliente in pl_data:
            cliente_nome = cliente.get("Cliente", "")
            for date in sorted_dates:
                if date in cliente and cliente[date] is not None:
                    cliente_pl_inicial[cliente_nome] = (date, float(cliente[date]))
                    break

        for cliente_nome, (first_date, first_value) in cliente_pl_inicial.items():
            if first_date != "2025-12-01":
                if first_date not in captacao_by_date:
                    captacao_by_date[first_date] = 0
                captacao_by_date[first_date] += first_value

        evolution_list = []
        accumulated = 0
        all_dates_captacao = set(sorted_dates) | set(captacao_by_date.keys())
        for date in sorted(all_dates_captacao):
            if date in captacao_by_date:
                accumulated += captacao_by_date[date]
            evolution_list.append({"date": date, "value": round(accumulated, 2)})

        return jsonify(
            {
                "success": True,
                "data": evolution_list,
                "captacao_total": round(accumulated, 2),
                "periodoInicio": sorted(all_dates_captacao)[0]
                if all_dates_captacao
                else None,
                "periodoFim": sorted(all_dates_captacao)[-1]
                if all_dates_captacao
                else None,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/metrics", methods=["GET"])
def get_metrics():
    """Retorna métricas principais do dashboard"""
    try:
        data = load_pl_data()
        bankers_map = load_cliente_bankers()
        try:
            with open(NETINFLOW_PATH, "r", encoding="utf-8") as f:
                netinflow_data = json.load(f)
        except:
            netinflow_data = []

        if not data:
            return jsonify({"success": False, "error": "No client data available"}), 404

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
        first_date, last_date = sorted_dates[0], sorted_dates[-1]

        clientes_primeira = clientes_ultima = 0
        pl_primeira = pl_ultima = 0
        bankers_captacao = {}
        cliente_to_banker = {}

        for cliente in data:
            cliente_nome = cliente.get("Cliente", "")
            banker = bankers_map.get(cliente_nome, cliente.get("Banker", "Sem Banker"))
            cliente_to_banker[cliente_nome] = banker

            if first_date in cliente and cliente[first_date] is not None:
                clientes_primeira += 1
                pl_primeira += float(cliente[first_date])
            if last_date in cliente and cliente[last_date] is not None:
                clientes_ultima += 1
                pl_ultima += float(cliente[last_date])

        # Calcular captação por banker a partir do netinflow
        for flow in netinflow_data:
            cliente_nome = flow.get("net_inflow.client_name", "")
            flow_value = flow.get("net_inflow.net_inflow_usd", 0)
            banker = cliente_to_banker.get(cliente_nome)
            if banker and flow_value > 0:
                if banker not in bankers_captacao:
                    bankers_captacao[banker] = 0
                bankers_captacao[banker] += flow_value

        # Incluir clientes novos (primeira data com valor > 0 != 2025-12-01) como captação
        for cliente in data:
            cliente_nome = cliente.get("Cliente", "")
            banker = cliente_to_banker.get(cliente_nome)

            # Verificar se é cliente novo (primeira data com valor > 0 não é 2025-12-01)
            primeiro_valor = None
            primeira_data = None
            for date in sorted_dates:
                if (
                    date in cliente
                    and cliente[date] is not None
                    and float(cliente[date]) > 0
                ):
                    primeira_data = date
                    primeiro_valor = float(cliente[date])
                    break

            # Se primeira data com valor > 0 não é 2025-12-01, é cliente novo - contar como captação
            if primeiro_valor and primeira_data and primeira_data != "2025-12-01":
                if banker not in bankers_captacao:
                    bankers_captacao[banker] = 0
                bankers_captacao[banker] += primeiro_valor

        # Se ainda não há dados de captação, usar P&L inicial como proxy
        if not bankers_captacao:
            for cliente in data:
                cliente_nome = cliente.get("Cliente", "")
                banker = cliente_to_banker.get(cliente_nome)
                if first_date in cliente and cliente[first_date] is not None:
                    pl_value = float(cliente[first_date])
                    if pl_value > 0:
                        if banker not in bankers_captacao:
                            bankers_captacao[banker] = 0
                        bankers_captacao[banker] += pl_value

        # Calcular Top 3 Bankers por captação
        top3_bankers = sorted(
            bankers_captacao.items(), key=lambda x: x[1], reverse=True
        )[:3]
        top3_list = [
            {"nome": nome, "captacao": round(captacao, 2)}
            for nome, captacao in top3_bankers
        ]

        # Captação total do período
        captacao_total = sum(bankers_captacao.values())

        return jsonify(
            {
                "success": True,
                "metrics": {
                    "totalClientes": clientes_ultima,
                    "novosClientes": max(0, clientes_ultima - clientes_primeira),
                    "plTotal": round(pl_ultima, 2),
                    "plVariacao": round(
                        ((pl_ultima - pl_primeira) / pl_primeira * 100)
                        if pl_primeira
                        else 0,
                        2,
                    ),
                    "captacaoPeriodo": round(captacao_total, 2),
                    "top3Bankers": top3_list,
                    "periodoInicio": first_date,
                    "periodoFim": last_date,
                },
            }
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(debug=debug, port=port, host="0.0.0.0")
