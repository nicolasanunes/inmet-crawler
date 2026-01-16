import uvicorn
from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
