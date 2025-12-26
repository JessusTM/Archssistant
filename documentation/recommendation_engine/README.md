# Servicio: recommendation_engine

## 1) Qué es este servicio
Este servicio es el **motor de recomendación**. No habla con el LLM.

Su trabajo es:
- Tomar parámetros inferidos del usuario (ej. `scalability = Alta`, `teamSize = Pequeño`).
- Compararlos contra un catálogo de arquitecturas predefinidas.
- Calcular un puntaje por arquitectura.
- Devolver las 3 mejores.

Código:
- `python_backend/server/recommendation_engine/architecture_data.py` (datos + VALUE_MAP)
- `python_backend/server/recommendation_engine/engine.py` (algoritmo de scoring)

---

## 2) Entradas y salidas

### Entrada
La función principal es `get_recommendation(user_answers)`.

- `user_answers` es un dict de la forma:
```python
{
  "complexity": "Alta",
  "scalability": "Moderada",
  "teamSize": "Pequeño",
  ...
}
```

### Salida
Una lista con 3 arquitecturas (dict) con un campo adicional `score`:
```python
[
  {
    "name": "Arquitectura de Microservicios",
    "complexity": "Alta",
    ...,
    "score": 11
  },
  ...
]
```

---

## 3) Archivo 1: architecture_data.py (catálogo y mapa de valores)

### 3.1 Código (con números de línea)

```python
 1  # server/recommendation_engine/architecture_data.py
 2  
 3  architectures = [
 4      {
 5          'name': 'Arquitectura Monolítica',
 6          'complexity': 'Baja',
 7          'scalability': 'Baja',
 8          'teamExperience': 'Baja',
 9          'dataVolume': 'Moderado',
10          'teamSize': 'Pequeño',
11          'availability': 'Baja',
12          'maintainability': 'Baja',
13          'interoperability': 'Baja'
14      },
15      {
16          'name': 'Arquitectura de Microservicios',
17          'complexity': 'Alta',
18          'scalability': 'Alta',
19          'teamExperience': 'Alta',
20          'dataVolume': 'Alto',
21          'teamSize': 'Grande',
22          'availability': 'Excelente',
23          'maintainability': 'Alta',
24          'interoperability': 'Excelente'
25      },
26      {
27          'name': 'Arquitectura Orientada a Servicios (SOA)',
28          'complexity': 'Alta',
29          'scalability': 'Moderada',
30          'teamExperience': 'Alta',
31          'dataVolume': 'Alto',
32          'teamSize': 'Grande',
33          'availability': 'Alta',
34          'maintainability': 'Alta',
35          'interoperability': 'Excelente'
36      },
37      {
38          'name': 'Arquitectura de Capas',
39          'complexity': 'Alta',
40          'scalability': 'Moderada',
41          'teamExperience': 'Moderada',
42          'dataVolume': 'Moderado',
43          'teamSize': 'Moderado',
44          'availability': 'Moderada',
45          'maintainability': 'Alta',
46          'interoperability': 'Moderada'
47      },
48      {
49          'name': 'Arquitectura Cliente-Servidor',
50          'complexity': 'Moderada',
51          'scalability': 'Alta',
52          'teamExperience': 'Moderada',
53          'dataVolume': 'Alto',
54          'teamSize': 'Moderado',
55          'availability': 'Moderada',
56          'maintainability': 'Moderada',
57          'interoperability': 'Moderada'
58      },
59      {
60          'name': 'Arquitectura en la Nube',
61          'complexity': 'Alta',
62          'scalability': 'Excelente',
63          'teamExperience': 'Alta',
64          'dataVolume': 'Alto',
65          'teamSize': 'Alto',
66          'availability': 'Excelente',
67          'maintainability': 'Excelente',
68          'interoperability': 'Excelente'
69      },
70      {
71          'name': 'Arquitectura Basada en Eventos (EDA)',
72          'complexity': 'Alta',
73          'scalability': 'Alta',
74          'teamExperience': 'Alta',
75          'dataVolume': 'Excelente',
76          'teamSize': 'Moderado',
77          'availability': 'Alta',
78          'maintainability': 'Moderada',
79          'interoperability': 'Excelente'
80      }
81  ]
82  
83  # Mapeo de valores (escala de 1-5) para comparar respuestas del usuario
84  VALUE_MAP = {
85      'Baja': 1,
86      'Pequeño': 2,
87      'Moderado': 3,
88      'Moderada': 3,
89      'Alta': 4,
90      'Grande': 4,
91      'Alto': 4,
92      'Excelente': 5
93  }
```

### 3.2 Explicación línea por línea

#### Líneas 3-81: `architectures`
- **L3**: define una lista.
- **L4-L80**: cada elemento es un diccionario que describe una arquitectura.
- Cada arquitectura tiene:
  - `name`: nombre humano.
  - parámetros: `complexity`, `scalability`, etc.

**Idea clave**: esto es un “catálogo” estático. No hay base de datos; está hardcodeado.

#### Líneas 83-93: `VALUE_MAP`
Convierte palabras a números para poder medir “distancia”:
- “Baja” → 1
- “Excelente” → 5

Así el algoritmo puede hacer restas como `abs(user_score - arch_score)`.

---

## 4) Archivo 2: engine.py (algoritmo de scoring)

### 4.1 Código (con números de línea)

```python
 1  # server/recommendation_engine/engine.py
 2  
 3  from .architecture_data import architectures, VALUE_MAP
 4  
 5  def get_recommendation(user_answers):
 6      """
 7      Calcula la recomendación de arquitectura basada en los parámetros inferidos del usuario.
 8      Retorna las 3 mejores arquitecturas ordenadas por puntuación.
 9      """
10      scored_architectures = []
11      
12      for arch in architectures:
13          score = 0
14          for parameter, user_answer in user_answers.items():
15              arch_value = arch.get(parameter)
16              user_score = VALUE_MAP.get(user_answer)
17              arch_score = VALUE_MAP.get(arch_value)
18              
19              if user_score and arch_score:
20                  difference = abs(user_score - arch_score)
21                  if difference == 0:
22                      score += 2
23                  elif difference == 1:
24                      score += 1
25          
26          scored_architectures.append({**arch, 'score': score})
27      
28      scored_architectures.sort(key=lambda x: x['score'], reverse=True)
29      return scored_architectures[:3]
```

### 4.2 Explicación línea por línea

#### Línea 3: import
- Importa el catálogo (`architectures`) y el mapa (`VALUE_MAP`) desde el otro archivo.

#### Líneas 5-10: función y estructura de salida
- **L5**: define la función.
- **L10**: crea una lista vacía donde se guardarán arquitecturas con su `score`.

#### Líneas 12-27: cálculo de puntajes
- **L12**: recorre cada arquitectura del catálogo.
- **L13**: inicializa `score` para esa arquitectura.

- **L14**: recorre cada par `(parameter, user_answer)` del usuario.
  - `parameter` es la clave (ej. `"scalability"`).
  - `user_answer` es el valor (ej. `"Alta"`).

- **L15**: `arch.get(parameter)` obtiene el valor de ese parámetro en la arquitectura.
  - Si la arquitectura no tiene ese parámetro, devuelve `None`.

- **L16**: convierte la respuesta del usuario a número usando `VALUE_MAP`.
- **L17**: convierte el valor de la arquitectura a número usando `VALUE_MAP`.

- **L19**: valida que ambos scores existan.
  - Importante: en este proyecto `VALUE_MAP` usa 1-5, así que no hay 0.
  - Aun así, esta condición depende de “truthiness”: si algún día `VALUE_MAP` tuviera 0, esto fallaría.

- **L20**: calcula la diferencia absoluta.

- **L21-L24**: reglas de scoring:
  - diferencia 0 → +2 puntos (match exacto)
  - diferencia 1 → +1 punto (cercano)
  - diferencia >= 2 → +0 puntos

- **L26**: agrega la arquitectura a la lista con el campo extra `score`.
  - `{**arch, 'score': score}` copia todas las claves de `arch` y agrega `score`.

#### Líneas 28-29: ordenar y devolver
- **L28**: ordena por score de mayor a menor.
- **L29**: devuelve las primeras 3.

---

## 5) Ejemplo de cálculo (con números)

Supón:
- Usuario: `scalability = Excelente` → 5
- Arquitectura: `scalability = Alta` → 4

Entonces:
- `difference = abs(5 - 4) = 1` → suma +1

Si fuera:
- Usuario 5 vs Arquitectura 3 → difference 2 → suma +0

---

## 6) Dónde se usa este servicio

El orquestador lo llama en fase de recomendación:
- `recommendations = get_recommendation(state['inferredParams'])`

---

Si quieres, el próximo paso es documentar el endpoint HTTP que recibe mensajes del frontend y construye el `history` que termina llegando al orquestador.
