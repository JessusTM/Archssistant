# server/dialogue_orchestrator/orchestrator.py

from server.llm_service import interpret_user_answer, generate_next_question, generate_final_descriptions
from server.recommendation_engine import get_recommendation

ALL_PARAMETERS = [
    'complexity', 'scalability', 'teamExperience', 'dataVolume',
    'teamSize', 'availability', 'maintainability', 'interoperability'
]


def get_conversation_state(history):
    """
    Extrae el estado actual de la conversación del historial.
    El estado contiene los parámetros ya inferidos y el último estado conocido.
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


async def handle_message(history):
    """
    Maneja un mensaje del usuario y retorna la respuesta del asistente.
    Este es el punto de entrada principal del orquestador.
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
            
            interpretation_result = await interpret_user_answer(
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
            
            next_question = await generate_next_question(
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
        descriptions = await generate_final_descriptions(
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
