# Avenue Dashboard - Integração Frontend & Backend

## 📋 Estrutura do Projeto

```
Avenue_Dashboard/
├── backend/          # API Python com Flask
│   ├── api.py       # Endpoints da API
│   ├── data/        # Dados em CSV/JSON
│   └── requirements.txt
└── frontend/        # React + TypeScript + Vite
    ├── src/
    │   └── components/
    │       └── EvolutionChart.tsx  # Gráfico integrado com API
    └── .env
```

## 🚀 Como Executar

### 1. Backend (API)

```bash
cd backend

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor Flask
python api.py
```

O servidor estará disponível em: `http://localhost:5000`

**Endpoints disponíveis:**

- `GET /api/pl/total` - P&L total agregado de todos os clientes (01/12 até 20/01)
- `GET /api/pl/stats` - Estatísticas do P&L total (máx, mín, média)
- `GET /api/health` - Health check

### 2. Frontend

```bash
cd frontend

# Instalar dependências
bun install

# Rodar em desenvolvimento
bun dev
```

O site estará disponível em: `http://localhost:5173`

## 📊 Dados Disponíveis

- **Período**: 2025-12-01 até 2026-01-20 (51 dias)
- **Clientes**: 10 clientes diferentes
- **Métrica**: P&L diário agregado de todos os clientes

### Estatísticas Gerais do P&L Total

| Métrica           | Valor         |
| ----------------- | ------------- |
| P&L Máximo        | $3.476.468,98 |
| P&L Mínimo        | $2.411.473,63 |
| P&L Médio         | $2.813.714,81 |
| Total de Dias     | 51            |
| Total de Clientes | 10            |

## 🔄 Integração Realizada

O componente `EvolutionChart` foi atualizado para:

1. ✅ Buscar dados em tempo real da API
2. ✅ Exibir P&L total de todos os clientes (agregado)
3. ✅ Mostrar período de 01/12 até 20/01
4. ✅ Calcular e exibir estatísticas (máx, mín, média)
5. ✅ Tratamento de erros e estados de carregamento

## 🔧 Variáveis de Ambiente

**Frontend (`.env`):**

```
VITE_API_URL=http://localhost:5000
```

Altere a URL se o backend estiver rodando em outra porta ou servidor.

## 📝 Próximos Passos

- [ ] Integrar dados de clientes individuais
- [ ] Adicionar filtros por período
- [ ] Integrar dados de NetInflow
- [ ] Dashboard de bankers
