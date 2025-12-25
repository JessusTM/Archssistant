# main.py - Servidor principal con FastAPI

import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from server.dialogue_orchestrator import handle_message
from server.llm_service.llm_service import ApiKeyError

load_dotenv()

app = FastAPI(title='Arch-Assistant', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

public_dir = os.path.join(os.path.dirname(__file__), '..', 'public')


class ChatRequest(BaseModel):
    history: list


@app.post('/api/chat')
async def chat(request: ChatRequest):
    """
    Maneja un mensaje de usuario y retorna la respuesta del asistente.
    """
    try:
        if not isinstance(request.history, list):
            raise HTTPException(
                status_code=400,
                detail='El historial de la conversación es obligatorio y debe ser un array.'
            )
        
        result = await handle_message(request.history)
        return result
    
    except ApiKeyError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail='Error interno al procesar el mensaje.'
        )


app.mount(
    '/',
    StaticFiles(directory=public_dir, html=True),
    name='static'
)


if __name__ == '__main__':
    import uvicorn
    
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    print(f'Servidor Arch-Assistant iniciando en http://localhost:{PORT}')
    uvicorn.run(app, host=HOST, port=PORT)