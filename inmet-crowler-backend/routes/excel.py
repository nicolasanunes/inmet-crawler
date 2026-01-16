from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

from services.csv_processor import processar_csv_inmet, ler_csv_inmet
from services.inmet_scraper import InmetScraper

router = APIRouter(prefix="/csv", tags=["CSV"])


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Faz upload manual de arquivo CSV e retorna os dados processados em formato JSON
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .csv")
    
    try:
        # Lê o conteúdo do arquivo
        contents = await file.read()
        
        # Lê o CSV com pandas
        df = ler_csv_inmet(contents)
        
        # Processa os dados
        resultado = processar_csv_inmet(df)
        resultado["filename"] = file.filename
        resultado["source"] = "manual_upload"
        
        return resultado
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")


@router.get("/auto-download")
async def auto_download_and_process(
    station_code: str = "A569",
    date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Baixa automaticamente o CSV do INMET e retorna os dados processados
    
    Args:
        station_code: Código da estação (padrão: A569)
        date: Data no formato YYYY-MM-DD (padrão: ontem)
    
    Returns:
        Dados processados do CSV
    """
    try:
        scraper = InmetScraper(headless=True)
        
        target_date = None
        if date:
            try:
                target_date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="Data deve estar no formato YYYY-MM-DD"
                )
        
        try:
            csv_path = await scraper.download_csv(station_code, target_date)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao baixar dados do INMET: {str(e)}"
            )
        
        try:
            with open(csv_path, 'rb') as f:
                contents = f.read()
            
            df = ler_csv_inmet(contents)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro ao ler arquivo baixado: {str(e)}"
            )
        
        resultado = processar_csv_inmet(df)
        resultado["filename"] = os.path.basename(csv_path)
        resultado["source"] = "auto_download"
        resultado["station_code"] = station_code
        resultado["download_date"] = datetime.now().isoformat()
        
        try:
            scraper.cleanup_old_files(days=7)
        except:
            pass
        
        return resultado
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar requisição: {str(e)}"
        )


@router.get("/stations")
async def list_stations() -> Dict[str, Any]:
    """
    Lista as estações disponíveis
    """
    return {
        "stations": [
            {
                "code": "A569",
                "name": "Brasília",
                "description": "Estação meteorológica de Brasília"
            }
        ],
        "default": "A569"
    }



