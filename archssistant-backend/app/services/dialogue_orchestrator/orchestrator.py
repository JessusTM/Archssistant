"""Dialogue Orchestrator: controls the end-to-end conversational flow.

Main responsibilities:
- Maintains a state derived from history (inferred parameters, last question, phase).
- Interprets user responses to infer architecture parameters.
- Decides when to transition from interview (collection) to recommendation.
- In final phase, generates recommendations and enriches them with LLM descriptions.
"""

from ..llm_service import LLMService
from ..recommendation_engine import RecommendationEngine
from app.core import get_logger


class DialogueOrchestrator:
    """Orchestrates the conversational flow for architecture recommendations.
    
    This class coordinates the dialogue between the user and the system,
    managing the state transitions from interviewing to recommending.
    """
    
    ALL_PARAMETERS = [
        'complexity', 'scalability' , 'teamExperience'  , 'dataVolume',
        'teamSize'  , 'availability', 'maintainability' , 'interoperability'
    ]
    
    def __init__(self, llm_service=None, recommendation_engine=None):
        """Initialize the Dialogue Orchestrator.
        
        Args:
            llm_service: LLMService instance (defaults to new instance if not provided)
            recommendation_engine: RecommendationEngine instance (defaults to new instance if not provided)
        """
        self.llm_service            = llm_service or LLMService()
        self.recommendation_engine  = recommendation_engine or RecommendationEngine()
        self.logger                 = get_logger(__name__)
    
    def get_conversation_state(self, history):
        """Extracts the conversational state from the history.

        Args:
            history (list[dict]): Complete history. Traversed from the end looking for
                the last message with `role == 'assistant'` and a `state` key.

        Behavior:
            - If it finds an assistant message with `state`, returns that state.
            - If there's no previous state (e.g. first interaction), returns an initial
              state with:
                - inferredParams: empty dict (parameter -> classification)
                - lastQuestion  : None
                - isClarifying  : False
                - status        : "interviewing"

        Returns:
            dict: Current conversational state (persistible) used by `handle_message`.

        Notes:
            This method assumes the frontend returns the `state` attached in assistant
            messages (see `public/script.js`). If the state is lost, the system
            restarts a new interview.
        """
        last_assistant_message = None
        for msg in reversed(history):
            if msg.get('role') == 'assistant':
                last_assistant_message = msg
                break
        
        if last_assistant_message:
            return last_assistant_message.get('state', {
                'inferredParams': {},
                'lastQuestion'  : None,
                'isClarifying'  : False,
                'status'        : 'interviewing'
            })
        
        return {
            'inferredParams': {},
            'lastQuestion'  : None,
            'isClarifying'  : False,
            'status'        : 'interviewing'
        }
    
    def handle_message(self, history):
        """Main entry point of the orchestrator: processes history and responds.

        Args:
            history (list[dict]): Conversation history. The last message is expected
                to correspond to the current user (`role == 'user'` typically).
                Each element must provide at least `content`.

        Behavior:
            - Determines the initial project description:
                - Looks for a message with `role == 'user_description'`, or
                - Uses the content of the first message as fallback.
            - If it's the first interaction (`len(history) == 1`), mutates history to
              mark the first message as `user_description`.
            - Phase "interviewing":
                - If `state.lastQuestion` exists, interprets the user's response
                  against that question to infer a parameter.
                - If interpretation is "UNCERTAIN", enters clarification mode.
                - If there are at least 5 inferred parameters, changes to "recommending".
                - Otherwise, generates the next question.
            - Phase "recommending":
                - Calculates recommended architectures with `get_recommendation`.
                - Asks LLM for descriptions/justifications and mixes them with base data.
                - Marks state as "finished".
            - Final phase:
                - Returns a closing message and maintains the state.

        Returns:
            dict: Serializable object with:
                - `response`: assistant message (and optionally `recommendation`)
                - `state`: updated state (to persist in frontend)

        Side Effects:
            - May mutate `history` (e.g. to label `user_description`).
            - Prints debug logs in recommendation phase.

        Raises:
            Propagates exceptions from LLM services or recommendation engine.
            In the HTTP server, these are translated to 4xx/5xx errors.
        """
        user_message = history[-1]
        
        # Find the initial project description
        project_description = None
        for msg in history:
            if msg.get('role') == 'user_description':
                project_description = msg.get('content')
                break
        
        if not project_description:
            project_description = history[0].get('content', '')
        
        # Mark the first message as user description
        if len(history) == 1:
            history[0]['role'] = 'user_description'
        
        state = self.get_conversation_state(history)
        interpretation_result = None
        
        # PHASE 1: INTERVIEW (Parameter collection)
        if state['status'] == 'interviewing':
            
            # If there's a previous question, interpret the user's response
            if state.get('lastQuestion'):
                parameter_to_infer = state['lastQuestion'].get('parameter_to_infer')
                question_text = state['lastQuestion'].get('question_text')
                
                interpretation_result = self.llm_service.interpret_user_answer(
                    question_text,
                    user_message.get('content'),
                    parameter_to_infer
                )
                
                # Clarification sub-dialogue logic
                if interpretation_result.get('classification') == 'UNCERTAIN':
                    state['isClarifying'] = True
                else:
                    state['inferredParams'][parameter_to_infer] = interpretation_result.get('classification')
                    state['isClarifying'] = False
            
            # Check if we've collected enough parameters
            inferred_count = len(state['inferredParams'])
            if inferred_count >= 5:
                state['status'] = 'recommending'
            else:
                # Generate the next question
                remaining_params = [p for p in self.ALL_PARAMETERS if p not in state['inferredParams']]
                
                next_question = self.llm_service.generate_next_question(
                    history,
                    remaining_params,
                    interpretation_result,
                    state['isClarifying']
                )
                
                # If clarifying, keep the same parameter
                # Otherwise, use the new suggested parameter
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
        
        # PHASE 2: RECOMMENDATION
        if state['status'] == 'recommending':
            recommendations = self.recommendation_engine.get_recommendation(state['inferredParams'])
            
            if not recommendations:
                response = {
                    'role': 'assistant',
                    'content': 'No he podido determinar una recomendación con los datos proporcionados.'
                }
                state['status'] = 'finished'
                return {'response': response, 'state': state}
            
            self.logger.debug(f"Generating descriptions for {len(recommendations)} architectures")
            self.logger.debug(f"Architectures: {[r['name'] for r in recommendations]}")
            
            # Generate descriptions for each recommended architecture
            descriptions = self.llm_service.generate_final_descriptions(
                project_description,
                recommendations,
                history
            )
            
            self.logger.debug(f"Descriptions received with keys: {list(descriptions.keys())}")
            
            # Enrich recommendations with descriptions and justifications
            enriched_recommendations = []
            for rec in recommendations:
                arch_name = rec['name']
                
                # Find description with exact name or try partial matches
                desc_data = descriptions.get(arch_name)
                
                if not desc_data:
                    # Try case-insensitive search
                    for key in descriptions.keys():
                        if key.lower() == arch_name.lower():
                            desc_data = descriptions[key]
                            break
                
                if not desc_data:
                    self.logger.warning(f"No description found for '{arch_name}'")
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
        
        # PHASE 3: FINAL
        final_response = {
            'role': 'assistant',
            'content': 'Si tienes otro proyecto que analizar, simplemente recarga la página.'
        }
        return {'response': final_response, 'state': state}
