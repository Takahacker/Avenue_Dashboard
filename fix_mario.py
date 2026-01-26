import json

with open("backend/data/PL/json/evolucao_pl_diaria.json", "r") as f:
    pl_data = json.load(f)

# Pegar todas as datas do primeiro cliente
template = pl_data[0]
all_dates = sorted(
    [k for k in template.keys() if k not in ["Cliente", "CPF", "Banker"]]
)

print(f"Todas as datas: {all_dates[0]} a {all_dates[-1]}")
print(f"Total de datas: {len(all_dates)}")

# Encontrar Mario e preencher todas as datas
for cliente in pl_data:
    if cliente["Cliente"] == "Mario Rossi":
        # Preencher com 0 para datas antes de 24/01
        for date in all_dates:
            if date < "2026-01-24":
                cliente[date] = 0
        print(
            f"✓ Mario Rossi agora tem dados em todas as datas de {all_dates[0]} a 2026-01-25"
        )
        print(f"  Datas com 0: {all_dates[0]} a 2026-01-23")
        print(f"  Datas com $195,930.77: 2026-01-24 a 2026-01-25")

with open("backend/data/PL/json/evolucao_pl_diaria.json", "w") as f:
    json.dump(pl_data, f, indent=2)

print("✓ Arquivo atualizado!")
