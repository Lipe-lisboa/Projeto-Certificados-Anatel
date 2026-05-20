from fastapi import FastAPI, HTTPException
from services.data_processor import DataProcessor
from services.file_manager import FileManager
from pathlib import Path
from typing import Optional

# 1. Pega o caminho de onde este arquivo .py está
CURRENT_DIR = Path(__file__).resolve().parent

# 2. Sobe dois níveis (sai de 'services', sai de 'src') para chegar na raiz
ROOT_DIR = CURRENT_DIR.parent

# 3. Define os caminhos das pastas de destino
DOCS_DIR = ROOT_DIR / "docs"
DB_PATH = ROOT_DIR / "src" /"banco.db"

processor = DataProcessor(ROOT_DIR, DOCS_DIR, DB_PATH)
file_manager = FileManager(ROOT_DIR, DOCS_DIR)

app = FastAPI()

@app.get("/carregar-dados")
def carregar_dados(
    ano:int, 
    ):
    try:

        file_manager.download_data()
        file_manager.extract_data()
        result = processor.process_and_save_to_db(ano)

        return {
            "status": result.get("status"),
            "mensagem": result.get("mensagem"),
            'status_code': result.get("status_code")
            }
    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail= {'Status': 'Fail', 'Mensagem': str(e)},
            )

   
@app.get("/certificados/{ocd_enviado}")
def certificados_ocd(ocd_enviado: str,ano:int, mes:str):
    
    try:
        result = processor.contar_certificados(ano, mes, ocd_enviado.upper())

        return {
            "status": result.get("status"),
            "mensagem": result.get("mensagem"),
            "status_code": result.get("status_code"),
            "result": result.get("result")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= {'Status': 'Fail', 'Mensagem': str(e)},
            )


@app.get("/certificados")
def certificados_ocds(ano: Optional[int] = None, mes: Optional[str] = None):
    try:
        result = processor.contar_certificados(ano, mes)

        return {
            "status": result.get("status"),
            "mensagem": result.get("mensagem"),
            "status_code": result.get("status_code"),
            "result": result.get("result")
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail= {'Status': 'Fail', 'Mensagem': str(e)},
            )