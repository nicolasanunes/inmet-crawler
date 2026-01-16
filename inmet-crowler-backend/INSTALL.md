# Guia de Instalação - INMET Crawler

## Passo 1: Instalar Dependências

Ative o ambiente virtual e instale as dependências:

```bash
cd inmet-crowler-backend
source venv/bin/activate  # No Linux/Mac
# ou
venv\Scripts\activate  # No Windows

pip install -r requirements.txt
```

## Passo 2: Instalar Navegadores do Playwright

Após instalar as dependências, instale os navegadores necessários:

```bash
playwright install chromium
```

Isso baixará o navegador Chromium necessário para o scraper funcionar.

## Passo 3: Executar o Servidor

Inicie o servidor FastAPI:

```bash
python run.py
```

Ou com uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

O servidor estará disponível em: `http://localhost:8000`

## Passo 4: Testar a API

### Opção 1: Usar o script de teste

```bash
python test_api.py
```

### Opção 2: Acessar a documentação interativa

Abra no navegador: `http://localhost:8000/docs`

### Opção 3: Testar com curl

**Testar download automático:**
```bash
curl -X GET "http://localhost:8000/csv/auto-download"
```

**Testar com data específica:**
```bash
curl -X GET "http://localhost:8000/csv/auto-download?date=2026-01-15"
```

**Testar upload manual:**
```bash
curl -X POST "http://localhost:8000/csv/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@seu_arquivo.csv"
```

## Rotas Disponíveis

1. **GET /** - Health check
2. **GET /csv/stations** - Lista estações disponíveis
3. **GET /csv/auto-download** - Download automático do CSV
4. **POST /csv/upload** - Upload manual do CSV

## Troubleshooting

### Erro: "playwright executable doesn't exist"

Solução: Execute `playwright install chromium`

### Erro: "Failed to launch browser"

Solução no Linux: Instale dependências do sistema:
```bash
sudo apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2
```

Ou simplesmente:
```bash
playwright install-deps chromium
```

### Erro: "Connection refused"

Verifique se o servidor está rodando. Execute `python run.py`

### Erro ao baixar CSV

Verifique:
- Se a data é válida (não pode ser futura)
- Se o código da estação existe
- Se há conexão com a internet
- Se o site do INMET está acessível

## Estrutura de Resposta

```json
{
  "filename": "inmet_A569_20260115.csv",
  "source": "auto_download",
  "station_code": "A569",
  "download_date": "2026-01-16T10:30:00",
  "temp_max": 32.5,
  "temp_min": 18.2,
  "temp_med": 25.35,
  "umidade_max": 85.0,
  "umidade_min": 45.0,
  "soma_radiacao": 25000.0,
  "vel_media_vento": 2.5,
  "dia_juliano": 15,
  "rs": 25.0,
  "dr": 1.0323,
  "delta": -0.3856,
  "phi": -0.3392,
  "ws": 1.5932,
  "ra": 35.67,
  "rso": 27.68,
  "es": 2.486,
  "ea": 1.645,
  "rnl": 3.21,
  "rns": 19.25,
  "rn": 16.04,
  "delta_vapor": 0.189,
  "pa": 93.24,
  "gamma": 0.062,
  "u2": 1.89,
  "eto": 4.52
}
```

## Próximos Passos

- Adicionar mais estações meteorológicas
- Implementar cache de downloads
- Adicionar autenticação
- Criar interface web para visualização
