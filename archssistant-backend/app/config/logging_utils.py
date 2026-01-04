"""Utilidades de logging para Arch-Assistant.

Proporciona decoradores y funciones auxiliares para logging automático:
- Decorador @log_function_call para rastrear ejecución de funciones
- Decorador @log_performance para medir tiempo de ejecución
- Funciones para loguear eventos específicos del dominio
"""

import logging
import functools
import time
from typing import Callable, Any

from .logging_config import get_logger


def log_function_call(func: Callable) -> Callable:
    """Decorador que registra las llamadas a una función.

    Registra:
    - Entrada a la función con argumentos
    - Salida de la función con resultado
    - Excepciones si ocurren

    Example:
        @log_function_call
        def my_function(x, y):
            return x + y
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__name__
        
        logger.debug(f"Entrando en {func_name}() con args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"Saliendo de {func_name}() con resultado={result}")
            return result
        except Exception as e:
            logger.error(f"Error en {func_name}(): {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_performance(func: Callable) -> Callable:
    """Decorador que mide y registra el tiempo de ejecución de una función.

    Registra:
    - Tiempo de inicio
    - Tiempo de finalización
    - Duración total en milisegundos

    Example:
        @log_performance
        def expensive_operation():
            time.sleep(1)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        func_name = func.__name__
        
        start_time = time.time()
        logger.debug(f"[PERF] Iniciando {func_name}...")
        
        try:
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(f"[PERF] {func_name} completó en {duration_ms:.2f}ms")
            return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[PERF] {func_name} falló después de {duration_ms:.2f}ms: {str(e)}",
                exc_info=True
            )
            raise
    
    return wrapper


def log_orchestration_event(
    event_type: str,
    phase: str,
    message: str,
    extra_data: dict = None
) -> None:
    """Registra un evento de orquestación conversacional.

    Args:
        event_type: Tipo de evento ('dialogue_start', 'question_asked', 'answer_received', etc.)
        phase: Fase actual ('interviewing', 'recommendation', 'complete')
        message: Descripción legible del evento
        extra_data: Datos adicionales a loguear (parámetros, scores, etc.)

    Example:
        log_orchestration_event(
            event_type='answer_received',
            phase='interviewing',
            message='Usuario respondió pregunta sobre scalability',
            extra_data={'parameter': 'scalability', 'inferred_value': 'Alta'}
        )
    """
    logger = get_logger('orchestrator')
    data_str = f" | Data: {extra_data}" if extra_data else ""
    logger.info(f"[ORQ] {event_type.upper()} ({phase}) - {message}{data_str}")


def log_llm_call(
    operation: str,
    input_summary: str,
    output_summary: str = None,
    model: str = 'deepseek'
) -> None:
    """Registra una llamada al servicio LLM.

    Args:
        operation: Tipo de operación ('interpret', 'generate_question', 'describe')
        input_summary: Resumen del input (para debugging)
        output_summary: Resumen del output (opcional)
        model: Modelo LLM utilizado

    Example:
        log_llm_call(
            operation='interpret',
            input_summary='Usuario respondió: "Startup pequeña"',
            output_summary='Parámetro inferido: teamSize=Pequeño'
        )
    """
    logger = get_logger('llm_service')
    
    if output_summary:
        logger.info(
            f"[LLM] {operation.upper()} ({model}) | "
            f"Input: {input_summary} | Output: {output_summary}"
        )
    else:
        logger.info(f"[LLM] {operation.upper()} ({model}) | Input: {input_summary}")


def log_recommendation_event(
    stage: str,
    message: str,
    extra_data: dict = None
) -> None:
    """Registra un evento del motor de recomendación.

    Args:
        stage: Etapa del proceso ('scoring', 'ranking', 'selection')
        message: Descripción del evento
        extra_data: Datos adicionales (scores, arquitecturas, etc.)

    Example:
        log_recommendation_event(
            stage='scoring',
            message='Calculando puntajes para 5 arquitecturas',
            extra_data={'parameters_count': 8}
        )
    """
    logger = get_logger('recommendation_engine')
    data_str = f" | Data: {extra_data}" if extra_data else ""
    logger.info(f"[REC] {stage.upper()} - {message}{data_str}")


def log_api_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration_ms: float,
    message: str = None
) -> None:
    """Registra una solicitud HTTP.

    Args:
        method: Método HTTP (GET, POST, etc.)
        endpoint: Endpoint accedido
        status_code: Código de respuesta HTTP
        duration_ms: Duración de la solicitud en ms
        message: Mensaje adicional

    Example:
        log_api_request(
            method='POST',
            endpoint='/api/chat',
            status_code=200,
            duration_ms=125.5,
            message='Chat procesado exitosamente'
        )
    """
    logger = get_logger('routes')
    msg_str = f" - {message}" if message else ""
    logger.info(
        f"[API] {method} {endpoint} | Status: {status_code} | "
        f"Duration: {duration_ms:.2f}ms{msg_str}"
    )
