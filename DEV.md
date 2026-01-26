# Development Guide - Avenue Dashboard

## Setup Local (Desenvolvimento)

### Pré-requisitos

- Python 3.10+
- Node.js 18+ ou Bun
- Git

### 1. Clonar repositório

```bash
git clone https://github.com/Takahacker/Avenue-Dashboard.git
cd Avenue-Dashboard
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais Looker:

```env
LOOKER_CLIENT_ID=seu_client_id
LOOKER_CLIENT_SECRET=seu_client_secret
FLASK_ENV=development
FLASK_DEBUG=1
```

### 3. Opção A: Rodar com script automático (recomendado)

```bash
chmod +x dev.sh
./dev.sh
```

Isso iniciará automaticamente:

- **Backend**: http://localhost:5000 (Flask)
- **Frontend**: http://localhost:5173 (Vite)

### 4. Opção B: Rodar manualmente em dois terminais

#### Terminal 1 - Backend (Python)

```bash
python3 -m venv venv  # Criar virtual environment (primeira vez)
source venv/bin/activate  # Ativar virtual environment
pip install -r requirements.txt  # Instalar dependências (primeira vez)

export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 -m flask run --port=5000
```

#### Terminal 2 - Frontend (Node/Bun)

```bash
cd frontend

# Com Bun (mais rápido)
bun install  # Primeira vez apenas
bun run dev

# Ou com npm
npm install  # Primeira vez apenas
npm run dev
```

## Estrutura de Pastas

```
Avenue-Dashboard/
├── app.py                 # Flask app (raiz, requerido pelo Railway)
├── requirements.txt       # Dependências Python
├── backend/
│   ├── api.py            # API Backend completa
│   ├── utils.py          # Funções utilitárias
│   └── data/             # Dados JSON, CSV, Excel
├── frontend/
│   ├── src/
│   │   ├── pages/        # Páginas (Index, Clients, Bankers)
│   │   ├── components/   # Componentes React
│   │   └── lib/          # Utilitários (apiConfig.ts, colors.ts)
│   └── package.json
└── .env.example          # Template de variáveis
```

## API Local

Quando rodar em dev, a API estará em:

- `http://localhost:5000/api/health`
- `http://localhost:5000/api/pl/total`
- `http://localhost:5000/api/metrics`
- `http://localhost:5000/api/clients/pl`
- `http://localhost:5000/api/clients/evolution`
- etc.

## Variáveis de Ambiente

### Backend (`.env`)

```env
LOOKER_CLIENT_ID=xxx
LOOKER_CLIENT_SECRET=xxx
FLASK_ENV=development
FLASK_DEBUG=1
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (automático)

- `VITE_API_URL=http://localhost:5000` (default em dev)

## Hot Reload

- **Backend**: Qualquer mudança em `app.py` reloa automaticamente (FLASK_DEBUG=1)
- **Frontend**: Qualquer mudança em `src/` reloa automaticamente (Vite)

## Troubleshooting

### Porta 5000 já em uso

```bash
lsof -i :5000
kill -9 <PID>
```

### Porta 5173 já em uso

```bash
lsof -i :5173
kill -9 <PID>
```

### CORS error

Certifique-se que `CORS_ORIGINS` no `.env` inclui `http://localhost:5173`

### Módulos Python não encontrados

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Dependências Node não encontradas

```bash
cd frontend
rm -rf node_modules package-lock.json
bun install  # ou npm install
```

## Deployment

Ver [RAILWAY_SETUP.md](./RAILWAY_SETUP.md) para deploy em production (Railway + Vercel).

## Commits e Deploy Automático

1. Mudanças no `app.py` ou `backend/` → Railway redeploy automático
2. Mudanças em `frontend/src/` → Vercel redeploy automático
3. Mudanças em dados (`backend/data/`) → Ambos redeploy automático

Basta fazer `git push` e os deploys acontecem automaticamente! 🚀
