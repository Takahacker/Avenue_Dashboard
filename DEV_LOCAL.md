# 🚀 Avenue Dashboard - Development Guide

## ⚡ Quick Start (Modo Fácil)

Iniciar Tudo em Um Comando:

```bash
./dev_new.sh
```

Abre automaticamente:

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173

Abra o navegador em http://localhost:5173 e pronto! 🎉

---

## 📁 Scripts Disponíveis

```bash
./backend.sh           # Backend dev na porta 8000
./frontend.sh          # Frontend dev na porta 5173
./dev_new.sh           # Ambos simultaneamente
```

---

## Setup Manual

### 1. Copiar env.development

```bash
cp .env.development .env
```

### 2. Terminal 1 - Backend (Porta 8000)

```bash
./backend.sh 8000
```

URLs:

- API: http://localhost:8000
- Health: http://localhost:8000/api/health

### 3. Terminal 2 - Frontend (Porta 5173)

```bash
./frontend.sh 5173
```

URL: http://localhost:5173

---

## 🌐 API Endpoints (Dev)

```
GET  http://localhost:8000/api/health
GET  http://localhost:8000/api/bankers/captacao
GET  http://localhost:8000/api/metrics
```

---

## 🔄 Hot Reload

- **Backend**: Mudanças em app.py recarregam automaticamente
- **Frontend**: Mudanças em src/ recarregam no navegador (Vite HMR)

---

## 🧪 Testar

```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/bankers/captacao | jq .
```

---

## 🐛 Troubleshooting

Porta 8000 em uso:

```bash
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

Porta 5173 em uso:

```bash
lsof -i :5173 | grep -v COMMAND | awk '{print $2}' | xargs kill -9
```

Backend não responde:

```bash
tail -f /tmp/backend_dev.log
```

---

## 🚀 Production (Porta 5000)

```bash
python3 app.py
```

A **porta 5000** fica livre para produção/deploy!
