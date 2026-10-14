# Extra final — De usar un agente a construir un agente

**Documento independiente adaptado para el laboratorio.** El módulo es opcional, se coloca después de S4 como extensión de S5 y no modifica el repo maestro del curso.

## Propósito y ubicación

El cierre no es “aprender otra librería”. Es aprender a diseñar el entorno donde un agente puede actuar: herramientas disponibles, permisos, datos, criterios de éxito, observabilidad y límites.

La progresión del curso se mantiene:

1. operar un agente dentro de un espacio de trabajo;
2. diseñar decisiones, contratos, evals y guardrails;
3. construir un agente pequeño dentro de una aplicación propia.

Claude Agent SDK resulta adecuado para esa transición porque deja construir programáticamente un agent loop con herramientas, permisos y sesiones desde Python.[1] El laboratorio no enseña a desplegar un sistema de producción.

## Prerrequisitos y resultados

Antes de tomar la ruta live, cada persona debería poder describir una tarea y su decisión, explicar el contrato de entrada/salida, redactar cuatro casos de evaluación, usar un entorno virtual de Python y mantener una API key fuera de Git.

Al terminar, la persona podrá:

- distinguir Claude Code, Agent SDK, Client SDK y Managed Agents;
- ejecutar una consulta nueva con `claude-agent-sdk`;
- exponer una herramienta determinista de lectura sin dar acceso a escribir o ejecutar comandos;
- probar casos normal, límite, adversarial y de error de herramienta;
- explicar qué hace el agente, qué puede usar y cuándo debe intervenir una persona;
- registrar resultados de evals y revisar el costo real en Console.

No se exige conocimiento previo de MCP, subagentes o sistemas multiagente.

## Proyecto: triage con un caso sintético

El agente recibe el ID de un caso ficticio. Una única herramienta local consulta ese ID en `data/casos_sinteticos.jsonl` y devuelve hechos etiquetados. El agente propone categoría, prioridad, resumen, IDs de evidencia y siguiente paso recomendado para una persona.

El starter no accede a correo, CRM, base de datos, navegador ni archivos reales. No envía nada, no edita casos y no ejecuta comandos. El dataset incluye una nota adversarial para enseñar que las instrucciones que aparecen dentro de los datos deben tratarse como contenido no confiable.

```text
Aprendedor(a)
   │ --case SYN-001 --live
   ▼
agent_sdk_lab/agent.py ── query() ── Claude Agent SDK
   │                                  │
   │                                  └─ solo mcp__lab__consultar_caso
   ▼
casos_sinteticos.jsonl ── salida JSON Schema ── evals
```

**Ajuste de seguridad del starter respecto al diseño conceptual inicial:** la guía original consideraba explorar `Read`, `Glob` y `Grep` de solo lectura. El repo no expone esas herramientas. Para que el primer ejemplo tenga una superficie acotada y reproducible, usa una sola herramienta MCP local de consulta por ID. En la API del SDK, `tools=[]` desactiva todas las herramientas built-in; el servidor MCP se configura por separado y `allowed_tools` permite autoaprobar solo la herramienta de consulta. `allowed_tools` por sí solo no restringe qué herramientas están disponibles. La configuración usa además `strict_mcp_config=True`, fuentes de settings vacías y `permission_mode="dontAsk"`.[2] [3]

La estructura de salida se valida con un JSON Schema. La consulta no reanuda sesiones, tiene un máximo de tres turnos y usa `max_budget_usd=0.25` como protección auxiliar. El costo que estima el SDK no es una factura autoritativa y puede superar ese límite; el límite de Console es la protección principal.[4]

## Agenda sugerida — 2.5 horas

| Minutos | Bloque | Evidencia |
|---|---|---|
| 0–15 | Elegibilidad, workspace y límites | La persona confirma su ruta live u offline; no comparte secretos. |
| 15–35 | Puente conceptual: CLI, Agent SDK, Client SDK y Managed Agents | Diagrama breve de cuándo usar cada alternativa. |
| 35–65 | Entorno virtual, instalación, contrato y primera ejecución offline | Tests y evals corren sin API key. |
| 65–75 | Pausa | — |
| 75–110 | Revisión del agente read-only, herramienta local y dataset | Se explica cada permiso y el contenido no confiable. |
| 110–135 | Cuatro evals; una llamada live opcional por caso | Resultado PASS/FAIL y evidencias identificables. |
| 135–150 | Debrief, costo y handoff | Registro de costo observado, límites y siguiente mejora. |

Para una sesión de dos horas, omite la pausa formal y deja la segunda ronda live como demostración. El trabajo offline y los cuatro criterios de evaluación se conservan.

## Recorrido del laboratorio

### 0. Preparar el espacio y decidir la ruta

Antes de cualquier llamada, lee [Guardrails de créditos y gasto](guardrails-de-creditos.md). Quien no tenga créditos elegibles o no pueda establecer un límite de gasto trabaja con el dataset y las fixtures, o observa la demostración del facilitador. No es necesario comprar créditos para cumplir el objetivo pedagógico.

### 1. Instalar y verificar en modo offline

Crea un entorno virtual e instala `.[test]`. Corre `python -m pytest`, `python -m evals.run` y `python -m agent_sdk_lab --case SYN-001`. El modo predeterminado no llama al modelo, incluso si la variable API key ya existe.

### 2. Entender el contrato antes del prompt

Revisa `OUTPUT_SCHEMA`: `case_id`, `category`, `priority`, `summary`, `evidence`, `next_step`, `needs_human_review` y `prompt_injection_detected`. El agente solo debe usar `fact_id` que regresó la herramienta; el scorer detecta IDs inventados.

### 3. Probar el manejo de fallas

Inspecciona los cuatro casos. En el caso inexistente, la herramienta devuelve un error explícito; el agente debe abstenerse de inventar. En el caso adversarial, detecta el intento de cambiar sus instrucciones, no lo obedece y escala a una persona.

### 4. Ejecutar una llamada live, si se autoriza

Solo después de fijar el límite de Console, ejecutar los evals offline y definir `ANTHROPIC_API_KEY`, usa `--live`. Cada invocación hace una consulta nueva; no hay bucle de reintentos ni escritura. Confirma el uso real en Console antes de volver a ejecutar.[4] [5]

### 5. Revisar resultados y registrar decisión

Para evaluar salidas live, guarda JSONL local excluido de Git y usa `python -m evals.run --responses ruta.jsonl`. Registra modelo, número de llamadas, herramientas declaradas, cuatro resultados, costo observado en Console y qué debe revisar una persona. No guardes API keys ni conversaciones innecesarias.

## Evals y criterio de éxito

La suite contiene:

- **Normal (`SYN-001`):** clasifica un fallo de acceso usando evidencia local.
- **Límite (`SYN-002`):** reconoce información faltante y no declara pérdida confirmada.
- **Adversarial (`SYN-003`):** trata la nota como dato no confiable, detecta la instrucción adversarial y escala.
- **Falla de herramienta (`SYN-404`):** no inventa cuando el ID no existe.

Cada caso fija expectativa, evidencia requerida y resultado observado. Las fixtures incluidas prueban el scorer, pero no sustituyen resultados live ni demuestran desempeño del modelo. Detalles en [`evals.md`](evals.md).

## Entregable de cada persona

Una carpeta pequeña, sin secretos:

```text
agent-sdk-lab/
├── README.md
├── resultado.jsonl              # sintético; respuesta revisable
├── evals-live.jsonl             # opcional y local, no commit si contiene trazas
└── decision.md                  # permisos, resultado y siguiente paso humano
```

`decision.md` responde: qué puede hacer el agente, qué se bloqueó, cuándo intervino una persona y qué cambiaría antes de una extensión. El registro final incluye el costo observado en Console cuando hubo llamada live.

## Rúbrica de cierre

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Modelo mental | Confunde CLI, SDK y API | Distingue parcialmente | Explica cuándo usar cada uno |
| Harness | Solo tiene un prompt | Tiene ejecución reproducible | Herramienta, salida y límites visibles |
| Herramientas | Acceso amplio o no declarado | Herramientas declaradas | Herramienta mínima y permiso defendible |
| Evals | Prueba aislada | Tiene casos, criterio parcial | Cuatro casos con expectativa y decisión |
| Seguridad | Usa secretos o datos reales | Evita algunos riesgos | Datos sintéticos, clave fuera de Git y escalamiento humano |
| Operación | No sabe cuánto consumió | Puede ver el saldo | Límite, registro y siguiente decisión |

**Salida sugerida:** mínimo 8/12 y ningún secreto en los archivos entregados. Quien no haga una llamada live puede cumplir si presenta evals offline, diseño de permisos y handoff bien razonado.

## Extensiones avanzadas

Solo después de que pasen los cuatro evals base:

- comparar `query()` con `ClaudeSDKClient` para conversación de varios turnos;
- añadir un hook que bloquee una herramienta concreta y probarlo;
- comparar el Agent SDK con el Client SDK directo;
- agregar un segundo agente solo si se demuestra mejora con evals;
- probar caching o batches cuando no se necesite respuesta inmediata.

No se empieza con subagentes, navegador, base de datos, correo ni MCP externo. El valor didáctico es hacer visible el loop mínimo y sus límites.

## Referencias

[1]: https://code.claude.com/docs/en/agent-sdk/overview "Agent SDK overview"
[2]: https://code.claude.com/docs/en/agent-sdk/python "Agent SDK reference — Python"
[3]: https://code.claude.com/docs/en/agent-sdk/permissions "Configure permissions"
[4]: https://code.claude.com/docs/en/agent-sdk/cost-tracking "Track cost and usage"
[5]: https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers "API credits for Max and Team plans"
