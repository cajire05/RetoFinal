# Auditoría de MFA con IA local

## Integrantes

- Cesar Jimenez — A00401283
- Esue Torres — A00401225

## Qué hace el proyecto

Este prototipo revisa si las cuentas de una organización cumplen su política de autenticación multifactor (MFA). Usa políticas ficticias y un inventario simulado para responder preguntas como «¿Cuántas cuentas activas tienen MFA desactivado?».

Python recupera la política aplicable mediante RAG y cuenta las cuentas sin MFA con una herramienta de solo lectura. El agente explica el hallazgo. Python incorpora la referencia del inventario desde el resultado de la herramienta y verifica la fuente de la política contra un registro de fuentes autorizadas. Si faltan datos para responder, el sistema declara evidencia insuficiente.

- **Un agente.** El analista redacta el hallazgo.
- **Dos agentes.** Un revisor contrasta el borrador del analista con la evidencia original.

## Cómo ejecutarlo

Necesitas Python 3 y Ollama. Con Ollama iniciado, ejecuta estos comandos desde la raíz del proyecto.

```bash
ollama pull qwen2.5:3b
python evaluar.py
```

## Resultados

La evaluación ejecutó los mismos seis casos en cada modo con `qwen2.5:3b`.

| Modo | Hallazgos exactos | Citas correctas antes → después | Respuestas aceptadas antes → después |
| --- | ---: | ---: | ---: |
| Un agente | 6/6 | 0/6 → 6/6 | 0/6 → 6/6 |
| Dos agentes | 6/6 | 0/6 → 6/6 | 0/6 → 6/6 |

Tras corregir la validación de fuentes, las **12 respuestas finales fueron aceptadas**. Ambos modos superaron el caso con el documento señuelo y declararon evidencia insuficiente para Recursos Humanos.

En estos seis casos, el segundo agente obtuvo la misma calidad final y añadió **11,444 segundos por caso** en promedio. En el caso C4, el validador descartó una revisión que contradecía el inventario y conservó el borrador correcto del analista.

### Ejemplo de respuesta

> El ámbito incumple la política de MFA. [POL-MFA-04]  
> Cuentas activas sin MFA: 1. [CSV-MFA]

[Ver resultados por caso, latencia, tokens y costo eléctrico estimado](docs/resultados.md)
