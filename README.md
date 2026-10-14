# Extra final — Agent SDK con Python

Laboratorio opcional para pasar de **operar un agente** a **diseñar el entorno donde puede actuar**. Está pensado como extensión de S5, después de S4, y no modifica el repo maestro del curso.

La ruta principal construye un agente pequeño de triage con Claude Agent SDK para Python, un dataset completamente sintético, una herramienta local de consulta de solo lectura y cuatro evaluaciones reproducibles. La sesión sugerida dura 2–2.5 horas. El código no realiza acciones externas ni incluye datos reales, API keys o créditos.

## Empezar sin API key

Se necesita Python 3.10 o posterior. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
```

Activa el entorno:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Instala solo las dependencias de prueba para explorar el dataset y correr los evals sin llamadas al modelo:

```bash
python -m pip install -e ".[test]"
python -m evals.run
python -m agent_sdk_lab --case SYN-001
```

El modo predeterminado es **offline**. No llama a Claude aunque haya una API key en el entorno. El comando muestra el caso sintético solicitado y explica cómo activar la ruta live.

## Ruta live opcional

Para instalar el SDK y sus dependencias:

```bash
python -m pip install -e ".[agent,test]"
```

Define `ANTHROPIC_API_KEY` en la terminal que ejecutará el laboratorio. Claude Agent SDK no carga archivos `.env` automáticamente.[1] No pegues la clave en el código, notebook, README, Git o mensajes.

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"

# Windows PowerShell
$env:ANTHROPIC_API_KEY="tu_clave_de_Claude_Console"
```

Antes de una llamada live, sigue [la guía de guardrails de créditos](docs/guardrails-de-creditos.md) y confirma un límite de gasto en Claude Console. Una llamada live se ejecuta solo con `--live`:

```bash
python -m agent_sdk_lab --case SYN-001 --live
```

El starter registra una sola herramienta MCP local. Configura `tools=[]` para deshabilitar todas las herramientas built-in, limita la configuración MCP a ese servidor, usa `permission_mode="dontAsk"`, permite únicamente la consulta local, limita a 3 turnos y fija `max_budget_usd=0.25` como freno auxiliar. **Ese valor es una estimación del SDK y puede rebasarse; no sustituye el límite de gasto de Console.** El límite de Console es la protección principal.[2] [3]

## Verificación

Los tests y evals no hacen llamadas live. La GitHub Action del repo ejecuta la suite y las fixtures offline en Python 3.10–3.12.

```bash
python -m pytest -q
python -m evals.run
```

Para evaluar salidas guardadas después de una demostración:

```bash
python -m evals.run --responses ruta/a/respuestas.jsonl
```

## Contenido

```text
.github/workflows/ci.yml           CI offline para PRs y pushes a main
data/casos_sinteticos.jsonl        Casos ficticios y locales
src/agent_sdk_lab/                 Starter Python del agente
evals/                             Criterios y respuestas de referencia offline
docs/guia-del-modulo.md            Diseño pedagógico, agenda y entregables
docs/evals.md                      Contrato de evaluación y ejecución
docs/guardrails-de-creditos.md     Créditos, gasto y fallback sin API
tests/                             Pruebas locales sin credenciales
```

Las respuestas incluidas en `evals/respuestas_demo.jsonl` son **fixtures didácticos**, no resultados de una llamada a Claude ni una afirmación sobre la calidad de un modelo.

## Licencia

No se incluye un archivo de licencia. La visibilidad pública de GitHub no equivale a conceder una licencia de reutilización; se conserva este criterio por consistencia con los repos públicos del curso.

## Referencias de operación

[1]: https://code.claude.com/docs/en/agent-sdk/quickstart "Agent SDK Quickstart"
[2]: https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers "API credits for Max and Team plans"
[3]: https://code.claude.com/docs/en/agent-sdk/cost-tracking "Track cost and usage"
