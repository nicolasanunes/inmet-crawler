import pandas as pd
import math
from typing import Dict, Any, Optional


def converter_para_float(valor):
    """
    Converte valores com vírgula para float
    """
    if pd.isna(valor) or valor is None:
        return None
    try:
        if isinstance(valor, str):
            return float(valor.replace(',', '.'))
        return float(valor)
    except:
        return None


def processar_csv_inmet(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Processa um DataFrame do INMET e calcula todas as métricas necessárias
    
    Args:
        df: DataFrame com os dados do INMET
        
    Returns:
        Dicionário com todas as métricas calculadas
    """
    # Extrai informações solicitadas
    temp_max = None
    temp_min = None
    if 'Temp. Max. (C)' in df.columns:
        valores = df['Temp. Max. (C)'].apply(converter_para_float).dropna()
        temp_max = valores.max() if len(valores) > 0 else None
    if 'Temp. Min. (C)' in df.columns:
        valores = df['Temp. Min. (C)'].apply(converter_para_float).dropna()
        temp_min = valores.min() if len(valores) > 0 else None
    
    umidade_max = None
    umidade_min = None
    if 'Umi. Max. (%)' in df.columns:
        valores = df['Umi. Max. (%)'].apply(converter_para_float).dropna()
        umidade_max = valores.max() if len(valores) > 0 else None
    if 'Umi. Min. (%)' in df.columns:
        valores = df['Umi. Min. (%)'].apply(converter_para_float).dropna()
        umidade_min = valores.min() if len(valores) > 0 else None
    
    soma_radiacao = None
    if 'Radiacao (KJ/m²)' in df.columns:
        valores = df['Radiacao (KJ/m²)'].apply(converter_para_float).dropna()
        soma_radiacao = valores.sum() if len(valores) > 0 else None
    
    # Calcula a velocidade média do vento (soma / 24 horas)
    vel_media_vento = None
    if 'Vel. Vento (m/s)' in df.columns:
        valores = df['Vel. Vento (m/s)'].apply(converter_para_float).dropna()
        vel_media_vento = valores.sum() / 24 if len(valores) > 0 else None
    
    # Calcula o dia juliano (número do dia no ano)
    dia_juliano = None
    if 'Data' in df.columns:
        # Tenta converter a primeira data para obter o dia juliano
        try:
            primeira_data = pd.to_datetime(df['Data'].iloc[0], format='%d/%m/%Y')
            dia_juliano = primeira_data.timetuple().tm_yday
        except:
            pass
    
    # Cálculos adicionais
    temp_med = None
    rs = None
    dr = None
    delta = None
    phi = None
    ws = None
    ra = None
    rso = None
    es = None
    ea = None
    rnl = None
    rns = None
    rn = None
    delta_vapor = None
    pa = None
    gamma = None
    u2 = None
    eto = None
    
    if temp_max is not None and temp_min is not None:
        temp_med = (temp_max + temp_min) / 2
    
    if soma_radiacao is not None:
        rs = soma_radiacao / 1000
    
    if dia_juliano is not None:
        dr = 1 + 0.033 * math.cos((2 * math.pi / 365) * dia_juliano)

        delta = 0.4093 * math.sin(((2 * math.pi) / 365) * dia_juliano - 1.405)
        
        phi = -1 * math.radians(19 + (27/60) + (19/3600))
        
        ws = math.acos(-math.tan(phi) * math.tan(delta))
        
        ra = 37.6 * dr * (ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws))
    
    if temp_med is not None and ra is not None:
        rso = (0.75 + 0.00002 * 719) * ra
    
    if temp_min is not None and temp_max is not None:
        es = (0.6108 * math.exp((17.27 * temp_min) / (temp_min + 237.3)) + 
              0.6108 * math.exp((17.27 * temp_max) / (temp_max + 237.3))) / 2
    
    if temp_min is not None and temp_max is not None and umidade_max is not None and umidade_min is not None:
        ea = (0.6108 * math.exp((17.27 * temp_min) / (temp_min + 237.3)) * (umidade_max / 100) + 
              0.6108 * math.exp((17.27 * temp_max) / (temp_max + 237.3)) * (umidade_min / 100)) / 2
    
    if temp_max is not None and temp_min is not None and ea is not None and rs is not None and rso is not None:
        rnl = 0.000000004903 * (((temp_max + 273.16)**4 + (temp_min + 273.16)**4) / 2) * \
              (0.34 - 0.14 * math.sqrt(ea)) * (1.35 * (rs / rso) - 0.35)
    
    if rs is not None:
        rns = (1 - 0.23) * rs
    
    if rns is not None and rnl is not None:
        rn = rns - rnl
    
    if temp_med is not None:
        delta_vapor = (4098 * (0.6108 * math.exp((17.27 * temp_med) / (temp_med + 237.3)))) / \
                      ((temp_med + 237.3)**2)
    
    # Altitude de 719m (referência)
    pa = 101.3 * ((293 - 0.0065 * 719) / 293)**5.26
    gamma = 0.000665 * pa
    
    if vel_media_vento is not None:
        u2 = vel_media_vento * (4.87 / math.log(67.8 * 4 - 5.42))
    
    if delta_vapor is not None and rn is not None and gamma is not None and temp_med is not None and u2 is not None and es is not None and ea is not None:
        eto = (0.408 * delta_vapor * (rn - 0) + gamma * (900 / (temp_med + 273)) * u2 * (es - ea)) / \
              (delta_vapor + gamma * (1 + 0.34 * u2))
    
    return {
        "temp_max": temp_max,
        "temp_min": temp_min,
        "umidade_max": umidade_max,
        "umidade_min": umidade_min,
        "soma_radiacao": soma_radiacao,
        "vel_media_vento": vel_media_vento,
        "dia_juliano": dia_juliano,
        "temp_med": temp_med,
        "rs": rs,
        "dr": dr,
        "delta": delta,
        "phi": phi,
        "ws": ws,
        "ra": ra,
        "rso": rso,
        "es": es,
        "ea": ea,
        "rnl": rnl,
        "rns": rns,
        "rn": rn,
        "delta_vapor": delta_vapor,
        "pa": pa,
        "gamma": gamma,
        "u2": u2,
        "eto": eto
    }


def ler_csv_inmet(conteudo: bytes) -> pd.DataFrame:
    """
    Lê o CSV do INMET a partir do conteúdo em bytes
    
    Args:
        conteudo: Conteúdo do arquivo CSV em bytes
        
    Returns:
        DataFrame com os dados
        
    Raises:
        Exception: Se não conseguir ler o arquivo
    """
    import io
    
    # Tenta primeiro com UTF-8
    try:
        return pd.read_csv(io.BytesIO(conteudo), delimiter=';', encoding='utf-8')
    except UnicodeDecodeError:
        # Tenta com latin-1
        return pd.read_csv(io.BytesIO(conteudo), delimiter=';', encoding='latin-1')
