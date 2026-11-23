# Sistema de Normalización de Transacciones

## Descripción

Desarrollé un programa que lee transacciones en distintos formatos JSON, las convierte a una estructura común, valida sus datos y permite consultarlas desde una interfaz de línea de comandos.

## Estructura de archivos

- `main.py`: carga los archivos, coordina la normalización y validación, y muestra el menú de opciones.
- `normalizer.py`: detecta el formato de origen y convierte cada registro en una transacción normalizada.
- `validator.py`: valida las transacciones y conserva una interfaz compatible para métricas.
- `metrics.py`: calcula conteos y sumas.
- `configuration.py`: carga y valida la configuración de negocio.
- `skills/transactions.py`: expone las capacidades de normalización, validación y métricas.
- `agents/analyst.py`: coordina las skills y define los perfiles del agente.
- `agents/provider.py`: adaptador HTTP opcional para el modelo de lenguaje.
- `agent_cli.py`: ejecuta el agente desde la consola.
- `tests/test_agent.py`: verifica las reglas y el comportamiento del agente.
- `config.json`: contiene los mapeos de estados, los formatos de fecha y las monedas admitidas.
- `data.json`: contiene los registros de entrada.

## Cómo ejecutarlo

El proyecto requiere Python 3 y no utiliza librerías externas. Desde la carpeta del proyecto, ejecuto:

```bash
python3 main.py
```

## Agente de análisis y skills

El agente ejecuta tres skills reutilizables en `skills/transactions.py`: normalizar, validar y calcular métricas. Las reglas siguen siendo deterministas; `metrics.py` y `configuration.py` separan métricas y carga de configuración. El perfil `tecnico` incluye motivos y fuentes; `ejecutivo` presenta categorías agregadas. Ambos utilizan las mismas reglas.

Desde esta carpeta:

```bash
python3 agent_cli.py --perfil tecnico
python3 agent_cli.py --perfil ejecutivo --data data.json
python3 -m unittest discover -s tests -v
```

Opcionalmente, `--llm` solicita una explicación al endpoint HTTPS de Chat Completions configurado con las variables de entorno `AGENT_LLM_ENDPOINT`, `AGENT_LLM_API_KEY` y `AGENT_LLM_MODEL`. No se requiere proveedor para las métricas. Solo se envían categorías de error y conteos, no registros originales; la respuesta del modelo es orientativa y no modifica los resultados. Si falla, se conservan las categorías y se informa el fallo. No guardar credenciales en el repositorio.

La orquestación es un flujo fijo: el agente invoca las tres skills en orden y el modelo solo explica sus resultados, sin elegir herramientas. La separación de adaptadores por formato y una skill independiente para explicación quedan como mejoras futuras. No se ha verificado la integración contra un proveedor real.

## Explicación técnica de la refactorización

### Problema identificado

El proyecto original ya separaba normalización y validación, pero `main.py` reunía carga de archivos, coordinación y presentación. Además, `Validator` calculaba métricas y `Normalizer` concentraba la detección y transformación de los tres formatos. Esta organización dificultaba reutilizar el procesamiento desde otra interfaz y añadir comportamiento de agente sin mezclarlo con la consola.

### Responsabilidades actuales

La configuración de monedas, mapeos y fechas permanece en `config.json`; `configuration.py` comprueba su estructura antes de usarla. `normalizer.py` transforma los datos y `validator.py` aplica las reglas de validez. `metrics.py` recibe transacciones ya clasificadas y calcula los resultados, separando esa responsabilidad de la validación. La consola original continúa disponible mediante `main.py`.

Las skills de `skills/transactions.py` ofrecen funciones independientes de la interfaz: reciben datos y configuración, y devuelven resultados estructurados. `agents/analyst.py` las coordina sin depender de `input` o `print`; `agent_cli.py` se encarga de leer argumentos y mostrar el JSON. El adaptador de `agents/provider.py` encapsula la comunicación HTTP con el proveedor, de manera que puede sustituirse por un objeto simulado durante las pruebas.

### Contratos de las skills

| Skill | Entrada | Resultado |
|---|---|---|
| `normalizar_transacciones` | Lista de objetos JSON y configuración. | Pares de registro original y `Transaction` normalizada. Rechaza entradas que no sean una lista de objetos. |
| `validar_transacciones` | Pares normalizados y configuración. | Lista de transacciones válidas y lista de inválidas con original, transacción y motivos. |
| `calcular_metricas` | Listas de válidas e inválidas. | Totales de procesamiento, conteos por estado y sumas por moneda. Los conteos por estado y las sumas usan solo las válidas. |

El registro `SKILLS` asocia nombres con funciones. El agente comprueba que la skill solicitada figure en la lista del perfil; un nombre desconocido o no permitido produce un error. Las funciones también pueden utilizarse directamente desde Python, sin proveedor LLM.

### Personalización y flujo

`TransactionAgent` acepta una configuración, un perfil y un proveedor opcional. Los perfiles están definidos en código en `PROFILES`: `tecnico` muestra fuentes y motivos individuales, mientras que `ejecutivo` presenta categorías agregadas. Las instrucciones para la explicación también cambian con el perfil; los cálculos y las reglas de negocio son los mismos.

El flujo es: cargar configuración y datos → normalizar → validar → calcular métricas → generar categorías de rechazo → solicitar una explicación al proveedor si se habilitó y hay rechazos → mostrar el resultado. El modelo recibe solo categorías y conteos, no el JSON original. La respuesta generada se presenta como texto adicional y no altera las métricas ni la clasificación. Si el proveedor falla o responde vacío, se informa el fallo y se conservan los resultados deterministas.

### Objetivos alcanzados y límites

| Objetivo | Resultado |
|---|---|
| Identificar responsabilidades acopladas | Se identificaron la coordinación y presentación en `main.py`, las métricas en `Validator` y los formatos concentrados en `Normalizer`. |
| Separar lógica, configuración y comportamiento | Se extrajeron configuración y métricas y se agregó una capa de skills y agente. La consola original mantiene su propia coordinación y los formatos siguen juntos en `Normalizer`. |
| Crear capacidades reutilizables | Se implementaron tres skills deterministas con entradas y resultados definidos. |
| Integrar y personalizar un agente | El agente ejecuta las skills con dos perfiles y admite un proveedor de explicaciones intercambiable. El flujo es fijo, no hay selección autónoma de herramientas. |
| Usar IA de forma consciente | El modelo se limita a explicar categorías; los cálculos se mantienen en Python y se minimizan los datos enviados. La explicación puede contener errores y debe contrastarse con los resultados estructurados. |

El código original no incluía un flujo LLM en ejecución: se incorporó durante esta refactorización. Si la actividad exige estrictamente que el proyecto inicial ya lo tuviera, debe confirmarse su elegibilidad con el docente.

### Evidencia de validación

Las cuatro pruebas de `tests/test_agent.py` verifican los formatos de ejemplo, métricas, casos inválidos, perfiles, configuración, rechazo de skills desconocidas y fallos de un proveedor simulado. Para el `data.json` incluido, el agente devuelve 4 procesadas, 3 válidas y 1 inválida; las sumas de las válidas son USD 201.00 y EUR 99.99. Las pruebas usan un proveedor simulado y no acreditan una conexión real con un servicio LLM.

## Decisiones de diseño y uso de IA

Usé Claude como apoyo para escribir el código base, pero definí las reglas de negocio y ajusté el comportamiento durante las pruebas. En particular:

- Asigné la moneda `EUR` a los registros que incluyen el símbolo `€` y no tienen un campo de moneda explícito.
- Los estados que no aparecen en el mapeo se guardan en mayúsculas, por ejemplo, `PENDING`.
- Agregué una opción para mostrar los motivos exactos por los que se rechaza cada transacción.
- Decidí que una fecha que no se puede interpretar hace que la transacción sea inválida.
- El conteo por estado y las sumas por moneda se calculan solo con transacciones válidas, para que los montos inválidos no alteren los totales.
- Los filtros de estado y moneda muestran únicamente transacciones válidas.
- Conservé el JSON original junto al objeto normalizado para mostrarlo al consultar los registros inválidos.
