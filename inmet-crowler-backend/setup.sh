#!/bin/bash
# Script de setup rápido para o projeto INMET Crawler

echo "=================================================="
echo "  INMET Crawler - Setup Automático"
echo "=================================================="
echo ""

# Verifica se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script no diretório inmet-crowler-backend"
    exit 1
fi

# Ativa ambiente virtual se existir
if [ -d "venv" ]; then
    echo "✓ Ativando ambiente virtual..."
    source venv/bin/activate
else
    echo "⚠️ Ambiente virtual não encontrado. Crie com: python -m venv venv"
    exit 1
fi

# Instala dependências Python
echo ""
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

# Verifica se a instalação foi bem-sucedida
if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar dependências Python"
    exit 1
fi

# Instala navegadores do Playwright
echo ""
echo "🎭 Instalando navegadores do Playwright..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Erro ao instalar Playwright"
    echo "Tente instalar dependências do sistema:"
    echo "  sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0"
    echo "  playwright install-deps chromium"
    exit 1
fi

# Cria diretório de downloads
echo ""
echo "📁 Criando diretório de downloads..."
mkdir -p downloads

echo ""
echo "=================================================="
echo "  ✅ Setup concluído com sucesso!"
echo "=================================================="
echo ""
echo "Para iniciar o servidor:"
echo "  python run.py"
echo ""
echo "Para testar a API:"
echo "  python test_api.py"
echo ""
echo "Documentação interativa:"
echo "  http://localhost:8000/docs"
echo ""
