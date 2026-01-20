"""Base data for the recommendation engine.

This module contains:
- `architectures`: list of known architectures with their categorical values per parameter.
- `VALUE_MAP`: mapping of categorical values to a numeric scale for comparison.

This data is consumed by the Decision Maker component.
"""

architectures = [
    {
        'name'              : 'Monolithic Architecture',
        'complexity'        : 'Low',
        'scalability'       : 'Low',
        'teamExperience'    : 'Low',
        'dataVolume'        : 'Moderate',
        'teamSize'          : 'Small',
        'availability'      : 'Low',
        'maintainability'   : 'Low',
        'interoperability'  : 'Low'
    },
    {
        'name'              : 'Microservices Architecture',
        'complexity'        : 'High',
        'scalability'       : 'High',
        'teamExperience'    : 'High',
        'dataVolume'        : 'High',
        'teamSize'          : 'Large',
        'availability'      : 'Excellent',
        'maintainability'   : 'High',
        'interoperability'  : 'Excellent'
    },
    {
        'name'              : 'Service-Oriented Architecture (SOA)',
        'complexity'        : 'High',
        'scalability'       : 'Moderate',
        'teamExperience'    : 'High',
        'dataVolume'        : 'High',
        'teamSize'          : 'Large',
        'availability'      : 'High',
        'maintainability'   : 'High',
        'interoperability'  : 'Excellent'
    },
    {
        'name'              : 'Layered Architecture',
        'complexity'        : 'High',
        'scalability'       : 'Moderate',
        'teamExperience'    : 'Moderate',
        'dataVolume'        : 'Moderate',
        'teamSize'          : 'Moderate',
        'availability'      : 'Moderate',
        'maintainability'   : 'High',
        'interoperability'  : 'Moderate'
    },
    {
        'name'              : 'Client-Server Architecture',
        'complexity'        : 'Moderate',
        'scalability'       : 'High',
        'teamExperience'    : 'Moderate',
        'dataVolume'        : 'High',
        'teamSize'          : 'Moderate',
        'availability'      : 'Moderate',
        'maintainability'   : 'Moderate',
        'interoperability'  : 'Moderate'
    },
    {
        'name'              : 'Cloud Architecture',
        'complexity'        : 'High',
        'scalability'       : 'Excellent',
        'teamExperience'    : 'High',
        'dataVolume'        : 'High',
        'teamSize'          : 'High',
        'availability'      : 'Excellent',
        'maintainability'   : 'Excellent',
        'interoperability'  : 'Excellent'
    },
    {
        'name'              : 'Event-Driven Architecture (EDA)',
        'complexity'        : 'High',
        'scalability'       : 'High',
        'teamExperience'    : 'High',
        'dataVolume'        : 'Excellent',
        'teamSize'          : 'Moderate',
        'availability'      : 'High',
        'maintainability'   : 'Moderate',
        'interoperability'  : 'Excellent'
    }
]

VALUE_MAP = {
    'Low'       : 1,
    'Small'     : 2,
    'Moderate'  : 3,
    'High'      : 4,
    'Large'     : 4,
    'Excellent' : 5
}