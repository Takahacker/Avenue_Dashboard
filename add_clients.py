import json

# Ler P&L
with open("backend/data/PL/json/evolucao_pl_diaria.json", "r") as f:
    pl_data = json.load(f)

# Pegar um cliente como template para pegar todas as datas
template = pl_data[0]
dates = [k for k in template.keys() if k not in ["Cliente", "CPF", "Banker"]]

# Adicionar Mario Rossi
mario = {"Cliente": "Mario Rossi", "CPF": "12345678901", "Banker": "Bruno Leite"}
for date in dates:
    mario[date] = 0

# Adicionar Agel Gustavo Turim
agel = {
    "Cliente": "Agel Gustavo Turim",
    "CPF": "12345678902",
    "Banker": "Eduardo Marquesi de Oliveira",
}
for date in dates:
    agel[date] = 0

pl_data.append(mario)
pl_data.append(agel)

# Salvar
with open("backend/data/PL/json/evolucao_pl_diaria.json", "w") as f:
    json.dump(pl_data, f, indent=2)

print(f"Clientes adicionados! Total agora: {len(pl_data)} clientes")
print("- Mario Rossi (Bruno Leite)")
print("- Agel Gustavo Turim (Eduardo Marquesi de Oliveira)")
