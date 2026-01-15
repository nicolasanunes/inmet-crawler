from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import pandas as pd
import io

router = APIRouter(prefix="/csv", tags=["CSV"])

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Faz upload e processa arquivo CSV e retorna os dados em formato JSON
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser .csv")
    
    try:
        # Lê o conteúdo do arquivo
        contents = await file.read()
        
        # Lê o CSV com pandas
        df = pd.read_csv(io.BytesIO(contents), delimiter=';', encoding='utf-8')
        
        # Converte para JSON
        data = df.to_dict(orient='records')
        
        return {
            "filename": file.filename,
            "total_rows": len(data),
            "columns": list(df.columns),
            "data": data
        }
    
    except UnicodeDecodeError:
        # Tenta com encoding latin-1 se utf-8 falhar
        try:
            df = pd.read_csv(io.BytesIO(contents), delimiter=';', encoding='latin-1')
            data = df.to_dict(orient='records')
            
            return {
                "filename": file.filename,
                "total_rows": len(data),
                "columns": list(df.columns),
                "data": data
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")