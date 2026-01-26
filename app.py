"""
Wrapper para rodar a API do backend na raiz
"""

import sys
import os

# Adiciona backend ao path para importar o módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from api import app

if __name__ == "__main__":
    app.run()
