"""Módulo API para Arch-Assistant.

Este paquete contiene la definición de rutas HTTP, modelos de request/response
y la configuración de los endpoints de la aplicación.
"""

from .routes import router

__all__ = ['router']
