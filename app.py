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


def aggregate_total_pl(data: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Agrega P&L total de todos os clientes por data
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
    """Retorna P&L de cada cliente na última data disponível com email"""
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

        clients_data = []
        for cliente in data:
            cliente_nome = cliente.get("Cliente", "")
            cpf = cliente.get("CPF", "")
            banker = cliente.get("Banker", "")
            email = emails.get(cliente_nome, "")

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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    print(f"Starting Flask app on port {port}")
    app.run(debug=debug, port=port, host="0.0.0.0")
