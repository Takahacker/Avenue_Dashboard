#!/bin/bash

# Development Environment Setup
# Inicia backend (porta 8000) e frontend (porta 5173) simultaneamente

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      Avenue Dashboard - Dev Environment    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function para cleanup ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Encerrando servidores...${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Servidores encerrados"
    exit 0
}

# Trap para Ctrl+C
trap cleanup SIGINT SIGTERM

# Kill any existing processes on ports 8000 and 5173
echo -e "${BLUE}🔍 Verificando portas em uso...${NC}"
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 8000 em uso, encerrando processo antigo...${NC}"
    lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    sleep 1
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 5173 em uso, encerrando processo antigo...${NC}"
    lsof -i :5173 | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo ""
echo -e "${BLUE}🚀 Iniciando servidores...${NC}"
echo ""

# Start backend
echo -e "${YELLOW}[1/2]${NC} Iniciando backend na porta 8000..."
cd "$SCRIPT_DIR"
PORT=8000 FLASK_ENV=development python3 app.py > /tmp/backend_dev.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓${NC} Backend iniciado (PID: $BACKEND_PID)"

sleep 3

# Check backend health
if curl -s http://localhost:8000/api/health | grep -q "ok"; then
    echo -e "${GREEN}✓${NC} Backend respondendo corretamente"
else
    echo -e "${RED}✗${NC} Backend não respondendo"
    echo "Logs:"
    tail -20 /tmp/backend_dev.log
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""

# Start frontend
echo -e "${YELLOW}[2/2]${NC} Iniciando frontend na porta 5173..."
cd "$SCRIPT_DIR/frontend"
$SCRIPT_DIR/frontend.sh &
FRONTEND_PID=$!
echo -e "${GREEN}✓${NC} Frontend iniciado (PID: $FRONTEND_PID)"

echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  ${GREEN}✓ Backend:${NC}  http://localhost:8000"
echo -e "  ${GREEN}✓ Frontend:${NC} http://localhost:5173"
echo -e "  ${GREEN}✓ API:${NC}      http://localhost:8000/api"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Abra http://localhost:5173 no navegador${NC}"
echo -e "${YELLOW}Pressione Ctrl+C para parar ambos os servidores${NC}"
echo ""

# Wait for processes
wait
