"""Servidor principal (FastAPI) para Arch-Assistant.

Este es el punto de entrada de la aplicación. Configura la aplicación FastAPI,
registra los routers de la API, habilita CORS, monta los archivos estáticos
del frontend y configura el logging global.

La lógica de negocio y los endpoints están organizados en módulos separados
para mantener el código limpio, mantenible y escalable.

Arquitectura de capas:
- Routes (python_backend/api/routes.py): Endpoints HTTP
- Gateway (python_backend/api/gateway.py): Validación, logging, manejo de errores
- Orchestrator (python_backend/server/dialogue_orchestrator/): Orquestación de flujo
- LLM Service & Recommendation Engine: Servicios especializados
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Importar configuración de logging centralizada
from python_backend.config import setup_logging, get_logger
from python_backend.api import router

# Configurar logging global PRIMERO
setup_logging(debug_mode=False)
logger = get_logger(__name__)

# Cargar variables de entorno
load_dotenv()

# Crear instancia de la aplicación
app = FastAPI(
    title='Arch-Assistant',
    version='1.0.0',
    description='API para el asistente de recomendación de arquitecturas de software'
)

logger.info("Inicializando Arch-Assistant API...")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
logger.info("CORS habilitado para todos los orígenes")

# Registrar routers de la API
app.include_router(router)
logger.info("Routers de API registrados")

# Configurar directorio de archivos estáticos
public_dir = os.path.join(os.path.dirname(__file__), 'public')

# Montar archivos estáticos del frontend
app.mount(
    '/',
    StaticFiles(directory=public_dir, html=True),
    name='static'
)
logger.info(f"Archivos estáticos montados desde: {public_dir}")
logger.info("Arch-Assistant API lista para recibir solicitudes")


if __name__ == '__main__':
    import uvicorn
    
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    print(f'Servidor Arch-Assistant iniciando en http://localhost:{PORT}')
    uvicorn.run(app, host=HOST, port=PORT)
