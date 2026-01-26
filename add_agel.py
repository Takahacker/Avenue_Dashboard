import json

with open("backend/data/PL/json/evolucao_pl_diaria.json", "r") as f:
    pl_data = json.load(f)

template = pl_data[-1].copy()
new_client = {
    "Cliente": "Agel Gustavo Turim",
    "CPF": "12345678900",
    "Banker": "Eduardo Marquesi de Oliveira",
}

for key, value in template.items():
    if key not in ["Cliente", "CPF", "Banker"]:
        new_client[key] = round(float(value) * 0.8, 2)

pl_data.append(new_client)

with open("backend/data/PL/json/evolucao_pl_diaria.json", "w") as f:
    json.dump(pl_data, f, indent=2)

print("Cliente Agel Gustavo Turim adicionado!")
print(f"Total: {len(pl_data)} clientes")
