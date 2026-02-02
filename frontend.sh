#!/bin/bash

# Frontend Development Server Script
# Roda o Vite dev server na porta 5173 por padrão
# Pode passar uma porta diferente como argumento

set -e

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
PORT=${1:-5173}

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Avenue Dashboard - Frontend Dev Server    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if bun or npm is available
if command -v bun &> /dev/null; then
    PACKAGE_MANAGER="bun"
    echo -e "${GREEN}✓${NC} Bun encontrado"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
    echo -e "${GREEN}✓${NC} NPM encontrado"
else
    echo -e "${YELLOW}❌ Nem Bun nem NPM encontrados${NC}"
    echo "Instale um deles e tente novamente"
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo ""
    echo -e "${BLUE}📦 Instalando dependências...${NC}"
    $PACKAGE_MANAGER install
    echo -e "${GREEN}✓${NC} Dependências instaladas"
fi

# Set environment variable for backend port
export VITE_API_URL="http://localhost:8000"

echo ""
echo -e "${BLUE}🚀 Iniciando servidor...${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "  🌐 Frontend:    ${GREEN}http://localhost:$PORT${NC}"
echo -e "  🔗 Backend API: ${GREEN}http://localhost:8000/api${NC}"
echo -e "  📝 Edite files em: ${BLUE}./frontend/src${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Pressione Ctrl+C para parar o servidor${NC}"
echo ""

# Run dev server
$PACKAGE_MANAGER run dev -- --port $PORT
