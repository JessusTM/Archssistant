"""Servidor principal (FastAPI) para Arch-Assistant.

Este módulo expone:
- Un endpoint HTTP `POST /api/chat` para gestionar la conversación.
- El montaje de archivos estáticos (frontend) desde `public/`.

Flujo general:
1) El frontend envía un historial de conversación (lista de mensajes).
2) Este servidor delega el procesamiento al orquestador (`handle_message`).
3) Devuelve un objeto JSON con `response` y `state` para que el frontend actualice UI.
"""

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
    """Modelo de request para el endpoint de chat.

    Attributes:
        history: Lista ordenada de mensajes de la conversación. Cada mensaje es un
            diccionario (o estructura equivalente) con al menos:
            - `role`: str (p.ej. "user", "assistant", o "user_description")
            - `content`: str (texto del mensaje)

            El orquestador también puede adjuntar `state` en mensajes del asistente.
            Este backend valida que `history` sea una lista; el contenido interno se
            valida de forma tolerante en el orquestador.
    """

    history: list


@app.post('/api/chat')
async def chat(request: ChatRequest):
    """Procesa el último mensaje del usuario y responde como asistente.

    Args:
        request: Cuerpo JSON validado por Pydantic. Debe contener `history` como una
            lista con el historial completo de la conversación en orden cronológico.
            Se asume que el último elemento corresponde al mensaje actual del usuario.

    Behavior:
        - Valida que `request.history` sea una lista.
        - Delega el flujo conversacional al orquestador `handle_message(history)`.
        - Traduce errores de autenticación de LLM a un `HTTP 401`.
        - En errores inesperados, responde con `HTTP 500`.

    Returns:
        dict: Respuesta JSON con la forma:
            {
              "response": {"role": "assistant", "content": "...", ...},
              "state": {"inferredParams": {...}, "status": "...", ...}
            }
            El contenido exacto depende del estado de la entrevista (preguntas) o de
            la fase de recomendación (incluye `recommendation`).

    Raises:
        HTTPException:
            - 400 si `history` no es una lista.
            - 401 si falta/es inválida la API key del proveedor LLM.
            - 500 para fallos internos no controlados.
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