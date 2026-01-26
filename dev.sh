#!/bin/bash

# Script para rodar Avenue Dashboard em desenvolvimento

echo "=================================="
echo "Avenue Dashboard - Development Mode"
echo "=================================="

# Verificar se .env existe
if [ ! -f .env ]; then
    echo "⚠️  Arquivo .env não encontrado. Criando a partir de .env.example..."
    cp .env.example .env
    echo "✓ Arquivo .env criado. Configure suas credenciais Looker!"
fi

# Terminal 1: Backend
echo ""
echo "1️⃣  Iniciando Backend (Python Flask)..."
echo "   URL: http://localhost:5000"
echo ""

# Verificar se requirements está instalado
python3 -c "import flask" 2>/dev/null || {
    echo "   Instalando dependências Python..."
    pip install -r requirements.txt
}

# Rodar Flask em desenvolvimento
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
python3 -m flask run --port=5000 &
BACKEND_PID=$!

sleep 2

# Terminal 2: Frontend
echo ""
echo "2️⃣  Iniciando Frontend (React + Vite)..."
echo "   URL: http://localhost:5173"
echo ""

cd frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "   Instalando dependências Node..."
    if command -v bun &> /dev/null; then
        bun install
    else
        npm install
    fi
fi

# Rodar Vite dev server
if command -v bun &> /dev/null; then
    bun run dev
else
    npm run dev
fi
FRONTEND_PID=$!

# Capturar Ctrl+C para limpar ambos processos
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '\n\n✓ Ambiente de desenvolvimento finalizado.'" EXIT

wait
