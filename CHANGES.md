# Mudanças Implementadas - Janeiro 26, 2026

## 📊 Período de Dados

### Pipelines (Backend)

- **PL_Prunus_Historico.py**: Agora roda desde **01/11/2025** (antes era 01/12/2025)
  - Coleta dados completos para 87 dias (01/nov até hoje)
  - Permite análise mais rica dos bankers

### Gráficos (Frontend)

- Todos os gráficos exibem dados apenas de **01/12/2025 em diante**
- Inclui: P&L Total, Clientes, Bankers, Captação

### Top 3 Bankers (Métrica)

- Usa dados desde **01/11/2025** para ranking mais robusto
- Captação do Período usa **01/12 - 31/01** para métrica semanal

---

## 📝 Detalhes Técnicos

### Backend (app.py)

```python
# Já estava configurado assim - mantido como está:
top_bankers_inicio = "2025-11-01"    # Para ranking (dados mais ricos)
periodo_captacao_inicio = "2025-12-01"  # Para métrica do período
```

### APIs Atualizadas

Todas as rotas de evolução agora filtram `date >= "2025-12-01"`:

- `GET /api/clients/evolution` ✅
- `GET /api/bankers/evolution` ✅
- `GET /api/captacao/evolucao` ✅
- `GET /api/pl/total` ✅ (já tinha filtro)

---

## 🚀 Deploy

- ✅ Commit: `feat: Estender pipelines para desde 01/11/2025...`
- ✅ Push para GitHub realizado
- ✅ Railway redeploy em progresso (auto)
- ✅ Vercel redeploy em progresso (auto)

Mudanças devem estar disponíveis em ~2 minutos em:

- Backend: https://avenuedashboard-production.up.railway.app
- Frontend: https://avenuedashboard.vercel.app

---

## 📋 Resumo das Mudanças

| Arquivo                                    | Mudança                                                 |
| ------------------------------------------ | ------------------------------------------------------- |
| `backend/pipelines/PL_Prunus_Historico.py` | Alterou start date de 2025-12-01 → 2025-11-01           |
| `app.py`                                   | Adicionou filtro `>= 2025-12-01` em 3 rotas de evolução |
| `DEV.md`                                   | Novo: guia de desenvolvimento local                     |
| `dev.sh`                                   | Novo: script de startup automático                      |

---

## ✅ Verificar

1. **Gráficos começam em 01/12/2025**: ✓
2. **Top 3 Bankers usa dados desde nov**: ✓
3. **Captação = movimentações positivas + novos clientes**: ✓
4. **Novos clientes podem entrar desde nov**: ✓

Tudo pronto! 🎉
