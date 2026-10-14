# Guardrails de créditos y gasto

**Verificación documental: 14 de octubre de 2026.** Los saldos promocionales y las reglas de elegibilidad pueden cambiar; antes de un laboratorio real, vuelve a revisar la documentación y los valores que muestra Claude Console.[1]

## Qué cubren los créditos

Los créditos promocionales no son un beneficio universal de “100 USD para cada participante”. La documentación vigente indica:[1]

- **Max 5x:** 100 USD por ciclo de facturación.
- **Max 20x:** 200 USD por ciclo.
- **Team:** 20 USD por asiento Standard y 100 USD por asiento Premium; todos los asientos comparten un saldo mensual con tope de 500 USD.
- **Free, Pro y Enterprise:** no son elegibles según la página vigente.
- El plan debe estar activo y en buen estado. Una persona nueva puede reclamar el beneficio después de siete días.
- Para reclamarlo se requiere el rol adecuado: el suscriptor Max o un Primary Owner/Owner de Team, y un rol Owner/Admin/Billing en Claude Console.
- Una organización de Console vinculada recibe los créditos por ciclo de facturación —mensualmente en planes anuales—; vencen al final del ciclo y no se acumulan.
- Cubren Claude API, Managed Agents, Claude Agent SDK y Playground. No cubren Claude Code interactivo, uso extra en las apps de Claude ni otros proveedores cloud.
- No necesitas añadir un método de pago de Claude Platform para reclamar estos créditos.

El vínculo importa: cada plan se puede asociar a una sola organización Console y la persona no puede cambiarla por sí misma. Antes de aceptar el vínculo, asegúrate de elegir la organización que vas a usar para desarrollar.[1]

## Límite de gasto: dos capas

**1. Límite de Console — protección principal.** Si tienes permisos de administrador, crea un workspace dedicado para el laboratorio y configura allí un límite de gasto bajo. Como recomendación pedagógica, comienza con **5–10 USD por laboratorio**, no con el saldo total disponible. Ese rango es una decisión del curso, no una regla de Anthropic.[1] [2]

El workspace `Default` no admite límites propios; una persona administradora debe crear otro workspace para configurar el límite. Si no tienes ese permiso o no puedes fijarlo, trabaja offline o sigue la demostración del facilitador.[2]

**2. Límite del código — protección auxiliar.** El starter usa una sola llamada nueva, `max_turns=3` y `max_budget_usd=0.25`. El presupuesto del SDK es una **estimación local** que puede rebasarse. Solo cubre la consulta actual; al reanudar una sesión o reiniciar el contexto puede reiniciarse el cómputo. Por eso el código no reanuda sesiones ni repite llamadas automáticamente. Confirma siempre el gasto real y el saldo en Console.[3]

## Lista de verificación antes de `--live`

1. Revisa si tu plan y cuenta son elegibles y si el saldo está disponible.
2. Vincula la organización de Claude Console correcta; revisa los roles y acepta los términos desde Settings > Billing de claude.ai.
3. Comprueba la fecha de expiración del saldo en **Settings > Billing > Promotional credits** de Console.
4. Usa una organización propia y, si está disponible, un workspace exclusivo del laboratorio con límite bajo.
5. Deja **Auto-reload apagado**. La recarga automática se activa por el saldo comprado y puede recargar incluso si aún hay créditos promocionales disponibles.[1]
6. Define `ANTHROPIC_API_KEY` solo en la terminal de tu entorno virtual. No la pegues en un archivo, notebook, issue, chat o commit.
7. Ejecuta primero `python -m pytest` y `python -m evals.run`; ambos son offline.
8. Usa datos de `data/casos_sinteticos.jsonl` exclusivamente. No conectes correo, CRM, navegador, base de datos ni archivos reales.
9. Haz como máximo una ejecución live por invocación y verifica el gasto en Console antes de repetir.

Cada API key y workspace de la organización vinculada consume del mismo saldo promocional; separar un workspace establece un límite de gasto, pero **no crea un saldo promocional independiente**.[1]

## Si no tienes créditos elegibles

No compres créditos, no cambies de plan y no uses una key del facilitador. Puedes participar con cualquiera de estas rutas:

- correr el dataset y los evals offline;
- revisar las respuestas de referencia, que son fixtures didácticos y no salidas reales de Claude;
- observar una única demostración live del facilitador;
- diseñar criterios, permisos y handoff sin ejecutar una llamada.

Si una organización agota sus créditos y no tiene otros créditos, las solicitudes API se detienen hasta el siguiente ciclo; no se cargan al plan de Claude.[1] El laboratorio no requiere habilitar compras ni recarga automática.

## Fuentes

[1]: https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers "API credits for Max and Team plans"
[2]: https://platform.claude.com/docs/en/manage-claude/workspaces "Workspaces"
[3]: https://code.claude.com/docs/en/agent-sdk/cost-tracking "Track cost and usage"
