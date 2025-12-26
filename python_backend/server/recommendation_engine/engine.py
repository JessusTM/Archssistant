# server/recommendation_engine/engine.py

from .architecture_data import architectures, VALUE_MAP

def get_recommendation(user_answers):
    """
    Calcula la recomendación de arquitectura basada en los parámetros inferidos del usuario.
    Retorna las 3 mejores arquitecturas ordenadas por puntuación.
    """
    scored_architectures = []
    
    for arch in architectures:
        score = 0
        for parameter, user_answer in user_answers.items():
            arch_value = arch.get(parameter)
            user_score = VALUE_MAP.get(user_answer)
            arch_score = VALUE_MAP.get(arch_value)
            
            if user_score and arch_score:
                difference = abs(user_score - arch_score)
                if difference == 0:
                    score += 2
                elif difference == 1:
                    score += 1
        
        scored_architectures.append({**arch, 'score': score})
    
    scored_architectures.sort(key=lambda x: x['score'], reverse=True)
    return scored_architectures[:3]
