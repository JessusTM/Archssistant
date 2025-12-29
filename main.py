"""Servidor principal (FastAPI) para Arch-Assistant.

Este es el punto de entrada de la aplicación. Configura la aplicación FastAPI,
registra los routers de la API, habilita CORS y monta los archivos estáticos
del frontend.

La lógica de negocio y los endpoints están organizados en módulos separados
para mantener el código limpio, mantenible y escalable.
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from python_backend.api import router

# Cargar variables de entorno
load_dotenv()

# Crear instancia de la aplicación
app = FastAPI(
    title='Arch-Assistant',
    version='1.0.0',
    description='API para el asistente de recomendación de arquitecturas de software'
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Registrar routers de la API
app.include_router(router)

# Configurar directorio de archivos estáticos
public_dir = os.path.join(os.path.dirname(__file__), 'public')

# Montar archivos estáticos del frontend
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
