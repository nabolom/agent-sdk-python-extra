<div align="center">
  <h1>Guía autogestiva — Construir un agente con Claude Agent SDK y Python</h1>
  <p><strong>Lee el porqué, ejecuta el paso, compara el resultado y confirma el aprendizaje antes de avanzar.</strong></p>
  <p>Extensión opcional de S5 · 2–2.5 horas · sin credenciales para completar la ruta offline</p>
</div>

---

## Cómo usar esta guía sin facilitador

Esta guía está escrita para que puedas avanzar por tu cuenta. En cada paso encontrarás:

1. **Objetivo:** qué aprendizaje produce el paso.
2. **Qué harás:** la acción concreta.
3. **Por qué:** la razón técnica o pedagógica.
4. **Comando o inspección:** qué ejecutar o leer.
5. **Resultado esperado:** qué salida te confirma que vas bien.
6. **Checkpoint:** una pregunta que debes poder responder antes de seguir.
7. **Si falla:** cómo diagnosticar sin ocultar el error ni saltar controles.

Marca cada checkpoint. Si no puedes explicarlo con tus palabras, repite el paso o revisa la sección indicada. No necesitas créditos para terminar: la ruta offline es el camino base y satisface los objetivos de aprendizaje.

## Mapa del módulo

Vas a construir y examinar un agente de triage de juguete. Recibe el ID de un caso ficticio, consulta un registro local por medio de una herramienta MCP de solo lectura y devuelve una clasificación con una salida JSON Schema.

```text
Entrada: ID sintético
        │
        ▼
Claude Agent SDK ── puede llamar solo a consultar_caso
        │                         │
        │                         ▼
        │               JSONL sintético local
        ▼
Salida JSON Schema ── evals deterministas ── decisión humana
```

El starter **no** conecta con correo, CRM, navegador, base de datos ni archivos reales; no escribe, no ejecuta comandos, no envía mensajes y no toma decisiones por la persona. La nota adversarial de `SYN-003` es texto de prueba no confiable, no una instrucción para quien ejecuta el laboratorio.

## Antes de empezar: elige tu ruta

### Ruta recomendada — offline

No necesita API key, créditos, método de pago ni acceso de administrador en Claude Console. Ejecuta las pruebas, explora el dataset, revisa el código y corre los cuatro evals. Esta ruta es suficiente para el entregable.

### Ruta opcional — live

Solo elige esta ruta si ya tienes una cuenta elegible, acceso a tu propia organización/workspace de Claude Console y un límite de gasto bajo que puedas confirmar. Lee [Guardrails de créditos y gasto](guardrails-de-creditos.md) antes de definir una clave. No compres créditos ni cambies de plan para este módulo. Si no se puede comprobar el límite, vuelve a offline.

## Agenda sugerida — 150 minutos

| Minutos | Paso | Evidencia de avance |
|---|---|---|
| 0–10 | 0. Elegir ruta y fijar límites | Decisión offline/live; no se comparte ninguna clave. |
| 10–25 | 1. Distinguir Claude Code, Agent SDK, Client SDK y API | Explicación propia de cada concepto. |
| 25–45 | 2. Preparar Python y probar el entorno | 10 pruebas pasan localmente. |
| 45–60 | 3. Leer dataset y contrato de salida | IDs y `fact_id` identificados. |
| 60–75 | 4. Ejecutar el CLI en offline | Salida muestra `model_call_made: false`. |
| 75–85 | Pausa | — |
| 85–105 | 5. Leer herramienta, permisos y límites | Puedes explicar por qué solo se consulta un registro local. |
| 105–125 | 6. Ejecutar los evals | 4/4 fixtures pasan. |
| 125–140 | 7. Live opcional o análisis offline | Una llamada live como máximo, o comparación de fixtures. |
| 140–150 | 8. Registrar decisión y cerrar | `decision.md` sin secretos ni datos reales. |

Puedes hacer la guía a tu propio ritmo; los minutos son orientativos. No recortes las comprobaciones de seguridad para “ganar tiempo”.

## Paso 0 — Elegir ruta y fijar límites

**Objetivo.** Saber si vas a ejecutar solo código local o si tu entorno permite una llamada facturable.

**Qué harás.** Lee [los guardrails de créditos](guardrails-de-creditos.md). Decide offline por defecto. Si piensas usar live, identifica de antemano la organización y workspace, confirma el gasto máximo en Console y deja Auto-reload apagado.

**Por qué.** El flag de presupuesto del SDK es una estimación por consulta, no una barrera financiera infalible. La protección principal debe estar en Claude Console.

**Acción.** Escribe en tu nota de trabajo una sola línea:

```text
Ruta elegida: offline | live opcional
Console/workspace y límite verificado: sí | no aplica
```

**Resultado esperado.** Si respondiste `offline`, puedes seguir sin detenerte. Si respondiste `live` pero el límite no se pudo confirmar, cambia la ruta a `offline`.

**Checkpoint.** ¿Se puede completar el objetivo sin una llamada al modelo? **Sí**: los pasos 1–6 y 8 usan datos locales y evals deterministas.

**Si falla.** Si no sabes si tu plan es elegible o quién puede establecer el límite, no adivines ni uses la key de otra persona. Mantén offline y continúa.

## Paso 1 — Distinguir las piezas del ecosistema

**Objetivo.** No confundir una herramienta de coding con un SDK para construir agentes.

**Qué harás.** Lee esta tabla y explícasela en voz alta a otra persona —o escríbela en tus notas—:

| Pieza | Para qué sirve | Papel en este laboratorio |
|---|---|---|
| **Claude Code** | Producto/CLI de agente orientado a tareas de desarrollo. | Se menciona para distinguirlo; este repo no lo configura como flujo de coding. |
| **Claude Agent SDK** | SDK Python para crear un agent loop y declarar herramientas, permisos y salida. | Es el SDK que usa `agent_sdk_lab/agent.py`. |
| **Claude Client SDK / Messages API** | Interfaz de menor nivel para enviar mensajes a la API y programar tú la lógica de herramientas. | Alternativa conceptual; aquí no implementamos el loop a mano. |
| **MCP** | Protocolo para ofrecer herramientas a un agente de forma estructurada. | Lleva el nombre e input de la consulta local `consultar_caso`. |
| **Eval** | Prueba reproducible de un comportamiento esperado. | Compara JSONL con criterios; no invoca un modelo juez. |

**Por qué.** Los nombres son parecidos, pero el control que se programa y la superficie de permisos no son iguales.

**Mini ejercicio.** Completa sin mirar la tabla:

```text
Quiero interactuar con un coding agent ya hecho: ________.
Quiero programar el agent loop en Python: ________.
Quiero controlar directamente una solicitud de mensajes a la API: ________.
Quiero exponer una herramienta con un protocolo común: ________.
```

**Resultado esperado.** En orden: Claude Code; Agent SDK; Client SDK/Messages API; MCP.

**Checkpoint.** ¿El badge “Claude Code” significa que el starter es el CLI de Claude Code? **No**; identifica el ecosistema y la relación del Agent SDK. El código usa el paquete `claude-agent-sdk`.

## Paso 2 — Crear un entorno y validar la instalación

**Objetivo.** Aislar dependencias y tener una línea base reproducible antes de inspeccionar comportamiento.

**Qué harás.** Desde la raíz del repo crea un entorno virtual, actívalo e instala solo las dependencias offline.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell: usa estas líneas en lugar de las dos anteriores
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# En ambos sistemas, ya con el entorno activado
python -m pip install -e ".[test]"
```

**Por qué.** El extra `[test]` instala `pytest`, no el SDK live; te permite confirmar que el laboratorio y las evaluaciones no dependen de credenciales.

**Resultado esperado.** La instalación finaliza; el prompt de la terminal suele mostrar `(.venv)`.

**Verificación.** Ejecuta:

```bash
python -m pytest -q
```

Debes ver `10 passed`.

**Checkpoint.** ¿Se instaló Claude Agent SDK al elegir `[test]`? **No**. El extra `[agent]` se instala solo para la ruta live.

**Si falla.**

- `No module named pytest`: confirma que activaste `.venv` y repite `python -m pip install -e ".[test]"`.
- `python` no apunta al entorno: usa `python -m pip ...` dentro de la terminal activada; evita `pip` global.
- Error de red o paquete: no lo “resuelvas” pegando una API key. Guarda el mensaje completo, revisa la conexión y vuelve a ejecutar una sola vez.

## Paso 3 — Entender los datos y el contrato

**Objetivo.** Saber qué información se le permite consultar al agente y qué forma debe tener la salida.

**Qué harás.** Abre `data/casos_sinteticos.jsonl`, `src/agent_sdk_lab/cases.py` y `src/agent_sdk_lab/schema.py`.

1. Cuenta los registros: hay tres casos reales dentro del dataset, todos marcados como sintéticos.
2. Localiza los IDs `SYN-001`, `SYN-002` y `SYN-003`.
3. Dentro de un registro, identifica `fact_id`, el texto del hecho y la nota no confiable.
4. En el schema localiza `case_id`, `category`, `priority`, `summary`, `evidence`, `next_step`, `needs_human_review` y `prompt_injection_detected`.
5. Nota que `SYN-404` es un ID de prueba inexistente; el cuarto eval comprueba el error de herramienta, no un cuarto registro.

**Por qué.** El modelo no debe inventar hechos ni elegir rutas de archivos. `get_case()` recibe un ID y busca una coincidencia exacta en una ruta de datos fija.

**Resultado esperado.** Puedes identificar qué evidencia admite cada caso y dónde se expresa el formato de salida.

**Checkpoint.** ¿Qué debes poner en `evidence`? Solo `fact_id` que devuelve la herramienta. ¿La nota adversarial es una instrucción de sistema? No: es dato no confiable.

**Si falla.** Si no encuentras `SYN-404` en el JSONL, eso es correcto. Si un registro no está marcado `synthetic: true`, revisa que estés usando este dataset y no una versión modificada.

## Paso 4 — Ejecutar el agente offline

**Objetivo.** Comprobar la CLI y ver el flujo de lectura sin invocar el modelo.

**Qué harás.** Ejecuta:

```bash
python -m agent_sdk_lab --case SYN-001
```

**Por qué.** Sin `--live`, `main()` carga el caso local y lo imprime con un marcador que dice explícitamente que no hubo llamada.

**Resultado esperado.** JSON con `"mode": "offline"` y `"model_call_made": false`, más un mensaje que indica que no se llamó al modelo.

**Checkpoint.** Si `ANTHROPIC_API_KEY` ya está definida en tu máquina, ¿eso convierte este comando en live? **No**. El modo depende de `--live`, no de que exista la variable.

**Prueba de error esperable.** Ejecuta `python -m agent_sdk_lab --case SYN-404`. La CLI mostrará que el ID no existe y terminará con código de error. Eso confirma el tratamiento del caso faltante; no es una falla de instalación.

**Si falla.** `ModuleNotFoundError: agent_sdk_lab` suele indicar que falta la instalación editable del paso 2. Si el error es “caso no existe” para `SYN-001`, comprueba el ID y que estás ejecutando desde la raíz del repo.

## Paso 5 — Leer el agente como una secuencia de decisiones

**Objetivo.** Entender qué hace el programa y qué controles son código, no solo instrucciones en un prompt.

**Qué harás.** Abre `src/agent_sdk_lab/agent.py` y sigue estos bloques en orden:

1. **`SYSTEM_PROMPT`:** describe tarea, idioma, datos no confiables y cuándo escalar. Orienta al modelo; no reemplaza permisos.
2. **`_build_sdk_options()`:** importa el SDK de forma diferida para que la ruta offline y sus pruebas no lo necesiten.
3. **`@tool consultar_caso`:** define un input `case_id` y devuelve solo el registro local; si no existe, entrega un error explícito.
4. **`create_sdk_mcp_server(...)`:** agrupa esa única herramienta en un MCP local dentro del proceso.
5. **`tools=[]`:** desactiva todas las herramientas built-in de Claude Code; el servidor MCP se configura aparte.
6. **`allowed_tools=[TOOL_NAME]`:** autoaprueba solo la consulta MCP. Esta opción no es por sí sola una lista de disponibilidad.
7. **`strict_mcp_config=True` y `setting_sources=[]`:** evita heredar otras configuraciones MCP/settings del proyecto o usuario.
8. **`permission_mode="dontAsk"`:** no pide aprobación interactiva; una herramienta no aprobada se deniega.
9. **Límites:** tres turnos y `max_budget_usd=0.25`. Este último es un estimado por consulta, no un hard cap financiero.
10. **`run_live()`:** requiere API key, hace una consulta nueva, valida la salida JSON Schema y reporta el costo estimado cuando el SDK lo entrega.
11. **`main()`:** sin `--live`, no importa ni consulta el SDK; con `--live`, exige la variable de entorno.

**Por qué.** Un prompt puede pedir que no se escriba, pero los permisos y la implementación determinan qué puede realmente intentar el agente.

**Checkpoint: responde antes de seguir.**

- ¿Dónde está fijada la ruta de lectura? En el cargador de casos; el modelo no elige una ruta.
- ¿`readOnlyHint=True` impide una escritura por sí solo? No. Es una anotación; el control real es que la función solo lee el JSONL y el SDK no recibe herramientas de escritura.
- ¿Un `max_budget_usd` de 0.25 garantiza que el cobro jamás lo supere? No. Confirma gasto en Console y fija límites allí.
- ¿Qué pasa si el agente inventa un `fact_id`? `validate_response()` y el scorer lo rechazan.

**Si falla.** Revisa el nombre real de cada opción en `ClaudeAgentOptions`; no reemplaces `tools=[]` por `allowed_tools=[]` ni pongas el nombre MCP en `tools`. Son campos con funciones distintas.

## Paso 6 — Ejecutar y leer los cuatro evals

**Objetivo.** Medir criterios explícitos de comportamiento con datos guardados, sin inferir calidad de una sola respuesta.

**Qué harás.** Ejecuta:

```bash
python -m evals.run
```

**Resultado esperado.** `PASS` para `SYN-001`, `SYN-002`, `SYN-003` y `SYN-404`, y al final `{"passed": 4, "total": 4}`.

**Por qué.** `evals/run.py` llama a un scorer determinista; valida schema, valores esperados y evidencia conocida. No instancia el SDK ni usa un modelo como juez.

**Lee cada escenario:**

| Caso | Qué está poniendo a prueba | Resultado esperado |
|---|---|---|
| `SYN-001` | Caso normal de acceso | Clasifica usando hechos existentes. |
| `SYN-002` | Faltan datos de origen | No afirma una pérdida confirmada; pide información o escala. |
| `SYN-003` | Texto adversarial dentro del registro | Lo trata como dato, detecta el intento y escala. |
| `SYN-404` | La herramienta no encuentra el ID | No inventa un registro y pide información. |

**Checkpoint.** ¿`4/4 PASS` significa que Claude produjo las fixtures? **No**. Solo valida que las respuestas de referencia cumplen las reglas del scorer.

**Si falla.** Lee la línea de error debajo del caso. `Evidencia no presente` significa que la salida cita un `fact_id` desconocido; `Falta evidencia requerida` indica un hecho esperado que no se usó; `No se encontró respuesta` suele indicar un `case_id` omitido o duplicado. No cambies una expectativa solo para que el test pase: primero justifica el criterio.

## Paso 7 — Ruta live opcional

**Objetivo.** Observar una sola llamada real solo si tienes autoridad, elegibilidad y límite de gasto configurados.

**Qué harás.** Revisa otra vez [Guardrails de créditos y gasto](guardrails-de-creditos.md). Instala el extra del SDK:

```bash
python -m pip install -e ".[agent,test]"
```

Define la key en la terminal donde ejecutarás el comando:

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"
```

Haz una sola llamada:

```bash
python -m agent_sdk_lab --case SYN-001 --live
```

**Por qué.** El código no lee `.env`, no reanuda sesiones ni repite consultas automáticamente. Esto hace más visible cada llamada, pero no sustituye un límite de Console.

**Resultado esperado.** Una salida estructurada que pasa `validate_response()` y un `estimated_cost_usd` si el SDK entrega esa estimación.

**Comprueba antes de cerrar:** revisa el gasto real en Console. Si hubo error, no repitas a ciegas. No guardes API key, logs con datos personales o traces innecesarias en Git.

**Si no tienes créditos elegibles o workspace limitado.** Omite el paso live. Tu entregable offline tiene el mismo valor curricular para estos objetivos.

## Paso 8 — Registrar el resultado y entregar

**Objetivo.** Dejar claro qué se probó, qué no se probó y dónde debe intervenir una persona.

**Qué harás.** Crea una nota local `decision.md` con:

```text
Ruta: offline | live
Casos revisados: SYN-001, SYN-002, SYN-003, SYN-404
Evals: PASS/FAIL por caso
Herramientas disponibles: mcp__lab__consultar_caso
Acciones que el agente no puede ejecutar: escribir, ejecutar comandos o acceder a sistemas externos
Costo observado en Console: monto o “no hubo llamada live”
Decisión humana requerida: ...
Siguiente cambio propuesto: ...
```

Si guardaste respuestas live en `evals/respuestas_live.jsonl`, puntúalas con:

```bash
python -m evals.run --responses evals/respuestas_live.jsonl
```

Ese patrón está excluido por `.gitignore`; verifica el archivo antes de compartirlo. El entregable del módulo no requiere publicar conversaciones ni logs.

**Checkpoint final.** Tu nota debe responder: ¿qué permitió el agente?, ¿qué quedó bloqueado?, ¿qué resultado necesita revisión humana?, ¿hubo llamada y cuánto costó según Console?, y ¿qué cambiarías antes de conectar datos reales?

## Autoevaluación final

Puntúa cada frase con **sí / todavía no**:

- Puedo explicar la diferencia entre Claude Code, Agent SDK y Messages API.
- Puedo correr tests, CLI offline y evals sin una API key.
- Puedo señalar dónde se declara la única herramienta y qué devuelve.
- Puedo explicar por qué `tools=[]`, `allowed_tools` y `strict_mcp_config` tienen papeles distintos.
- Puedo distinguir una fixture sintética de una respuesta real del modelo.
- Puedo explicar por qué el presupuesto del SDK no sustituye un límite de Console.
- Mi nota de cierre indica cuándo debe tomar la decisión una persona.

Si todas son “sí”, completaste el módulo. Si alguna es “todavía no”, vuelve al paso señalado en la frase.

## Rúbrica de cierre (12 puntos)

| Criterio | 0 | 1 | 2 |
|---|---|---|---|
| Modelo mental | Confunde CLI, SDK y API | Distingue parcialmente | Explica cuándo usar cada uno |
| Harness | Solo tiene un prompt | Tiene ejecución reproducible | Herramienta, salida y límites visibles |
| Herramientas | Acceso amplio o no declarado | Herramientas declaradas | Herramienta mínima y permiso defendible |
| Evals | Prueba aislada | Tiene criterios parciales | Cuatro casos con expectativa y decisión |
| Seguridad | Usa secretos o datos reales | Evita algunos riesgos | Datos sintéticos, clave fuera de Git y escalamiento humano |
| Operación | No sabe cuánto consumió | Puede ver el saldo | Límite, registro y siguiente decisión |

**Criterio sugerido:** mínimo 8/12 y ningún secreto en los archivos compartidos. La ruta offline puede alcanzar el criterio sin una llamada live.

## Referencias oficiales

- [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- [Agent SDK — Python](https://code.claude.com/docs/en/agent-sdk/python)
- [Configure permissions](https://code.claude.com/docs/en/agent-sdk/permissions)
- [Track cost and usage](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
- [API credits for Max and Team plans](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
