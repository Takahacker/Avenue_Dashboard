#!/bin/bash

# Backend Development Server Script
# Roda o servidor na porta 8000 para desenvolvimento local
# Mantém a porta 5000 livre para produção/deploy

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
PORT=${1:-8000}

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    Avenue Dashboard - Backend Dev Server   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python3 não encontrado${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python3 encontrado: $(python3 --version)"

# Check if running on port
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta $PORT já está em uso${NC}"
    read -p "Deseja matar o processo em uso? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        lsof -i :$PORT | grep -v COMMAND | awk '{print $2}' | xargs kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✓${NC} Processo antigo finalizado"
    else
        echo -e "${YELLOW}Abortando...${NC}"
        exit 1
    fi
fi

# Set environment variables
export FLASK_ENV=development
export PORT=$PORT
export FLASK_APP=app.py

cd "$PROJECT_ROOT"

# Install dependencies if needed
if [ ! -f "backend/requirements.txt" ]; then
    echo -e "${YELLOW}⚠️  requirements.txt não encontrado${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📦 Instalando dependências...${NC}"
python3 -m pip install -q -r backend/requirements.txt --break-system-packages 2>/dev/null || \
python3 -m pip install -q -r backend/requirements.txt 2>/dev/null || \
true

echo -e "${GREEN}✓${NC} Dependências prontas"
echo ""

# Show info
echo -e "${BLUE}🚀 Iniciando servidor...${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  🌐 URL:     ${GREEN}http://localhost:$PORT${NC}"
echo -e "  📡 API:     ${GREEN}http://localhost:$PORT/api${NC}"
echo -e "  💚 Health:  ${GREEN}http://localhost:$PORT/api/health${NC}"
echo -e "  🏦 Bankers: ${GREEN}http://localhost:$PORT/api/bankers/captacao${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar o servidor${NC}"
echo ""

# Run the server
python3 app.py
