# 📖 Exemplos de Uso - INMET Crawler

## 1. Download Automático (Simples)

Baixa dados de ontem automaticamente:

```bash
curl http://localhost:8000/csv/auto-download
```

**Resposta**:
```json
{
  "filename": "inmet_A569_20260115.csv",
  "source": "auto_download",
  "station_code": "A569",
  "download_date": "2026-01-16T14:30:00",
  "temp_max": 28.5,
  "temp_min": 19.2,
  "temp_med": 23.85,
  "umidade_max": 82.0,
  "umidade_min": 48.0,
  "soma_radiacao": 22450.0,
  "vel_media_vento": 2.1,
  "dia_juliano": 15,
  "eto": 4.12
}
```

---

## 2. Download Automático (Data Específica)

Baixa dados de uma data específica:

```bash
curl "http://localhost:8000/csv/auto-download?date=2026-01-10"
```

---

## 3. Download Automático (Python)

```python
import requests
from datetime import datetime, timedelta

# Data de ontem
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# Faz a requisição
response = requests.get(
    'http://localhost:8000/csv/auto-download',
    params={'date': yesterday}
)

data = response.json()

print(f"Temperatura máxima: {data['temp_max']}°C")
print(f"Temperatura mínima: {data['temp_min']}°C")
print(f"ETo: {data['eto']} mm/dia")
```

---

## 4. Upload Manual (curl)

```bash
curl -X POST "http://localhost:8000/csv/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/caminho/para/arquivo.csv"
```

---

## 5. Upload Manual (Python com requests)

```python
import requests

# Caminho do arquivo CSV
file_path = 'dados_inmet.csv'

# Abre o arquivo e faz upload
with open(file_path, 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/csv/upload',
        files=files
    )

data = response.json()
print(f"ETo: {data['eto']} mm/dia")
```

---

## 6. Upload Manual (Python com httpx - assíncrono)

```python
import httpx
import asyncio

async def upload_csv(file_path: str):
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await client.post(
                'http://localhost:8000/csv/upload',
                files=files
            )
        return response.json()

# Uso
data = asyncio.run(upload_csv('dados_inmet.csv'))
print(data)
```

---

## 7. Listar Estações Disponíveis

```bash
curl http://localhost:8000/csv/stations
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

---

## 8. Script Completo - Download Automático Diário

```python
#!/usr/bin/env python3
"""
Script para baixar dados meteorológicos diariamente
"""
import requests
from datetime import datetime, timedelta
import json
import os

def download_dados_ontem():
    """Baixa dados de ontem do INMET"""
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"Baixando dados de {yesterday}...")
    
    response = requests.get(
        'http://localhost:8000/csv/auto-download',
        params={
            'station_code': 'A569',
            'date': yesterday
        },
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Salva em arquivo JSON
        filename = f"dados_{yesterday}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Dados salvos em: {filename}")
        print(f"  - Temp. Máx: {data['temp_max']}°C")
        print(f"  - Temp. Mín: {data['temp_min']}°C")
        print(f"  - ETo: {data['eto']} mm/dia")
        
        return data
    else:
        print(f"✗ Erro: {response.status_code}")
        print(response.text)
        return None

if __name__ == '__main__':
    download_dados_ontem()
```

---

## 9. Integração com Pandas

```python
import requests
import pandas as pd
from datetime import datetime, timedelta

def obter_dados_periodo(dias: int = 7):
    """
    Baixa dados dos últimos N dias
    """
    dados = []
    
    for i in range(dias):
        date = (datetime.now() - timedelta(days=i+1)).strftime('%Y-%m-%d')
        
        try:
            response = requests.get(
                'http://localhost:8000/csv/auto-download',
                params={'date': date},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                data['date'] = date
                dados.append(data)
                print(f"✓ {date}")
            else:
                print(f"✗ {date} - Erro {response.status_code}")
        
        except Exception as e:
            print(f"✗ {date} - {str(e)}")
    
    # Cria DataFrame
    df = pd.DataFrame(dados)
    
    # Seleciona colunas principais
    df = df[[
        'date', 'temp_max', 'temp_min', 'temp_med',
        'umidade_max', 'umidade_min', 'eto'
    ]]
    
    return df

# Uso
df = obter_dados_periodo(7)
print(df)

# Salva em Excel
df.to_excel('dados_inmet_7dias.xlsx', index=False)
```

---

## 10. Agendamento com APScheduler

```python
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)

def baixar_dados_diarios():
    """Função executada diariamente"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    logging.info(f"Iniciando download de dados: {yesterday}")
    
    try:
        response = requests.get(
            'http://localhost:8000/csv/auto-download',
            params={'date': yesterday},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            logging.info(f"✓ Dados baixados - ETo: {data['eto']} mm/dia")
        else:
            logging.error(f"✗ Erro: {response.status_code}")
    
    except Exception as e:
        logging.error(f"✗ Erro: {str(e)}")

# Cria scheduler
scheduler = BlockingScheduler()

# Agenda para executar todo dia às 6h da manhã
scheduler.add_job(
    baixar_dados_diarios,
    'cron',
    hour=6,
    minute=0
)

print("Scheduler iniciado. Executará diariamente às 6h.")
print("Pressione Ctrl+C para parar.")

scheduler.start()
```

---

## 11. Teste de Performance

```python
import requests
import time

def testar_performance(n_requests: int = 10):
    """Testa performance da API"""
    
    tempos = []
    
    for i in range(n_requests):
        start = time.time()
        
        response = requests.get('http://localhost:8000/csv/auto-download')
        
        end = time.time()
        tempo = end - start
        tempos.append(tempo)
        
        print(f"Request {i+1}: {tempo:.2f}s - Status: {response.status_code}")
    
    print(f"\nTempo médio: {sum(tempos)/len(tempos):.2f}s")
    print(f"Tempo mínimo: {min(tempos):.2f}s")
    print(f"Tempo máximo: {max(tempos):.2f}s")

testar_performance(5)
```

---

## 12. Monitoramento de Erros

```python
import requests
from datetime import datetime
import time

def monitorar_api(intervalo_segundos: int = 60):
    """Monitora a disponibilidade da API"""
    
    print("Iniciando monitoramento da API...")
    print("Pressione Ctrl+C para parar.\n")
    
    while True:
        try:
            start = time.time()
            response = requests.get('http://localhost:8000/', timeout=5)
            tempo = time.time() - start
            
            if response.status_code == 200:
                status = "✓ ONLINE"
            else:
                status = f"⚠️ Status {response.status_code}"
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] {status} - Tempo: {tempo:.2f}s")
        
        except requests.exceptions.ConnectionError:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ✗ OFFLINE - Não foi possível conectar")
        
        except Exception as e:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[{timestamp}] ✗ ERRO - {str(e)}")
        
        time.sleep(intervalo_segundos)

# Executa
monitorar_api(60)  # Verifica a cada 60 segundos
```

---

## 📝 Notas

- Todos os exemplos assumem que a API está rodando em `http://localhost:8000`
- Ajuste o timeout conforme necessário (download pode levar mais tempo)
- Para produção, adicione tratamento de erros mais robusto
- Considere usar variáveis de ambiente para a URL da API
