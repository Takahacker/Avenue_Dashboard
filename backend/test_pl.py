#!/usr/bin/env python3
import json
from typing import Dict, List, Any

# Simular o que o endpoint faz
with open("data/PL/json/evolucao_pl_diaria.json", "r") as f:
    data = json.load(f)

pl_total = {}

for cliente in data:
    for key, value in cliente.items():
        if key in ["Cliente", "CPF", "Banker"]:
            continue

        if isinstance(key, str) and len(key) == 10 and key[4] == "-" and key[7] == "-":
            if value is not None:
                if key not in pl_total:
                    pl_total[key] = 0
                try:
                    pl_total[key] += float(value)
                except (ValueError, TypeError):
                    pass

# Mostra resultado
sorted_dates = sorted(pl_total.items())
print(f"Total de datas com dados: {len(pl_total)}")
print(f"\nPrimeiras 5 datas:")
for date, value in sorted_dates[:5]:
    print(f"  {date}: ${value:,.2f}")

print(f"\nÚltimas 5 datas:")
for date, value in sorted_dates[-5:]:
    print(f"  {date}: ${value:,.2f}")

# Estatísticas
values = list(pl_total.values())
print(f"\nEstatísticas:")
print(f"  Máximo: ${max(values):,.2f}")
print(f"  Mínimo: ${min(values):,.2f}")
print(f"  Média: ${sum(values) / len(values):,.2f}")
