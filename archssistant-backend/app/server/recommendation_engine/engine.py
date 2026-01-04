"""Motor de recomendación basado en scoring.

Compara las clasificaciones inferidas del usuario con una tabla de arquitecturas
predefinidas y asigna un puntaje por similitud.
"""

from .architecture_data import architectures, VALUE_MAP

def get_recommendation(user_answers):
    """Calcula recomendaciones de arquitectura a partir de parámetros inferidos.

    Args:
        user_answers (dict[str, str]): Mapa `parametro -> clasificacion` inferida por el
            orquestador. Ejemplos de valores:
            - Para `teamSize`: "Pequeño" | "Moderado" | "Grande" | "Alto"
            - Para otros parámetros: "Baja" | "Moderada" | "Alta" | "Excelente"

    Behavior:
        - Para cada arquitectura base (ver `architecture_data.architectures`), compara
          cada parámetro presente en `user_answers`.
        - Convierte valores categóricos a escala numérica con `VALUE_MAP`.
        - Suma puntaje por cercanía:
            - diferencia 0: +2
            - diferencia 1: +1
            - diferencia >1 o valores no mapeados: +0
        - Ordena de mayor a menor puntaje.

    Returns:
        list[dict]: Hasta 3 arquitecturas (top-3), cada una como dict que incluye
            sus atributos y una clave adicional `score` (int).

    Notes:
        Este motor es determinista y no usa el LLM. Si `VALUE_MAP` no contiene algún
        valor (p.ej. entradas nuevas), ese parámetro no contribuye al puntaje.
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
