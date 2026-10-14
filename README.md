<div align="center">
  <h1>Extra final: construye un agente con Claude Agent SDK y Python</h1>
  <p><strong>De operar un agente a diseñar su entorno, herramientas, permisos y evaluaciones.</strong></p>
  <p>
    <a href="https://github.com/nabolom/agent-sdk-python-extra/actions/workflows/ci.yml"><img src="https://github.com/nabolom/agent-sdk-python-extra/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI offline: Python 3.10, 3.11 y 3.12"></a>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10 o posterior">
    <img src="https://img.shields.io/badge/Claude_Code-Agent_SDK-D97757" alt="Claude Code Agent SDK">
    <img src="https://img.shields.io/badge/Claude_API-opt--in-4B5563" alt="Claude API opcional">
    <img src="https://img.shields.io/badge/MCP-1_local_read--only-00897B" alt="Una herramienta MCP local de solo lectura">
    <img src="https://img.shields.io/badge/Evals-4_offline-6C5CE7" alt="Cuatro evaluaciones offline">
    <img src="https://img.shields.io/badge/Data-synthetic-F2C94C" alt="Datos sintéticos">
  </p>
  <p><a href="#ruta-autoguiada">Comenzar</a> · <a href="docs/guia-del-modulo.md">Guía completa</a> · <a href="docs/guardrails-de-creditos.md">Guardrails de créditos</a></p>
  <p><strong>Topics:</strong> Python · Claude Code · Agent SDK · API · MCP · Evals · Synthetic Data · Education</p>
</div>

---

**Módulo opcional para la cohorte:** extensión de S5 después de S4; duración sugerida de 2–2.5 horas. El repo es independiente del repo maestro. Sigue los pasos en orden: cada uno explica qué harás, por qué, qué resultado esperar y cómo comprobarlo.

## Qué estás construyendo

Un agente pequeño de triage que recibe el identificador de un caso ficticio, consulta un registro local mediante una sola herramienta MCP de lectura y propone una clasificación estructurada. No envía mensajes, no cambia registros, no navega, no ejecuta comandos y no usa datos reales.

| Concepto | Qué significa aquí |
|---|---|
| **Claude Code** | Producto/CLI de coding agent; no es el código de este laboratorio. |
| **Claude Agent SDK** | SDK Python para construir un agent loop programático con herramientas y permisos. Es el foco del módulo. |
| **Claude API** | Servicio al que llega la ruta live; puede generar uso facturable en la organización de Console. |
| **MCP** | Protocolo de herramientas; aquí conecta el agente con una única consulta local. |
| **Evals** | Casos y reglas reproducibles para detectar salidas incorrectas sin llamar a un modelo juez. |

## Ruta autoguiada

> **Regla de seguridad:** puedes completar los pasos 1–6 sin API key ni créditos. El paso live es opcional; no compres créditos ni cambies de plan para este laboratorio. Si no puedes establecer un límite de gasto en Console, quédate en offline.

### Paso 1 — Preparar Python y el entorno

**Qué harás:** crear un entorno virtual aislado para que las dependencias del laboratorio no se mezclen con otros proyectos.

**Por qué:** el SDK y las herramientas de prueba pertenecen a este proyecto, no a la instalación global de Python.

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell (usa estos comandos en lugar de las dos líneas anteriores)
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Comprueba:** la terminal muestra `(.venv)` al principio de la línea. Si PowerShell bloquea la activación, sigue usando el Python del entorno directamente: `\.venv\Scripts\python.exe`.

### Paso 2 — Instalar solo lo necesario para trabajar offline

**Qué harás:** instalar el repo en modo editable y `pytest`. Esta opción no instala Claude Agent SDK ni hace llamadas a la API.

```bash
python -m pip install -e ".[test]"
```

**Resultado esperado:** la instalación termina con `Successfully installed`.

**Si falla:** confirma que `(.venv)` está activo y vuelve a ejecutar el comando con el Python del entorno: `python -m pip install -e ".[test]"`. No uses `sudo` ni instales paquetes globales.

### Paso 3 — Comprobar el entorno antes de leer el agente

**Qué harás:** ejecutar las pruebas unitarias, que revisan el dataset, el contrato JSON, el modo offline y el scorer.

```bash
python -m pytest -q
```

**Resultado esperado:** diez pruebas aprobadas (`10 passed`).

**Comprueba:** si aparece `ModuleNotFoundError: pytest`, repite el paso 2. Si falla una prueba, lee el caso y su mensaje antes de editar código; el test señala qué supuesto no se cumple.

### Paso 4 — Ver un caso sin modelo

**Qué harás:** pedir al CLI que muestre `SYN-001`. Al no incluir `--live`, la aplicación solo lee el JSONL local.

```bash
python -m agent_sdk_lab --case SYN-001
```

**Resultado esperado:** JSON que incluye `"mode": "offline"` y `"model_call_made": false`.

**Comprueba:** el identificador está en `data/casos_sinteticos.jsonl`; los hechos tienen `fact_id` como `F1`. Prueba también `SYN-003` y localiza la nota adversarial. El caso `SYN-404` no existe: si lo pides en offline, el CLI debe decirlo y terminar con error; ese resultado es intencional.

### Paso 5 — Medir las respuestas de referencia

**Qué harás:** correr cuatro evaluaciones deterministas, una por cada escenario: normal, información faltante, prompt injection y caso inexistente.

```bash
python -m evals.run
```

**Resultado esperado:** cuatro líneas `PASS` y un resumen `{"passed": 4, "total": 4}`.

**Qué demuestra y qué no:** demuestra que el scorer interpreta correctamente las fixtures preparadas; no demuestra que Claude haya producido esas respuestas ni que el modelo tenga calidad de producción. Lee [la guía de evals](docs/evals.md) antes de cambiar expectativas.

### Paso 6 — Entender las decisiones de seguridad

**Qué harás:** sigue el código en `src/agent_sdk_lab/agent.py` desde `_build_sdk_options()` hasta `run_live()`.

**Por qué:** las instrucciones del prompt no sustituyen controles técnicos. El starter usa `tools=[]` para desactivar built-ins, configura por separado un servidor MCP local, usa `strict_mcp_config=True` y `permission_mode="dontAsk"`, y permite solo la consulta declarada. El código de la herramienta únicamente devuelve un registro sintético.

**Comprueba que puedes explicar:** qué hace `allowed_tools`; por qué no es una lista de disponibilidad por sí sola; qué evita `SYN-003`; y por qué `ToolAnnotations(readOnlyHint=True)` es una indicación y no el control de seguridad que impide escrituras.

### Paso 7 — Ruta live, solo si ya tienes límites configurados

**Qué harás:** una invocación explícita de `--live` consulta el SDK. No es requisito para aprobar el laboratorio.

**Antes de seguir:** lee [Guardrails de créditos y gasto](docs/guardrails-de-creditos.md), verifica elegibilidad y saldo, usa un workspace de Console con un límite bajo y deja Auto-reload apagado. `max_budget_usd=0.25` es una estimación local por consulta, **no un límite financiero infalible**.

Instala el extra del SDK:

```bash
python -m pip install -e ".[agent,test]"
```

Define la variable solo en la terminal (el SDK no carga `.env` automáticamente):

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"
```

Haz una sola ejecución, sin reintentar automáticamente:

```bash
python -m agent_sdk_lab --case SYN-001 --live
```

**Resultado esperado:** respuesta JSON estructurada y, si el SDK reporta el dato, `estimated_cost_usd`. Confirma el costo real en Claude Console antes de cualquier otra llamada. Nunca pegues la clave en el repo, un notebook, un issue o un chat.

### Paso 8 — Cerrar el trabajo y dejar evidencia

**Qué harás:** guarda solo los resultados que necesitas, compara las cuatro salidas con las expectativas y completa un `decision.md`: capacidades permitidas, límites, resultados, costo observado en Console (si hubo llamada) y punto de escalamiento humano.

Para puntuar respuestas JSONL propias:

```bash
python -m evals.run --responses ruta/a/respuestas.jsonl
```

**Comprueba antes de compartir:** no hay API key, datos personales, trazas innecesarias ni respuestas live en Git. `evals/respuestas_demo.jsonl` son fixtures didácticas; no las presentes como resultados reales del modelo.

## Si algo no coincide

| Síntoma | Qué revisar primero |
|---|---|
| `pytest` no se encuentra | Activa `.venv` y repite la instalación `.[test]`. |
| El CLI dice que el caso no existe | Verifica el ID exacto; solo `SYN-001`, `SYN-002` y `SYN-003` están en el dataset. `SYN-404` representa un ID faltante. |
| Un eval falla por evidencia | Compara `evidence` con los `fact_id` del caso; no inventes un ID para hacer pasar el test. |
| `--live` indica que falta la key | Define `ANTHROPIC_API_KEY` en la misma terminal. No la guardes en `.env` ni en Git. |
| El SDK corta por presupuesto o devuelve error | No repitas a ciegas. Revisa el resultado y el uso real en Console; trabaja offline si no puedes confirmar el límite. |

## Referencias

- [Guía completa paso a paso](docs/guia-del-modulo.md)
- [Evaluaciones: formato, ejecución y lectura de resultados](docs/evals.md)
- [Guardrails de créditos y gasto](docs/guardrails-de-creditos.md)
- [Agent SDK Quickstart](https://code.claude.com/docs/en/agent-sdk/quickstart)
- [Agent SDK — Python](https://code.claude.com/docs/en/agent-sdk/python)

## Licencia

No se incluye un archivo de licencia. El repo es público, pero la visibilidad pública no concede por sí sola una licencia general de reutilización.
