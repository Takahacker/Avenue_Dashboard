# 🚀 Guia de Deploy no Railway

## 📋 Pré-requisitos

1. **GitHub** - Repositório com o código
2. **Railway** - Conta gratuita em https://railway.app
3. **Vercel** - Para o frontend (opcional)

---

## ✅ Passo 1: Preparar o GitHub

### 1.1 Criar repositório (se não tiver)

```bash
cd /Users/takahashi/LVNT/Avenue/Avenue_Dashboard

git init
git add .
git commit -m "Initial commit - Avenue Dashboard"
git branch -M main
git remote add origin https://github.com/seu-usuario/Avenue-Dashboard.git
git push -u origin main
```

### 1.2 Copiar credenciais Looker para `.env`

```bash
cd backend
cp .env.example .env

# Editar .env com suas credenciais reais
# LOOKER_CLIENT_ID=seu_id_real
# LOOKER_CLIENT_SECRET=seu_secret_real
```

⚠️ **NÃO** fazer commit do `.env` com dados sensíveis!

---

## 🚂 Passo 2: Configurar Railway

### 2.1 Acessar Railway

1. Ir para https://railway.app
2. Clique "Login" (ou sign up se não tiver conta)
3. Conecte com GitHub

### 2.2 Criar novo projeto

1. Dashboard → "New Project"
2. Selecione "Deploy from GitHub repo"
3. Autorize o GitHub Copilot se necessário
4. Escolha seu repositório `Avenue-Dashboard`

### 2.3 Configurar serviço

Railway vai detectar automaticamente o `Procfile`. Se não:

1. Clique no projeto
2. Selecione "Settings"
3. Defina **Start Command**:
   ```
   cd backend && gunicorn -w 1 -b 0.0.0.0:$PORT api:app
   ```

### 2.4 Adicionar variáveis de ambiente

No painel do Railway:

1. Vá para a aba **Variables**
2. Adicione:

```
LOOKER_CLIENT_ID=seu_client_id_real
LOOKER_CLIENT_SECRET=seu_client_secret_real
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://seu-frontend.vercel.app,http://localhost:5173
```

### 2.5 Deploy

Railway faz deploy automaticamente quando você faz `push` no GitHub.

Você pode:

- ✅ Ver logs em tempo real
- ✅ Reiniciar o serviço
- ✅ Ver a URL pública do seu backend

A URL será parecida com: `https://avenue-dashboard-prod.up.railway.app`

---

## 🌐 Passo 3: Conectar Frontend no Vercel

### 3.1 Deploy do Frontend

1. Ir para https://vercel.com
2. "New Project"
3. Selecione seu repositório GitHub
4. Configure:
   - **Framework**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `bun install && bun run build`
   - **Output Directory**: `dist`

### 3.2 Variáveis de ambiente no Vercel

Na aba **Environment Variables**, adicione:

```
VITE_API_URL=https://sua-url-railway.up.railway.app
```

---

## ⏰ Passo 4: Agendar Pipelines Diários

Criar `.github/workflows/daily-pipeline.yml`:

```yaml
name: Daily Data Update

on:
  schedule:
    - cron: "0 9 * * *" # 9 AM UTC todo dia
  workflow_dispatch: # Permite disparo manual

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt

      - name: Run PL Pipeline
        env:
          LOOKER_CLIENT_ID: ${{ secrets.LOOKER_CLIENT_ID }}
          LOOKER_CLIENT_SECRET: ${{ secrets.LOOKER_CLIENT_SECRET }}
        run: |
          cd backend
          python pipelines/PL_Prunus_Atualizar.py

      - name: Commit and push updates
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add backend/data/
          git commit -m "Update data - $(date)" || true
          git push
```

### 4.1 Configurar Secrets no GitHub

1. Ir para **Settings** → **Secrets and variables** → **Actions**
2. Clique "New repository secret"
3. Adicione:
   - `LOOKER_CLIENT_ID`
   - `LOOKER_CLIENT_SECRET`

---

## 🧪 Teste Local Antes de Fazer Deploy

### Backend

```bash
cd backend
pip install -r requirements.txt
python api.py
# Deve rodar em http://localhost:5000
```

### Frontend

```bash
cd frontend
bun install
VITE_API_URL=http://localhost:5000 bun dev
# Deve rodar em http://localhost:5173
```

Acesse http://localhost:5173 e verifique se os gráficos carregam.

---

## 📊 URLs Finais

- **Frontend**: `https://seu-projeto.vercel.app`
- **Backend**: `https://avenue-dashboard-prod.up.railway.app`
- **API**: `https://avenue-dashboard-prod.up.railway.app/api/pl/total`

---

## 🆘 Troubleshooting

### ❌ Backend não conecta ao Looker

Verifique:

1. `LOOKER_CLIENT_ID` e `LOOKER_CLIENT_SECRET` estão corretos?
2. As credenciais foram adicionadas em **Variables** no Railway?

### ❌ Frontend não carrega dados

Verifique:

1. `VITE_API_URL` aponta para a URL correta do Railway?
2. CORS está habilitado no backend?
3. Abra Developer Tools (F12) e veja os erros de rede

### ❌ GitHub Actions não executa

Verifique:

1. O workflow file está em `.github/workflows/daily-pipeline.yml`?
2. Os secrets foram adicionados em Settings → Secrets?

---

## 💰 Custos Estimados

| Serviço   | Preço       | Limite             |
| --------- | ----------- | ------------------ |
| Railway   | $5/mês      | 500h CPU + 5GB RAM |
| Vercel    | Gratuito    | ✅                 |
| GitHub    | Gratuito    | ✅                 |
| **TOTAL** | **~$5/mês** | ✅                 |

---

## 📝 Checklist Final

- [ ] Repositório GitHub criado e com código atualizado
- [ ] `.env.example` com placeholder de credenciais
- [ ] `requirements.txt` com gunicorn
- [ ] `Procfile` criado
- [ ] Dockerfile criado
- [ ] Railway conectado ao GitHub
- [ ] Variáveis de ambiente no Railway
- [ ] Frontend deployado no Vercel
- [ ] `VITE_API_URL` atualizado no Vercel
- [ ] GitHub Actions workflow criado
- [ ] Secrets do GitHub configurados
- [ ] Testes locais passando

🎉 Pronto para deployment em produção!
