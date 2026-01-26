import json
from datetime import datetime, timedelta

# Hoje é 26/01/2026 (domingo)
today = datetime(2026, 1, 26)
friday = datetime(2026, 1, 24)  # Sexta-feira

# Gerar datas de sexta até hoje
dates_range = []
current = friday
while current <= today:
    dates_range.append(current.strftime("%Y-%m-%d"))
    current += timedelta(days=1)

print(f"Datas para adicionar: {dates_range}")

# Carregar JSON
with open("backend/data/PL/json/evolucao_pl_diaria.json", "r") as f:
    pl_data = json.load(f)

# Encontrar Mario Rossi e atualizar
mario_found = False
for cliente in pl_data:
    if cliente["Cliente"] == "Mario Rossi":
        # Adicionar PL para sexta até hoje
        for date in dates_range:
            cliente[date] = 195930.77
        mario_found = True
        print(
            f"✓ Atualizado Mario Rossi com PL = $195,930.77 de {dates_range[0]} a {dates_range[-1]}"
        )

if not mario_found:
    print("✗ Mario Rossi não encontrado!")

# Salvar
with open("backend/data/PL/json/evolucao_pl_diaria.json", "w") as f:
    json.dump(pl_data, f, indent=2)

print("✓ Arquivo atualizado com sucesso!")
