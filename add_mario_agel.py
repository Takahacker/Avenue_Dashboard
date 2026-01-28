#!/usr/bin/env python3
"""
Script para adicionar Mario Rossi e Agel Gustavo Turim aos dados de PL
"""

import json
from datetime import datetime, timedelta

# Carregar dados existentes
with open("backend/data/PL/json/evolucao_pl_diaria.json", "r") as f:
    data = json.load(f)

# Gerar todas as datas de 01/11/2025 a 25/01/2026
start_date = datetime.strptime("2025-11-01", "%Y-%m-%d")
end_date = datetime.strptime("2026-01-27", "%Y-%m-%d")
dates = []
current = start_date
while current <= end_date:
    dates.append(current.strftime("%Y-%m-%d"))
    current += timedelta(days=1)

# Agel Gustavo Turim - PL = 0 em todas as datas
agel = {
    "Cliente": "Agel Gustavo Turim",
    "CPF": "00000000000",
    "Banker": "Eduardo Marquesi de Oliveira",
}
for date in dates:
    agel[date] = 0.0

# Mario Rossi - PL = 0 até 24/01, depois tem saldo
mario = {
    "Cliente": "Mario Rossi",
    "CPF": "11111111111",
    "Banker": "Bruno Leite Bernardes",
}
for date in dates:
    if date < "2026-01-24":
        mario[date] = None  # Sem dados antes de 24/01
    elif date == "2026-01-24":
        mario[date] = 195930.77
    elif date == "2026-01-25":
        mario[date] = 195930.77
    elif date == "2026-01-26":
        mario[date] = 195930.77
    elif date == "2026-01-27":
        mario[date] = 195930.77
    else:
        mario[date] = None

# Adicionar ao JSON
data.append(agel)
data.append(mario)

# Salvar
with open("backend/data/PL/json/evolucao_pl_diaria.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("✓ Mario Rossi e Agel Gustavo Turim adicionados ao JSON")
print(f"  Total de clientes: {len(data)}")
