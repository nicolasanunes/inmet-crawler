# 🚀 INMET Crawler - Resumo da Implementação

## ✅ O que foi implementado

### 1. Scraper com Playwright
- **Arquivo**: `services/inmet_scraper.py`
- Acessa automaticamente a página do INMET
- Configura a data desejada (padrão: ontem)
- Faz download do arquivo CSV
- Gerencia arquivos baixados (limpeza automática após 7 dias)

### 2. Processador de CSV
- **Arquivo**: `services/csv_processor.py`
- Lógica de cálculo reutilizável
- Processa dados meteorológicos
- Calcula todas as métricas (temperatura, umidade, ETo, etc.)
- Suporta múltiplos encodings (UTF-8 e Latin-1)

### 3. Rotas da API
- **Arquivo**: `routes/excel.py`

#### Rota 1: Upload Manual (mantida)
- **Endpoint**: `POST /csv/upload`
- Permite upload manual do CSV
- Processa e retorna os dados calculados

#### Rota 2: Download Automático (nova)
- **Endpoint**: `GET /csv/auto-download`
- Baixa automaticamente o CSV do INMET
- Parâmetros opcionais:
  - `station_code`: código da estação (padrão: A569)
  - `date`: data no formato YYYY-MM-DD (padrão: ontem)
- Processa e retorna os dados calculados

#### Rota 3: Listar Estações (nova)
- **Endpoint**: `GET /csv/stations`
- Lista estações disponíveis

## 📁 Estrutura de Arquivos Criados/Modificados

```
inmet-crowler-backend/
├── requirements.txt              # ✏️ Modificado - adicionado playwright
├── routes/
│   └── excel.py                  # ♻️ Refatorado - simplificado e nova rota
├── services/                     # 🆕 Novo diretório
│   ├── __init__.py              # 🆕 Novo
│   ├── inmet_scraper.py         # 🆕 Novo - scraper com Playwright
│   └── csv_processor.py         # 🆕 Novo - lógica de cálculos
├── downloads/                    # 🆕 Criado automaticamente
├── README.md                     # 🆕 Documentação completa
├── INSTALL.md                    # 🆕 Guia de instalação
└── test_api.py                   # 🆕 Script de teste
```

## 🔧 Como Usar

### Instalação Rápida

```bash
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar navegador do Playwright
playwright install chromium

# 3. Executar servidor
python run.py
```

### Usar a API

#### Opção 1: Download Automático (Nova Funcionalidade)
```bash
# Download de ontem
curl http://localhost:8000/csv/auto-download

# Download de data específica
curl "http://localhost:8000/csv/auto-download?date=2026-01-15"
```

#### Opção 2: Upload Manual (Rota Original)
```bash
curl -X POST "http://localhost:8000/csv/upload" \
  -F "file=@arquivo.csv"
```

#### Testar com Script Python
```bash
python test_api.py
```

#### Documentação Interativa
Abra no navegador: `http://localhost:8000/docs`

## 🎯 Diferenças entre as Rotas

| Característica | Upload Manual | Download Automático |
|----------------|---------------|---------------------|
| Método HTTP | POST | GET |
| Arquivo CSV | Enviado pelo usuário | Baixado automaticamente |
| Necessita arquivo | ✅ Sim | ❌ Não |
| Data configurável | Depende do arquivo | ✅ Sim (parâmetro) |
| Estação configurável | Depende do arquivo | ✅ Sim (parâmetro) |
| Usa Playwright | ❌ Não | ✅ Sim |

## 📊 Exemplo de Resposta

Ambas as rotas retornam o mesmo formato de dados:

```json
{
  "filename": "inmet_A569_20260115.csv",
  "source": "auto_download",  // ou "manual_upload"
  "station_code": "A569",     // apenas no auto_download
  "download_date": "2026-01-16T10:30:00",  // apenas no auto_download
  "temp_max": 32.5,
  "temp_min": 18.2,
  "temp_med": 25.35,
  "umidade_max": 85.0,
  "umidade_min": 45.0,
  "soma_radiacao": 25000.0,
  "vel_media_vento": 2.5,
  "dia_juliano": 15,
  "eto": 4.52,
  // ... outros campos calculados
}
```

## 🔍 Como Funciona o Scraper

1. **Acessa a página**: `https://tempo.inmet.gov.br/TabelaEstacoes/A569`
2. **Preenche a data**: Insere a data desejada no campo de data
3. **Clica no botão CSV**: Localiza e clica no botão de download
4. **Salva o arquivo**: Armazena em `downloads/inmet_A569_YYYYMMDD.csv`
5. **Processa os dados**: Calcula todas as métricas meteorológicas
6. **Retorna JSON**: Devolve os dados processados ao usuário
7. **Limpa arquivos antigos**: Remove downloads com mais de 7 dias

## ⚠️ Observações Importantes

1. **Playwright**: Necessita instalação dos navegadores (`playwright install`)
2. **Permissões**: O diretório `downloads/` é criado automaticamente
3. **Limpeza**: Arquivos antigos são removidos automaticamente
4. **Compatibilidade**: Funciona em Linux, Mac e Windows
5. **Headless**: O navegador roda em modo invisível (sem janela)

## 🐛 Troubleshooting

### Erro ao instalar Playwright
```bash
# Linux/Ubuntu
sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0
playwright install-deps chromium

# Ou simplesmente
playwright install chromium
```

### Erro "Connection refused"
```bash
# Verifique se o servidor está rodando
python run.py
```

### Erro ao baixar CSV
- Verifique a conexão com internet
- Verifique se a data é válida (não futura)
- Verifique se o site do INMET está acessível

## 📝 Próximos Passos Sugeridos

- [ ] Adicionar mais códigos de estações
- [ ] Implementar cache para evitar downloads duplicados
- [ ] Adicionar logs detalhados
- [ ] Criar interface web
- [ ] Adicionar autenticação
- [ ] Suportar download de múltiplas datas
- [ ] Exportar dados em diferentes formatos (Excel, JSON, etc.)

---

**Desenvolvido com Python, FastAPI e Playwright** 🐍⚡🎭
