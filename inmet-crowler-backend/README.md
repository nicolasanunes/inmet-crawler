# INMET Crawler - Documentação

## Visão Geral

O sistema agora possui duas rotas para processar dados meteorológicos do INMET:

1. **Upload Manual**: O usuário faz upload de um arquivo CSV manualmente
2. **Download Automático**: O sistema baixa o CSV automaticamente da página do INMET

## Instalação

### 1. Instalar dependências

```bash
cd inmet-crowler-backend
pip install -r requirements.txt
```

### 2. Instalar navegadores do Playwright

Após instalar o Playwright, é necessário instalar os navegadores:

```bash
playwright install chromium
```

Ou instale todos os navegadores:

```bash
playwright install
```

## Rotas Disponíveis

### 1. Upload Manual (POST `/csv/upload`)

**Descrição**: Permite ao usuário fazer upload manual de um arquivo CSV do INMET.

**Endpoint**: `POST http://localhost:8000/csv/upload`

**Exemplo com curl**:
```bash
curl -X POST "http://localhost:8000/csv/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@caminho/para/arquivo.csv"
```

**Resposta**:
```json
{
  "filename": "arquivo.csv",
  "source": "manual_upload",
  "temp_max": 32.5,
  "temp_min": 18.2,
  "umidade_max": 85.0,
  "umidade_min": 45.0,
  "soma_radiacao": 25000.0,
  "vel_media_vento": 2.5,
  "dia_juliano": 15,
  "temp_med": 25.35,
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

---

### 2. Download Automático (GET `/csv/auto-download`)

**Descrição**: Baixa automaticamente o CSV do INMET usando Playwright e processa os dados.

**Endpoint**: `GET http://localhost:8000/csv/auto-download`

**Parâmetros**:
- `station_code` (opcional): Código da estação (padrão: "A569" - Brasília)
- `date` (opcional): Data no formato YYYY-MM-DD (padrão: ontem)

**Exemplos**:

1. Baixar dados de ontem (padrão):
```bash
curl -X GET "http://localhost:8000/csv/auto-download"
```

2. Baixar dados de uma data específica:
```bash
curl -X GET "http://localhost:8000/csv/auto-download?date=2026-01-15"
```

3. Baixar dados de outra estação:
```bash
curl -X GET "http://localhost:8000/csv/auto-download?station_code=A001&date=2026-01-15"
```

**Resposta**:
```json
{
  "filename": "inmet_A569_20260115.csv",
  "source": "auto_download",
  "station_code": "A569",
  "download_date": "2026-01-16T10:30:00",
  "temp_max": 32.5,
  "temp_min": 18.2,
  ...
}
```

---

### 3. Listar Estações (GET `/csv/stations`)

**Descrição**: Lista as estações disponíveis.

**Endpoint**: `GET http://localhost:8000/csv/stations`

**Exemplo**:
```bash
curl -X GET "http://localhost:8000/csv/stations"
```

**Resposta**:
```json
{
  "stations": [
    {
      "code": "A569",
      "name": "Brasília",
      "description": "Estação meteorológica de Brasília"
    }
  ],
  "default": "A569"
}
```

## Estrutura do Projeto

```
inmet-crowler-backend/
├── app/
│   └── main.py              # Aplicação principal FastAPI
├── routes/
│   ├── excel.py             # Rotas de processamento CSV
│   └── health.py            # Rota de health check
├── services/
│   ├── inmet_scraper.py     # Scraper com Playwright
│   └── csv_processor.py     # Processamento e cálculos
├── downloads/               # Diretório de downloads (criado automaticamente)
├── requirements.txt         # Dependências
└── run.py                   # Script de execução
```

## Como Funciona o Scraper

O scraper utiliza o Playwright para:

1. Acessar a página do INMET: `https://tempo.inmet.gov.br/TabelaEstacoes/{station_code}`
2. Preencher o campo de data com a data desejada (padrão: ontem)
3. Clicar no botão de download CSV
4. Salvar o arquivo no diretório `downloads/`
5. Processar o arquivo e retornar os dados calculados
6. Limpar arquivos antigos (mantém últimos 7 dias)

## Cálculos Realizados

O sistema calcula automaticamente:

- Temperaturas (máxima, mínima, média)
- Umidade (máxima, mínima)
- Radiação solar
- Velocidade média do vento
- Dia juliano
- Evapotranspiração de referência (ETo)
- E diversos outros parâmetros meteorológicos

## Executar o Servidor

```bash
cd inmet-crowler-backend
python run.py
```

Ou com uvicorn:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em: `http://localhost:8000`

Documentação interativa: `http://localhost:8000/docs`

## Observações

- O scraper funciona em modo headless (sem interface gráfica)
- Os arquivos baixados são salvos em `downloads/` com nome: `inmet_{station_code}_{YYYYMMDD}.csv`
- Arquivos com mais de 7 dias são automaticamente removidos
- A rota de upload manual continua funcionando normalmente
