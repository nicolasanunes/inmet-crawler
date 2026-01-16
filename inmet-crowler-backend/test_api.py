#!/usr/bin/env python3
"""
Script de exemplo para testar as rotas da API
"""
import requests
from datetime import datetime, timedelta

# URL base da API
BASE_URL = "http://localhost:8000"


def test_auto_download():
    """
    Testa a rota de download automático
    """
    print("=" * 60)
    print("Testando download automático...")
    print("=" * 60)
    
    # Data de ontem
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Faz a requisição
    url = f"{BASE_URL}/csv/auto-download"
    params = {
        "station_code": "A569",
        "date": yesterday
    }
    
    print(f"\nFazendo requisição para: {url}")
    print(f"Parâmetros: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Sucesso!")
            print(f"\nArquivo: {data.get('filename')}")
            print(f"Fonte: {data.get('source')}")
            print(f"Estação: {data.get('station_code')}")
            print(f"\nDados:")
            print(f"  - Temp. Máxima: {data.get('temp_max')}°C")
            print(f"  - Temp. Mínima: {data.get('temp_min')}°C")
            print(f"  - Temp. Média: {data.get('temp_med')}°C")
            print(f"  - Umidade Máx: {data.get('umidade_max')}%")
            print(f"  - Umidade Mín: {data.get('umidade_min')}%")
            print(f"  - ETo: {data.get('eto')} mm/dia")
        else:
            print(f"\n✗ Erro: {response.status_code}")
            print(f"Mensagem: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("\n✗ Erro: Não foi possível conectar à API")
        print("Certifique-se de que o servidor está rodando (python run.py)")
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")


def test_list_stations():
    """
    Testa a rota de listagem de estações
    """
    print("\n" + "=" * 60)
    print("Testando listagem de estações...")
    print("=" * 60)
    
    url = f"{BASE_URL}/csv/stations"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Sucesso!")
            print(f"\nEstações disponíveis:")
            for station in data.get('stations', []):
                print(f"  - {station['code']}: {station['name']}")
            print(f"\nEstação padrão: {data.get('default')}")
        else:
            print(f"\n✗ Erro: {response.status_code}")
    
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")


def test_health():
    """
    Testa se a API está rodando
    """
    print("=" * 60)
    print("Testando conexão com a API...")
    print("=" * 60)
    
    url = f"{BASE_URL}/"
    
    try:
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("\n✓ API está rodando!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"\n✗ Erro: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print("\n✗ API não está rodando")
        print("Execute: python run.py")
        return False
    except Exception as e:
        print(f"\n✗ Erro: {str(e)}")
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TESTE DA API INMET CRAWLER" + " " * 21 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    # Testa se a API está rodando
    if not test_health():
        print("\n❌ Não é possível continuar os testes.")
        exit(1)
    
    # Testa listagem de estações
    test_list_stations()
    
    # Testa download automático
    test_auto_download()
    
    print("\n" + "=" * 60)
    print("Testes concluídos!")
    print("=" * 60 + "\n")
