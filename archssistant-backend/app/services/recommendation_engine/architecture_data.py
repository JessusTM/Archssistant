"""Base data for the recommendation engine.

This module contains:
- `architectures`: list of known architectures with their categorical values per parameter.
- `VALUE_MAP`: mapping of categorical values to a numeric scale for comparison.

This data is consumed by `recommendation_engine.engine.get_recommendation`.
"""

architectures = [
    {
        'name'              : 'Arquitectura Monolítica',
        'complexity'        : 'Baja',
        'scalability'       : 'Baja',
        'teamExperience'    : 'Baja',
        'dataVolume'        : 'Moderado',
        'teamSize'          : 'Pequeño',
        'availability'      : 'Baja',
        'maintainability'   : 'Baja',
        'interoperability'  : 'Baja'
    },
    {
        'name'              : 'Arquitectura de Microservicios',
        'complexity'        : 'Alta',
        'scalability'       : 'Alta',
        'teamExperience'    : 'Alta',
        'dataVolume'        : 'Alto',
        'teamSize'          : 'Grande',
        'availability'      : 'Excelente',
        'maintainability'   : 'Alta',
        'interoperability'  : 'Excelente'
    },
    {
        'name'              : 'Arquitectura Orientada a Servicios (SOA)',
        'complexity'        : 'Alta',
        'scalability'       : 'Moderada',
        'teamExperience'    : 'Alta',
        'dataVolume'        : 'Alto',
        'teamSize'          : 'Grande',
        'availability'      : 'Alta',
        'maintainability'   : 'Alta',
        'interoperability'  : 'Excelente'
    },
    {
        'name'              : 'Arquitectura de Capas',
        'complexity'        : 'Alta',
        'scalability'       : 'Moderada',
        'teamExperience'    : 'Moderada',
        'dataVolume'        : 'Moderado',
        'teamSize'          : 'Moderado',
        'availability'      : 'Moderada',
        'maintainability'   : 'Alta',
        'interoperability'  : 'Moderada'
    },
    {
        'name'              : 'Arquitectura Cliente-Servidor',
        'complexity'        : 'Moderada',
        'scalability'       : 'Alta',
        'teamExperience'    : 'Moderada',
        'dataVolume'        : 'Alto',
        'teamSize'          : 'Moderado',
        'availability'      : 'Moderada',
        'maintainability'   : 'Moderada',
        'interoperability'  : 'Moderada'
    },
    {
        'name'              : 'Arquitectura en la Nube',
        'complexity'        : 'Alta',
        'scalability'       : 'Excelente',
        'teamExperience'    : 'Alta',
        'dataVolume'        : 'Alto',
        'teamSize'          : 'Alto',
        'availability'      : 'Excelente',
        'maintainability'   : 'Excelente',
        'interoperability'  : 'Excelente'
    },
    {
        'name'              : 'Arquitectura Basada en Eventos (EDA)',
        'complexity'        : 'Alta',
        'scalability'       : 'Alta',
        'teamExperience'    : 'Alta',
        'dataVolume'        : 'Excelente',
        'teamSize'          : 'Moderado',
        'availability'      : 'Alta',
        'maintainability'   : 'Moderada',
        'interoperability'  : 'Excelente'
    }
]

# Mapeo de valores (escala de 1-5) para comparar respuestas del usuario
VALUE_MAP = {
    'Baja'      : 1,
    'Pequeño'   : 2,
    'Moderado'  : 3,
    'Moderada'  : 3,
    'Alta'      : 4,
    'Grande'    : 4,
    'Alto'      : 4,
    'Excelente' : 5
}