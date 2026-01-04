"""Logging utilities for Arch-Assistant.

Provides helper functions to log domain-specific events:
- log_orchestration_event: conversational orchestration events
- log_llm_call: LLM service calls
- log_recommendation_event: recommendation engine events
- log_api_request: HTTP API requests

These functions provide structured logging for better debugging and monitoring.
"""

from .logging_config import get_logger


def log_orchestration_event(
    event_type  : str,
    phase       : str,
    message     : str,
    extra_data  : dict = None
) -> None:
    """Logs a conversational orchestration event.

    Args:
        event_type  : Event type ('dialogue_start', 'question_asked', 'answer_received', etc.)
        phase       : Current phase ('interviewing', 'recommendation', 'complete')
        message     : Human-readable event description
        extra_data  : Additional data to log (parameters, scores, etc.)

    Example:
        log_orchestration_event(
            event_type  ='answer_received',
            phase       ='interviewing',
            message     ='Usuario respondió pregunta sobre scalability',
            extra_data  ={'parameter': 'scalability', 'inferred_value': 'Alta'}
        )
    """
    logger      = get_logger('orchestrator')
    data_str    = f" | Data: {extra_data}" if extra_data else ""
    logger.info(f"[ORQ] {event_type.upper()} ({phase}) - {message}{data_str}")


def log_llm_call(
    operation       : str,
    input_summary   : str,
    output_summary  : str = None,
    model           : str = 'deepseek'
) -> None:
    """Logs an LLM service call.

    Args:
        operation       : Operation type ('interpret', 'generate_question', 'describe')
        input_summary   : Input summary (for debugging)
        output_summary  : Output summary (optional)
        model           : LLM model used

    Example:
        log_llm_call(
            operation       = 'interpret',
            input_summary   = 'Usuario respondió: "Startup pequeña"',
            output_summary  = 'Parámetro inferido: teamSize=Pequeño'
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
    stage       : str,
    message     : str,
    extra_data  : dict = None
) -> None:
    """Logs a recommendation engine event.

    Args:
        stage       : Process stage ('scoring', 'ranking', 'selection')
        message     : Event description
        extra_data  : Additional data (scores, architectures, etc.)

    Example:
        log_recommendation_event(
            stage       = 'scoring',
            message     = 'Calculando puntajes para 5 arquitecturas',
            extra_data  = {'parameters_count': 8}
        )
    """
    logger      = get_logger('recommendation_engine')
    data_str    = f" | Data: {extra_data}" if extra_data else ""
    logger.info(f"[REC] {stage.upper()} - {message}{data_str}")


def log_api_request(
    method      : str,
    endpoint    : str,
    status_code : int,
    duration_ms : float,
    message     : str = None
) -> None:
    """Logs an HTTP request.

    Args:
        method      : HTTP method (GET, POST, etc.)
        endpoint    : Accessed endpoint
        status_code : HTTP response code
        duration_ms : Request duration in ms
        message     : Additional message

    Example:
        log_api_request(
            method      = 'POST',
            endpoint    = '/api/chat',
            status_code = 200,
            duration_ms = 125.5,
            message     = 'Chat procesado exitosamente'
        )
    """
    logger = get_logger('routes')
    msg_str = f" - {message}" if message else ""
    logger.info(
        f"[API] {method} {endpoint} | Status: {status_code} | "
        f"Duration: {duration_ms:.2f}ms{msg_str}"
    )