"""Orquestador de diálogo: controla el flujo conversacional end-to-end.

Responsabilidades principales:
- Mantener un `state` derivado del historial (parámetros inferidos, última pregunta, fase).
- Interpretar respuestas del usuario para inferir parámetros de arquitectura.
- Decidir cuándo pasar de entrevista (recopilación) a recomendación.
- En fase final, generar recomendaciones y enriquecerlas con descripciones del LLM.

Estructuras clave:
- `history`: lista de mensajes (dict-like) en orden cronológico. Se espera que cada
    elemento tenga `role` y `content`. El orquestador puede mutar `history` (p.ej.
    etiquetar el primer mensaje como `user_description`).
- `state`: dict persistible que el frontend vuelve a enviar dentro del historial
    (usualmente embebido en el último mensaje del asistente).
"""

from ..llm_service import interpret_user_answer, generate_next_question, generate_final_descriptions
from ..recommendation_engine import get_recommendation
from app.config import get_logger

logger = get_logger(__name__)

ALL_PARAMETERS = [
    'complexity', 'scalability', 'teamExperience', 'dataVolume',
    'teamSize', 'availability', 'maintainability', 'interoperability'
]


def get_conversation_state(history):
    """Extrae el estado conversacional desde el historial.

    Args:
        history (list[dict]): Historial completo. Se recorre desde el final buscando
            el último mensaje con `role == 'assistant'` y una clave `state`.

    Behavior:
        - Si encuentra un mensaje del asistente con `state`, devuelve ese estado.
        - Si no hay estado previo (p.ej. primera interacción), devuelve un estado
          inicial con:
            - `inferredParams`: dict vacío (parámetro -> clasificación)
            - `lastQuestion`: None
            - `isClarifying`: False
            - `status`: "interviewing"

    Returns:
        dict: Estado conversacional actual (persistible) usado por `handle_message`.

    Notes:
        Este método asume que el frontend devuelve el `state` adjunto en los mensajes
        del asistente (ver `public/script.js`). Si el estado se pierde, el sistema
        reinicia una entrevista nueva.
    """
    last_assistant_message = None
    for msg in reversed(history):
        if msg.get('role') == 'assistant':
            last_assistant_message = msg
            break
    
    if last_assistant_message:
        return last_assistant_message.get('state', {
            'inferredParams': {},
            'lastQuestion': None,
            'isClarifying': False,
            'status': 'interviewing'
        })
    
    return {
        'inferredParams': {},
        'lastQuestion': None,
        'isClarifying': False,
        'status': 'interviewing'
    }


def handle_message(history):
    """Punto de entrada principal del orquestador: procesa el historial y responde.

    Args:
        history (list[dict]): Historial de conversación. Se espera que el último
            mensaje corresponda al usuario actual (`role == 'user'` típicamente).
            Cada elemento debe proveer al menos `content`.

    Behavior:
        - Determina la descripción inicial del proyecto:
            - Busca un mensaje con `role == 'user_description'`, o
            - Usa el contenido del primer mensaje como fallback.
        - Si es la primera interacción (`len(history) == 1`), muta el historial para
          marcar el primer mensaje como `user_description`.
        - Fase "interviewing":
            - Si existe `state.lastQuestion`, interpreta la respuesta del usuario
              contra esa pregunta para inferir un parámetro.
            - Si la interpretación es "UNCERTAIN", entra en modo clarificación.
            - Si ya hay al menos 5 parámetros inferidos, cambia a "recommending".
            - Caso contrario, genera la siguiente pregunta.
        - Fase "recommending":
            - Calcula las arquitecturas recomendadas con `get_recommendation`.
            - Pide al LLM descripciones/justificaciones y las mezcla con la data base.
            - Marca el estado como "finished".
        - Fase final:
            - Devuelve un mensaje de cierre y mantiene el estado.

    Returns:
        dict: Objeto serializable con:
            - `response`: mensaje del asistente (y opcionalmente `recommendation`)
            - `state`: el estado actualizado (para persistir en el frontend)

    Side Effects:
        - Puede mutar `history` (p.ej. para etiquetar `user_description`).
        - Imprime logs de depuración en fase de recomendación.

    Raises:
        Propaga excepciones provenientes de los servicios LLM o del motor de
        recomendación. En el servidor HTTP, estas se traducen a errores 4xx/5xx.
    """
    user_message = history[-1]
    
    # Busca la descripción inicial del proyecto
    project_description = None
    for msg in history:
        if msg.get('role') == 'user_description':
            project_description = msg.get('content')
            break
    
    if not project_description:
        project_description = history[0].get('content', '')
    
    # Marca el primer mensaje como descripción del usuario
    if len(history) == 1:
        history[0]['role'] = 'user_description'
    
    state = get_conversation_state(history)
    interpretation_result = None
    
    # FASE 1: ENTREVISTA (Recopilación de parámetros)
    if state['status'] == 'interviewing':
        
        # Si ya hay una pregunta anterior, interpretar la respuesta del usuario
        if state.get('lastQuestion'):
            parameter_to_infer = state['lastQuestion'].get('parameter_to_infer')
            question_text = state['lastQuestion'].get('question_text')
            
            interpretation_result = interpret_user_answer(
                question_text,
                user_message.get('content'),
                parameter_to_infer
            )
            
            # Lógica de sub-diálogo de clarificación
            if interpretation_result.get('classification') == 'UNCERTAIN':
                state['isClarifying'] = True
            else:
                state['inferredParams'][parameter_to_infer] = interpretation_result.get('classification')
                state['isClarifying'] = False
        
        # Verificar si hemos recopilado suficientes parámetros
        inferred_count = len(state['inferredParams'])
        if inferred_count >= 5:
            state['status'] = 'recommending'
        else:
            # Generar la siguiente pregunta
            remaining_params = [p for p in ALL_PARAMETERS if p not in state['inferredParams']]
            
            next_question = generate_next_question(
                history,
                remaining_params,
                interpretation_result,
                state['isClarifying']
            )
            
            # Si estamos clarificando, mantener el mismo parámetro
            # Si no, usar el nuevo parámetro sugerido
            next_param_to_infer = (
                state['lastQuestion']['parameter_to_infer']
                if state['isClarifying']
                else next_question.get('parameter_to_infer')
            )
            
            state['lastQuestion'] = {
                'parameter_to_infer': next_param_to_infer,
                'question_text': next_question.get('question_for_user')
            }
            
            response = {
                'role': 'assistant',
                'content': next_question.get('full_response_text')
            }
            return {'response': response, 'state': state}
    
    # FASE 2: RECOMENDACIÓN
    if state['status'] == 'recommending':
        recommendations = get_recommendation(state['inferredParams'])
        
        if not recommendations:
            response = {
                'role': 'assistant',
                'content': 'No he podido determinar una recomendación con los datos proporcionados.'
            }
            state['status'] = 'finished'
            return {'response': response, 'state': state}
        
        print(f"DEBUG: Generando descripciones para {len(recommendations)} arquitecturas")
        print(f"DEBUG: Arquitecturas: {[r['name'] for r in recommendations]}")
        
        # Generar descripciones para cada arquitectura recomendada
        descriptions = generate_final_descriptions(
            project_description,
            recommendations,
            history
        )
        
        print(f"DEBUG: Descripciones recibidas con claves: {list(descriptions.keys())}")
        
        # Enriquecer las recomendaciones con descripciones y justificaciones
        enriched_recommendations = []
        for rec in recommendations:
            arch_name = rec['name']
            
            # Buscar la descripción con el nombre exacto o intentar coincidencias parciales
            desc_data = descriptions.get(arch_name)
            
            if not desc_data:
                # Intentar búsqueda case-insensitive
                for key in descriptions.keys():
                    if key.lower() == arch_name.lower():
                        desc_data = descriptions[key]
                        break
            
            if not desc_data:
                print(f"WARNING: No se encontró descripción para '{arch_name}'")
                desc_data = {}
            
            enriched_recommendations.append({
                **rec,
                'description': desc_data.get('description', 'Descripción no disponible.'),
                'justification': desc_data.get('justification', 'Justificación no disponible.')
            })
        
        response = {
            'role': 'assistant',
            'content': '¡Gracias! He analizado tus respuestas.',
            'recommendation': enriched_recommendations
        }
        state['status'] = 'finished'
        return {'response': response, 'state': state}
    
    # FASE 3: FINAL
    final_response = {
        'role': 'assistant',
        'content': 'Si tienes otro proyecto que analizar, simplemente recarga la página.'
    }
    return {'response': final_response, 'state': state}
